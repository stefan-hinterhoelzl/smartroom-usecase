from ast import And
from asyncio.log import logger
from datetime import datetime
import pytz
import uvicorn
import asyncio
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from session import db_Session,conn 
from databases import Database 
from schema import Room, Light, Light_Operation
from fastAPI_models import Room_Object, Update_RoomObject, Lights_Object, Light_Operation_Object
from typing import List
from sqlalchemy import and_
from publisher import publish_message

database = Database(settings.DATABASE_URL)

app = FastAPI(title=settings.PROJECT_NAME)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


cur = conn.cursor()



# room
@app.post("/Rooms",response_model=Room_Object, status_code = status.HTTP_201_CREATED)
async def add_Room(addRoom:Room_Object):
    db_classes = Room(room_id=addRoom.room_id,room_size=addRoom.room_size,room_name=addRoom.room_name)
    try:
        db_Session.add(db_classes)
        db_Session.flush()
        db_Session.commit()
    except Exception as ex:
        logger.error(f"{ex.__class__.__name__}: {ex}")
        db_Session.rollback()
   
    return addRoom
 
@app.get("/Rooms", response_model=List[Room_Object], status_code = status.HTTP_200_OK)
async def get_AllRoom_Details():
    """ query = 'SELECT * FROM room'
    cur.execute(query)
    for i in cur:
        print(i) """
    results=db_Session.query(Room).all()
    return results         

@app.get("/Room/{room_id}", response_model=List[Room_Object], status_code = status.HTTP_200_OK)
async def get_Specific_Room(room_id:str):
    specificRoomDetail=db_Session.query(Room).filter(Room.room_id==room_id).all()        
    return specificRoomDetail

@app.put("/Room/{room_id}",status_code = status.HTTP_200_OK)
async def update_RoomDetails(room_id:str,request:Update_RoomObject):
    updateRoomDetail=db_Session.query(Room).filter(Room.room_id==room_id)
    if not updateRoomDetail.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'Room with the id {room_id} is not available')
    updateRoomDetail.update({'room_size':request.room_size,'room_name':request.room_name})
    db_Session.commit()
    return {"code":"success","message":"updated room"}

@app.delete("/Room/{room_id}", status_code = status.HTTP_200_OK)
async def delete_Room(room_id:str):
    deleteRoom=db_Session.query(Room).filter(Room.room_id==room_id).one()
    if not deleteRoom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'Room with the room id {room_id} is not found')
    db_Session.delete(deleteRoom)
    db_Session.commit()
    return {"code":"success","message":f"deleted room with id {room_id}"} 
  

# lights
@app.post("/Room/{room_id}/Lights", response_model=Lights_Object, status_code=status.HTTP_201_CREATED)
async def add_light(room_id: str, addLight: Lights_Object):
    addLight=Light(room_id=room_id,light_id=addLight.light_id, name=addLight.name)
    try:
        db_Session.add(addLight)
        db_Session.flush()
        db_Session.commit()
    except Exception as ex:
        logger.error(f"{ex.__class__.__name__}: {ex}")
        db_Session.rollback()
    
    return addLight

@app.get("/Room/{room_id}/Lights", response_model=List[Lights_Object], status_code=status.HTTP_200_OK)
async def get_All_Lights(room_id: str):
    getAllLights=db_Session.query(Light).filter(Light.room_id==room_id).all()
    return getAllLights


#  lights operation

@app.post("/Room/{room_id}/Light/{light_id}/Activation", response_model=Light_Operation_Object, status_code=status.HTTP_200_OK)
async def activate_Light(room_id: str, light_id: str):
    
    try:
        last_operation: Light_Operation_Object = db_Session.query(Light_Operation).filter(Light_Operation.light_id==light_id, Light_Operation.room_id == room_id).order_by(Light_Operation.time.desc()).first()

        if last_operation == None:
            operation = Light_Operation(light_id = light_id, room_id = room_id, time = datetime.now(), turnon = False, color_x = 0.1, color_y = 0.1, brightness = 200)
        else:
            operation = Light_Operation(light_id = light_id, room_id = room_id, time = datetime.now(), turnon = not last_operation.turnon, color_x = last_operation.color_x, color_y = last_operation.color_y, brightness = last_operation.brightness)


        db_Session.add(operation)
        db_Session.flush()
        db_Session.commit()

        #Trigger the Action in Zigbee Network via the connector

        data = {}
        data["state"] = "TOGGLE"
        topic = f"zigbee2mqtt/{light_id}/set" 

        publish_message(topic, data)

    except Exception as ex:
        logger.error(f"{ex.__class__.__name__}: {ex}")
        db_Session.rollback()
        #TBA Better Error Responding Here (and in general lol)
        raise HTTPException(status_code=500,detail=f'Internal Server Error')

    return operation

@app.post("/Room/{room_id}/Light/{light_id}/ComplexSetting", response_model=Light_Operation_Object, status_code=status.HTTP_200_OK)
async def complex_setting_light(room_id: str, light_id: str, operation: Light_Operation_Object):

    try:
        operation = Light_Operation(light_id = light_id, room_id = room_id, time = datetime.now(), turnon = operation.turnon, color_x = operation.color_x, color_y = operation.color_y, brightness = operation.brightness)
        
        db_Session.add(operation)
        db_Session.flush()
        db_Session.commit()

        #Trigger the Action in Zigbee Network via the connector

        #Value Checking here

        data = {}
        data["state"] = "TOGGLE"
        if operation.turnon == True:
            data["state"] = "ON"
        else:
            data["state"] = "OFF"
        color = {}
        color["x"] = operation.color_x
        color["y"] = operation.color_y
        data["color"] = color
        data["brightness"] = operation.brightness

        topic = f"zigbee2mqtt/{light_id}/set" 
        
        publish_message(topic, data)

    except Exception as ex:
        logger.error(f"{ex.__class__.__name__}: {ex}")
        db_Session.rollback()
        #TBA Better Error Responding Here (and in general lol)
        raise HTTPException(status_code=500,detail=f'Internal Server Error')
    
    return operation



# @app.get("/Room/{room_id}/Light/{light_id}/", response_model=List[Lights_Object], status_code=status.HTTP_200_OK)
# async def get_Specific_Light(room_id: str,light_id: str):
#     getSpecificLight=db_Session.query(Light).filter(Light.room_id==room_id,Light.light_id==light_id).all()
#     return getSpecificLight

# @app.get("/Room{room_id}/Light{light_id}/isOn{timestamp}", response_model=Lights_Object, status_code=status.HTTP_200_OK)
# async def check_Light(room_id: str,light_id: str,time:datetime):
#     checkLight=db_Session.query(Light).filter(Light.room_id==room_id,Light.light_id==light_id,Light.time==time)
#     return checkLight      

# @app.put("/Room/{room_id}/Light/{light_id}", status_code=status.HTTP_200_OK)
# async def update_light(room_id: str,light_id:str,request: Light_Operation_Object):
#     updateLight=db_Session.query(Light).filter(Light.room_id==room_id,Light.light_id==light_id)
#     if not updateLight.first():
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'Light with the id {light_id} is not available in room {room_id}')
#     updateLight.update({'turnon':request.turnon,'time':request.time})
#     db_Session.commit()
#     return {"code":"success","message":"updated light settings"}
 
# @app.delete("/Room/{room_id}/Light/{light_id}", status_code=status.HTTP_200_OK)
# async def delete_light(room_id: str,light_id: str):
#     deleteLight=db_Session.query(Light).filter(Light.room_id==room_id,Light.light_id==light_id).one()
#     if not delete_light:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'Light with the id {light_id} is not available in room {room_id}') 
#     db_Session.delete(deleteLight)
#     db_Session.commit()
#     return {"code":"success","message":f"deleted light with id {light_id} from room {room_id}"} 
  
# # windows
# @app.post("/Room/Windows/", response_model=Windows_Object, status_code=status.HTTP_201_CREATED)
# async def create_Windows(addWindows: Windows_Object):
#     db_window=Window(room_id=addWindows.room_id,window_id=addWindows.window_id,isopen=addWindows.isopen,time=addWindows.time)
#     try:
#         db_Session.add(db_window)
#         db_Session.flush()
#         db_Session.commit()
#     except Exception as ex:
#         logger.error(f"{ex.__class__.__name__}: {ex}")
#         db_Session.rollback()
    
#     return addWindows

# @app.get("/Room/{room_id}/Windows/", response_model=List[Windows_Object], status_code=status.HTTP_200_OK)
# async def get_All_Windows(room_id: str):
#     get_AllWindow=db_Session.query(Window).filter(Window.room_id==room_id).all()
#     return get_AllWindow    

# @app.get("/Room/{room_id}/Windows/{window_id}/", response_model=List[Windows_Object], status_code=status.HTTP_200_OK)
# async def get_Specific_Window(room_id: str,window_id:str):
#     get_SpecificWindow=db_Session.query(Window).filter(Window.room_id==room_id,Window.window_id==window_id).all()
#     return get_SpecificWindow

# @app.put("/Room/{room_id}/Windows/{window_id}", status_code=status.HTTP_200_OK)
# async def update_window(room_id: str,window_id:str,request: Window_Operation_Object):
#     updateWindow=db_Session.query(Window).filter(Window.room_id==room_id,Window.window_id==window_id)
#     if not updateWindow.first():
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'Window with the id {window_id} is not available in room {room_id}')
#     updateWindow.update({'isopen':request.isopen,'time':request.time})
#     db_Session.commit()
#     return {"code":"success","message":"updated window settings"}

# @app.delete("/Room/{room_id}/Windows/{window_id}", status_code=status.HTTP_200_OK)
# async def delete_window(room_id: str,window_id: str):
#     deleteWindow=db_Session.query(Window).filter(Window.room_id==room_id,Window.window_id==window_id).one()
#     if not deleteWindow:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'Window with the id {window_id} is not available in room {room_id}')
#     db_Session.delete(deleteWindow)
#     db_Session.commit()
#     return {"code":"success","message":f"deleted window with id {window_id} from room {room_id}"} 
 
# #ventilators
# @app.post("/Room/Ventilators/", response_model=Ventilators_Object, status_code=status.HTTP_201_CREATED)
# async def create_Ventilators(addVentilators: Ventilators_Object):
#     db_ventilator = Ventilator(room_id=addVentilators.room_id,ventilator_id=addVentilators.ventilator_id,turnon=addVentilators.turnon,time=addVentilators.time)
#     try:
#         db_Session.add(db_ventilator)
#         db_Session.flush()
#         db_Session.commit()
#     except Exception as ex:
#         logger.error(f"{ex.__class__.__name__}: {ex}")
#         db_Session.rollback()
#     return addVentilators 

# @app.get("/Room/{room_id}/Ventilators/", response_model=List[Ventilators_Object], status_code=status.HTTP_200_OK)
# async def get_All_Ventilators(room_id:str):
#     getVentilators=db_Session.query(Ventilator).filter(Ventilator.room_id==room_id).all()
#     return getVentilators

# @app.get("/Room/{room_id}/Ventilators/{ventilator_id}/", response_model=List[Ventilators_Object], status_code=status.HTTP_200_OK)
# async def get_Specific_Ventilator(room_id:str,ventilator_id:str):
#     getSpecificVentilators=db_Session.query(Ventilator).filter(Ventilator.room_id==room_id,Ventilator.ventilator_id==ventilator_id).all()
#     return getSpecificVentilators

# @app.put("/Room/{room_id}/Ventilators/{ventilator_id}", status_code=status.HTTP_200_OK)
# async def update_ventilators(room_id:str,ventilator_id:str,request: Ventilator_Operation_Object):
#     updateVentilator=db_Session.query(Ventilator).filter(Ventilator.room_id==room_id,Ventilator.ventilator_id==ventilator_id)
#     if not updateVentilator.first():
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'Ventilator with the id {ventilator_id} is not available in room {room_id}')
#     updateVentilator.update({'turnon':request.turnon,'time':request.time})
#     db_Session.commit()
#     return {"code":"success","message":"updated ventilator settings"}

# @app.delete("/Room/{room_id}/Ventilators/{ventilator_id}", status_code=status.HTTP_200_OK)
# async def delete_ventilator(room_id: str,ventilator_id:str):
#     deleteVentilator=db_Session.query(Ventilator).filter(Ventilator.room_id==room_id,Ventilator.ventilator_id==ventilator_id).one()
#     if not deleteVentilator:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'Ventilator with the id {ventilator_id} is not available in room {room_id}')
#     db_Session.delete(deleteVentilator)
#     db_Session.commit()
#     return {"code":"success","message":f"deleted ventilator with id {ventilator_id} from room {room_id}"} 

# # doors
# @app.post("/Room/Doors/", response_model=Doors_Object, status_code=status.HTTP_201_CREATED)
# async def add_Doors(addDoors: Doors_Object):
#     db_doors = Door(room_id=addDoors.room_id,door_id=addDoors.door_id,door_lock=addDoors.door_lock,connectsdoor=addDoors.connectsdoor,time=addDoors.time)
#     try:
#         db_Session.add(db_doors)
#         db_Session.flush()
#         db_Session.commit()
#     except Exception as ex:
#         logger.error(f"{ex.__class__.__name__}: {ex}")
#         db_Session.rollback()
#     return addDoors

# @app.get("/Room/{room_id}/Doors/", response_model=List[Doors_Object], status_code=status.HTTP_200_OK)
# async def get_AllDoors(room_id:str):
#     getDoors=db_Session.query(Door).filter(Door.room_id==room_id).all()
#     return getDoors
# @app.get("/Room/{room_id}/Doors/{door_id}", response_model=List[Doors_Object], status_code=status.HTTP_200_OK)
# async def get_SpecificDoor(room_id:str,door_id:str):
#     getDoors=db_Session.query(Door).filter(Door.room_id==room_id,Door.door_id==door_id).all()
#     return getDoors

# @app.put("/Room/{room_id}/Doors/{door_id}", status_code=status.HTTP_200_OK)
# async def update_door(room_id:str,door_id:str,request: Door_Operation_Object):
#     updateDoor=db_Session.query(Door).filter(Door.room_id==room_id,Door.door_id==door_id)
#     if not updateDoor.first():
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'Door with the id {door_id} is not available in room {room_id}')
#     updateDoor.update({'door_lock':request.door_lock,'time':request.time})
#     db_Session.commit()
#     return {"code":"success","message":"updated door settings"}

# @app.delete("/Room/{room_id}/Doors/{door_id}",status_code=status.HTTP_200_OK)
# async def delete_door(room_id: str,door_id: str):
#    deleteDoor=db_Session.query(Door).filter(Door.door_id==door_id,Door.room_id==room_id).one()
#    if not deleteDoor:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'Door with the id {door_id} is not available in room {room_id}')
#    db_Session.delete(deleteDoor)
#    db_Session.commit()
#    return {"code":"success","message":f"deleted door with id {door_id} from room {room_id}"}

# # room_to_door_relation
# @app.post("/Room_to_Door_Relation/", response_model=Room_Door_Relation_Object, status_code=status.HTTP_201_CREATED)
# async def add_Room_Door_Relation(addRoomDoorRelation: Room_Door_Relation_Object):
#     db_room_door_relation = RoomToDoorRelations(room_id=addRoomDoorRelation.room_id,door_id=addRoomDoorRelation.door_id)
#     try:
#         db_Session.add(db_room_door_relation)
#         db_Session.flush()
#         db_Session.commit()
#     except Exception as ex:
#         logger.error(f"{ex.__class__.__name__}: {ex}")
#         db_Session.rollback()
#     return addRoomDoorRelation

# @app.get("/Room_to_Door_Relation/{room_id}/", response_model=List[Room_Door_Relation_Object], status_code=status.HTTP_200_OK)
# async def get_Room_Door_Relation(room_id:str):
#     getRoomDoorRelation=db_Session.query(RoomToDoorRelations).filter(RoomToDoorRelations.room_id==room_id).all()
#     return getRoomDoorRelation

# @app.delete("/Room_to_Door_Relation/{room_id}/{door_id}",status_code=status.HTTP_200_OK)
# async def delete_Room_Door_Relation(room_id: str,door_id:str):
#    deleteRoomDoorRelation=db_Session.query(RoomToDoorRelations).filter(and_(RoomToDoorRelations.room_id==room_id, RoomToDoorRelations.door_id==door_id)).one()
#    if not deleteRoomDoorRelation:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'Room with the id {room_id} is not available')
#    db_Session.delete(deleteRoomDoorRelation)
#    db_Session.commit()
#    return {"code":"success","message":f"deleted room to door relation with room id {room_id} and door id {door_id}"}

