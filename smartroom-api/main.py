from ast import And
import json
import os
from asyncio.log import logger
from datetime import datetime
import pytz
import uvicorn
import asyncio
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from session import db_Session, conn
from databases import Database
from schema import Room, Light, Light_Operation, Motion_Sensor, Motion_Sensor_Operation, Power_Plug, Power_Plug_Operation
from fastAPI_models import Room_Object, Update_RoomObject, Lights_Object, Light_Operation_Object, Light_Operation_Return_Object, Update_LightObject, Time_Query_Object, Light_Operation_Storing_Object, Motion_Sensor_Object, Motion_Sensor_Update_Object, Motion_Sensor_Operation_Object, Motion_Sensor_Storing_Object, Power_Plug_Object, Power_Plug_Update_Object, Power_Plug_Operation_Object, Power_Plug_Storing_Object
from typing import List
from sqlalchemy import and_, text
from publisher import publish_message
import subprocess

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

#create devices.json on first startup
if not os.path.exists('devices.json'):
    with open("devices.json", "w") as f:
        devices = {}
        json.dump(devices, f)



# Rooms

"""Creates a new room in the database and returns the room on success. Room_id needs to be unique"""
"""Example room object 
   {
    "room_id": 1,
    "room_size": 50,
    "room_name": "Living room"
    }"""
@app.post("/Rooms", response_model=Room_Object, status_code=status.HTTP_201_CREATED)
async def add_Room(addRoom: Room_Object):
    db_classes = Room(room_id=addRoom.room_id,
                      room_size=addRoom.room_size, room_name=addRoom.room_name)
    try:
        db_Session.add(db_classes)
        db_Session.flush()
        db_Session.commit()
    except Exception as ex:
        logger.error(f"{ex.__class__.__name__}: {ex}")
        db_Session.rollback()

    return addRoom

"""Returns all the rooms present in the database"""
@app.get("/Rooms", response_model=List[Room_Object], status_code=status.HTTP_200_OK)
async def get_AllRoom_Details():
    """ query = 'SELECT * FROM room'
    cur.execute(query)
    for i in cur:
        print(i) """
    results = db_Session.query(Room).all()

    return results

"""Returns a room with a certain room_id or an error if the room does not exist"""
@app.get("/Rooms/{room_id}", response_model= Room_Object, status_code=status.HTTP_200_OK)
async def get_Specific_Room(room_id: str):
    specificRoomDetail = db_Session.query(
        Room).filter(Room.room_id == room_id)

    if not specificRoomDetail.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Room with the id {room_id} does not exist')

    return specificRoomDetail


"""Updates a room with a certain room_id or returns an error if the room does not exist"""
"""Example room update object 
   {
    "room_size": 55,
    "room_name": "Living room changed"
    }"""
@app.put("/Rooms/{room_id}", status_code=status.HTTP_200_OK)
async def update_RoomDetails(room_id: str, request: Update_RoomObject):
    updateRoomDetail = db_Session.query(Room).filter(Room.room_id == room_id)
    if not updateRoomDetail.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Room with the id {room_id} is not available')
    updateRoomDetail.update(
        {'room_size': request.room_size, 'room_name': request.room_name})
    db_Session.commit()
    return {"code": "success", "message": "updated room"}

"""Deletes a room with a certain room_id or returns an error if the room does not exist"""
@app.delete("/Rooms/{room_id}", status_code=status.HTTP_200_OK)
async def delete_Room(room_id: str):
    deleteRoom = db_Session.query(Room).filter(Room.room_id == room_id).one()
    if not deleteRoom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Room with the room id {room_id} is not found')
    db_Session.delete(deleteRoom)
    db_Session.commit()
    return {"code": "success", "message": f"deleted room with id {room_id}"}


# Lights
"""Creates a new light in a room in the database and returns the light on success. Light_id needs to be unique in the room (Light_id is unique per definition due to zigbee)"""
"""Example light object 
   {
    "light_id": "0x804b50fffeb72fd9",
    "name": "Led Strip"
    }"""
@app.post("/Rooms/{room_id}/Lights", response_model=Lights_Object, status_code=status.HTTP_201_CREATED)
async def add_light(room_id: str, addLight: Lights_Object):
    addLight = Light(
        room_id=room_id, light_id=addLight.light_id, name=addLight.name)
    try:
        db_Session.add(addLight)
        db_Session.flush()
        db_Session.commit()

        write_to_json("Lights", room_id, addLight.light_id)

    except Exception as ex:
        logger.error(f"{ex.__class__.__name__}: {ex}")
        db_Session.rollback()

    return addLight

"""Returns all the lights in a room"""
@app.get("/Rooms/{room_id}/Lights", response_model=List[Lights_Object], status_code=status.HTTP_200_OK)
async def get_All_Lights(room_id: str):
    getAllLights = db_Session.query(Light).filter(
        Light.room_id == room_id).all()
    return getAllLights


"""Returns a specific light in a room or an error if the light does not exist in the room"""
@app.get("/Rooms/{room_id}/Lights/{light_id}/", response_model=Lights_Object, status_code=status.HTTP_200_OK)
async def get_Specific_Light(room_id: str, light_id: str):
    getSpecificLight = db_Session.query(Light).filter(
        Light.room_id == room_id, Light.light_id == light_id)
    if not getSpecificLight.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Light with the id {light_id} is not available in room {room_id}')
    return getSpecificLight

"""Updates a specific light in a room and returns it or returns an error if the light does not exist in the room """
"""Example light object 
   {
    "name": "Led Strip changed"
    }"""
@app.put("/Rooms/{room_id}/Lights/{light_id}", status_code=status.HTTP_200_OK)
async def update_light(room_id: str, light_id: str, request: Update_LightObject):
    updateLight = db_Session.query(Light).filter(
        Light.room_id == room_id, Light.light_id == light_id)
    if not updateLight.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Light with the id {light_id} is not available in room {room_id}')
    updateLight.update({'name': request.name})
    db_Session.commit()
    return updateLight

"""Deletes a specific light in a room or returns an error if the light does not exist in the room"""
@app.delete("/Rooms/{room_id}/Lights/{light_id}", status_code=status.HTTP_200_OK)
async def delete_light(room_id: str, light_id: str):
    deleteLight = db_Session.query(Light).filter(
        Light.room_id == room_id, Light.light_id == light_id).one()
    if not delete_light:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Light with the id {light_id} is not available in room {room_id}')
    db_Session.delete(deleteLight)
    db_Session.commit()
    return {"code": "success", "message": f"deleted light with id {light_id} from room {room_id}"}


#  Lights Operation
"""Toggles a light in a room with a specific light_id"""
"""does not contain a body"""
@app.post("/Rooms/{room_id}/Lights/{light_id}/Activation", status_code=status.HTTP_200_OK)
async def activate_Light(room_id: str, light_id: str):

    data = {}
    data["state"] = "TOGGLE"
    topic = f"zigbee2mqtt/{light_id}/set"

    publish_message(topic, data)

    return {"code": "success", "message": "Device toggled"}

"""Changes the settings of a light via a Light Operation Objects."""
"""Example Light Operation Object 
   {
    "turnon": "ON",
    "brightness": 200,
    "color": {"hex":"#466bca"}
    }"""
@app.post("/Rooms/{room_id}/Lights/{light_id}/ComplexSetting", status_code=status.HTTP_200_OK)
async def complex_setting_light(room_id: str, light_id: str, operation: Light_Operation_Object):

    data = {}
    if operation.turnon == True:
        data["state"] = "ON"
    else:
        data["state"] = "OFF"
    color = {}
    color["hex"] = operation.hex
    data["color"] = color
    data["brightness"] = operation.brightness

    topic = f"zigbee2mqtt/{light_id}/set"

    publish_message(topic, data)

    return {"code": "success", "message": "Device Settings changed"}

"""Returns the Operational Data for a Light. Either state an interval for the amount of days to go back, define a from and to in Unix Timestamps (ms) or leave everything on 0 to get all data"""
"""Example time query object 
   {
    "interval": 5,
    "timespan_from": 0,
    "timespan_to": 0
    }"""
@app.post("/Rooms/{room_id}/Lights/{light_id}/GetOperations", response_model=List[Light_Operation_Return_Object], status_code=status.HTTP_200_OK)
async def get_light_data(room_id: str, light_id: str, request: Time_Query_Object):

    if request.timespan_from != 0 and request.timespan_to != 0 and request.interval == 0:

        # conver to timestamp for comparison
        to = datetime.fromtimestamp(to)
        from_t = datetime.fromtimestamp(from_t)

        results = db_Session.query(Light_Operation).from_statement(
            text("""SELECT * FROM Light_Operation WHERE room_id = :ri and light_id = :li and time < :to and time > :ft ORDER BY time desc""")
        ).params(ri=room_id, li=light_id, to=request.timespan_to, ft=request.timespan_from).all()

        return results

    elif request.timespan_from == 0 and request.timespan_to == 0 and request.interval > 0:

        results = db_Session.query(Light_Operation).from_statement(
            text("""SELECT * FROM Light_Operation WHERE light_id = :li and time > now() - INTERVAL ':interval days' ORDER BY time desc""")
        ).params(interval=request.interval, ri=room_id, li=light_id).all()

        return results

    elif request.timespan_from == 0 and request.timespan_to == 0 and request.interval == 0:
        results = db_Session.query(Light_Operation).filter(Light_Operation.room_id == room_id,
                                                           Light_Operation.light_id == light_id).order_by(Light_Operation.time.desc()).all()
        return results

    else:
        raise HTTPException(
            status_code=400, detail=f'Bad arguments. Pass one value for interval, both values for from and to, or none for all data for the device.')

"""Trigger a manual save of the current device state of the light in a room"""
"""does not contain a body"""
@app.post("/Rooms/{room_id}/Lights/{light_id}/ManualSavestate", status_code = status.HTTP_200_OK)
async def get_status_of_light(room_id: str, light_id: str):

    data = {}
    data["state"] = " "
    topic = f"zigbee2mqtt/{light_id}/get"

    publish_message(topic, data)

    return {"code": "success", "message": "Manual save triggered"}

"""Post Operational Data for a light in a room"""
"""Example Operational Light object 
    {
        "turnon": True
        "brightness": 200
        "color_x": 0.125
        "color_y": 0.5
    }""" 
"""Mind: The color is set via a hex code, the device represents the color in the xy colorspace"""
@app.post("/Rooms/{room_id}/Lights/{light_id}/Operations", status_code = status.HTTP_200_OK)
async def post_operation_data_lights(room_id: str, light_id: str, body: Light_Operation_Storing_Object):
    new_operation = Light_Operation(room_id=room_id, light_id=light_id, time=datetime.now(), 
    turnon=body.turnon, color_y=body.color_y, color_x=body.color_x, brightness=body.brightness)
    try:
        db_Session.add(new_operation)
        db_Session.flush()
        db_Session.commit()
    except Exception as ex:
        logger.error(f"{ex.__class__.__name__}: {ex}")
        db_Session.rollback()

    return new_operation


#Motion Sensors
"""Creates a new motion sensor in a room in the database and returns the motion sensor on success. Sensor_id needs to be unique in the room (Sensor_id is unique per definition due to zigbee)"""
"""Example Motion Sensor object 
   {
    "sensor_id": "0x804b50fffeb72fd9",
    "name": "Sensor 1"
    }"""
@app.post("/Rooms/{room_id}/Motion_Sensors", response_model=Motion_Sensor_Object, status_code=status.HTTP_201_CREATED)
async def add_Motion_Sensor(room_id: str, addMotionSensor: Motion_Sensor_Object):
    addMotionSensor = Motion_Sensor(
        room_id=room_id, sensor_id=addMotionSensor.sensor_id, name=addMotionSensor.name)
    try:
        db_Session.add(addMotionSensor)
        db_Session.flush()
        db_Session.commit()

        write_to_json("Motion_Sensors", room_id, addMotionSensor.sensor_id)

    except Exception as ex:
        logger.error(f"{ex.__class__.__name__}: {ex}")
        db_Session.rollback()

    return addMotionSensor

"""Returns all the motion sensors in a room"""
@app.get("/Rooms/{room_id}/Motion_Sensors", response_model=List[Motion_Sensor_Object], status_code=status.HTTP_200_OK)
async def get_All_Motion_Sensors(room_id: str):
    allMotionSensors = db_Session.query(Motion_Sensor).filter(
        Motion_Sensor.room_id == room_id).all()
    return allMotionSensors

"""Returns a specific motion sensor in a room or an error if the motion sensor does not exist in the room"""
@app.get("/Rooms/{room_id}/Motion_Sensors/{sensor_id}", response_model=Motion_Sensor_Object, status_code=status.HTTP_200_OK)
async def get_Specific_Light(room_id: str, sensor_id: str):
    getSpecificMotionSensor = db_Session.query(Motion_Sensor).filter(
        Motion_Sensor.room_id == room_id, Motion_Sensor.sensor_id == sensor_id)
    if not getSpecificMotionSensor.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Motion Sensor with the id {sensor_id} is not available in room {room_id}')
    return getSpecificMotionSensor

"""Updates a specific motion sensor in a room and returns it or returns an error if the motion sensor does not exist in the room """
"""Example Motion Sensor update object 
   {
    "name": "Sensor 1 changed"
    }"""
@app.put("/Rooms/{room_id}/Motion_Sensors/{sensor_id}", response_model=Motion_Sensor_Object, status_code=status.HTTP_200_OK)
async def update_motion_sensor(room_id: str, sensor_id: str, request: Motion_Sensor_Update_Object):
    updateMotionSensor = db_Session.query(Motion_Sensor).filter(
        Motion_Sensor.room_id == room_id, Motion_Sensor.sensor_id == sensor_id)
    if not updateMotionSensor.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Motion Sensor with the id {sensor_id} is not available in room {room_id}')
    updateMotionSensor.update({'name': request.name})
    db_Session.commit()
    return updateMotionSensor

"""Deletes a specific motion sensor in a room or returns an error if the motion sensor does not exist in the room"""
@app.delete("/Rooms/{room_id}/Motion_Sensors/{sensor_id}", status_code=status.HTTP_200_OK)
async def delete_motion_sensor(room_id: str, sensor_id: str):
    deleteMotionSensor = db_Session.query(Motion_Sensor).filter(
        Motion_Sensor.room_id == room_id, Motion_Sensor.sensor_id == sensor_id).one()
    if not deleteMotionSensor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Light with the id {sensor_id} is not available in room {room_id}')
    db_Session.delete(deleteMotionSensor)
    db_Session.commit()
    return {"code": "success", "message": f"deleted light with id {sensor_id} from room {room_id}"}


#Motion Sensors Operations
"""Returns the Operational Data for a motion sensor. Either state an interval for the amount of days to go back, define a from and to in Unix Timestamps (ms) or leave everything on 0 to get all data"""
"""Example time query object 
   {
    "interval": 5,
    "timespan_from": 0,
    "timespan_to": 0
    }"""
@app.post("/Rooms/{room_id}/Motion_Sensors/{sensor_id}/GetOperations", response_model=List[Motion_Sensor_Operation_Object], status_code=status.HTTP_200_OK)
async def get_motion_sensor_data(room_id: str, sensor_id: str, request: Time_Query_Object):

    if request.timespan_from != 0 and request.timespan_to != 0 and request.interval == 0:

        # conver to timestamp for comparison
        to = datetime.fromtimestamp(to)
        from_t = datetime.fromtimestamp(from_t)

        results = db_Session.query(Motion_Sensor_Operation).from_statement(
            text("""SELECT * FROM Motion_Sensor_Operation WHERE room_id = :ri and sensor_id = :si and time < :to and time > :ft ORDER BY time desc""")
        ).params(ri=room_id, si=sensor_id, to=request.timespan_to, ft=request.timespan_from).all()

        return results

    elif request.timespan_from == 0 and request.timespan_to == 0 and request.interval > 0:

        results = db_Session.query(Motion_Sensor_Operation).from_statement(
            text("""SELECT * FROM Motion_Sensor_Operation WHERE room_id = :ri and sensor_id = :si and time > now() - INTERVAL ':interval days' ORDER BY time desc""")
        ).params(interval=request.interval, ri=room_id, si=sensor_id).all()

        return results

    elif request.timespan_from == 0 and request.timespan_to == 0 and request.interval == 0:
        results = db_Session.query(Motion_Sensor_Operation).filter(Motion_Sensor_Operation.room_id == room_id,
                                                          Motion_Sensor_Operation.sensor_id == sensor_id).order_by(Motion_Sensor_Operation.time.desc()).all()
        return results

    else:
        raise HTTPException(
            status_code=400, detail=f'Bad arguments. Pass one value for interval, both values for from and to, or none for all data for the device.')

"""Triggers a manual save of the current device state of the motion sensor in a room"""
"""does not contain a body"""
@app.post("/Rooms/{room_id}/Motion_Sensors/{sensor_id}/ManualSavestate", status_code = status.HTTP_200_OK)
async def get_status_of_motion_sensor(room_id: str, sensor_id: str):

    data = {}
    data["state"] = " "
    topic = f"zigbee2mqtt/{sensor_id}/get"

    publish_message(topic, data)

    return {"code": "success", "message": "Manual save triggered"}

"""Post Operational Data for a motion sensor in a room"""
"""Example Operational Motion Sensor object 
    {
        "detection": True
    }""" 
@app.post("/Rooms/{room_id}/Motion_Sensors/{sensor_id}/Operations", status_code = status.HTTP_200_OK)
async def post_operation_data_lights(room_id: str, sensor_id: str, body: Motion_Sensor_Storing_Object):
    new_operation = Motion_Sensor_Operation(room_id=room_id, sensor_id=sensor_id, time=datetime.now(), detection = body.detection)
    try:
        db_Session.add(new_operation)
        db_Session.flush()
        db_Session.commit()
    except Exception as ex:
        logger.error(f"{ex.__class__.__name__}: {ex}")
        db_Session.rollback()

    return new_operation


#Power Plugs
"""Creates a new power plug in a room in the database and returns the power plug on success. Plug_id needs to be unique in the room (Sensor_id is unique per definition due to zigbee)"""
"""Example Power Plug object 
   {
    "plug_id": "0x804b50fffeb72fd9",
    "name": "Plug 1"
    }"""
@app.post("/Rooms/{room_id}/Power_Plugs", response_model=Power_Plug_Object, status_code=status.HTTP_201_CREATED)
async def add_Power_Plug(room_id: str, addPowerPlug: Power_Plug_Object):
    addPowerPlug = Power_Plug(
        room_id=room_id, plug_id=addPowerPlug.plug_id, name=addPowerPlug.name)
    try:
        db_Session.add(addPowerPlug)
        db_Session.flush()
        db_Session.commit()

        write_to_json("Power_Plugs", room_id, addPowerPlug.plug_id)

    except Exception as ex:
        logger.error(f"{ex.__class__.__name__}: {ex}")
        db_Session.rollback()

    return addPowerPlug

"""Returns all the power plug in a room"""
@app.get("/Rooms/{room_id}/Power_Plugs", response_model=List[Power_Plug_Object], status_code=status.HTTP_200_OK)
async def get_All_Power_Plugs(room_id: str):
    allPowerPlugs = db_Session.query(Power_Plug).filter(
        Power_Plug.room_id == room_id).all()
    return allPowerPlugs

"""Returns a specific power plug in a room or an error if the power plug does not exist in the room"""
@app.get("/Rooms/{room_id}/Power_Plugs/{plug_id}", response_model=Power_Plug_Object, status_code=status.HTTP_200_OK)
async def get_Specific_Light(room_id: str, plug_id: str):
    getSpecificPowerPlug = db_Session.query(Power_Plug).filter(
        Power_Plug.room_id == room_id, Power_Plug.plug_id == plug_id)
    if not getSpecificPowerPlug.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Power Plug with the id {plug_id} is not available in room {room_id}')
    return getSpecificPowerPlug

"""Updates a specific power plug in a room and returns it or returns an error if the power plug does not exist in the room """
"""Example Power Plug update object 
   {
    "name": "Plug 1 changed"
    }"""
@app.put("/Rooms/{room_id}/Power_Plugs/{plug_id}", response_model=Power_Plug_Object, status_code=status.HTTP_200_OK)
async def update_power_plug(room_id: str, plug_id: str, request: Power_Plug_Update_Object):
    updatePowerPlug = db_Session.query(Power_Plug).filter(
        Power_Plug.room_id == room_id, Power_Plug.plug_id == plug_id)
    if not updatePowerPlug.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Motion Sensor with the id {plug_id} is not available in room {room_id}')
    updatePowerPlug.update({'name': request.name})
    db_Session.commit()
    return updatePowerPlug

"""Deletes a specific power plug  in a room or returns an error if the power plug does not exist in the room"""
@app.delete("/Rooms/{room_id}/Power_Plugs/{plug_id}", status_code=status.HTTP_200_OK)
async def delete_power_plug(room_id: str, plug_id: str):
    deletePowerPlug = db_Session.query(Power_Plug).filter(
        Power_Plug.room_id == room_id, Power_Plug.plug_id == plug_id).one()
    if not deletePowerPlug:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Light with the id {plug_id} is not available in room {room_id}')
    db_Session.delete(deletePowerPlug)
    db_Session.commit()
    return {"code": "success", "message": f"deleted light with id {plug_id} from room {room_id}"}



#Power Plugs Operations
"""Returns the Operational Data for a power plug. Either state an interval for the amount of days to go back, define a from and to in Unix Timestamps (ms) or leave everything on 0 to get all data"""
"""Example time query object 
   {
    "interval": 5,
    "timespan_from": 0,
    "timespan_to": 0
    }"""
@app.post("/Rooms/{room_id}/Power_Plugs/{plug_id}/GetOperations", response_model=List[Power_Plug_Operation_Object], status_code=status.HTTP_200_OK)
async def get_power_plug_data(room_id: str, plug_id: str, request: Time_Query_Object):

    if request.timespan_from != 0 and request.timespan_to != 0 and request.interval == 0:

        # conver to timestamp for comparison
        to = datetime.fromtimestamp(to)
        from_t = datetime.fromtimestamp(from_t)

        results = db_Session.query(Power_Plug_Operation).from_statement(
            text("""SELECT * FROM Power_Plug_Operation WHERE room_id = :ri and plug_id = :pi and time < :to and time > :ft ORDER BY time desc""")
        ).params(ri=room_id, pi=plug_id, to=request.timespan_to, ft=request.timespan_from).all()

        return results

    elif request.timespan_from == 0 and request.timespan_to == 0 and request.interval > 0:

        results = db_Session.query(Power_Plug_Operation).from_statement(
            text("""SELECT * FROM Power_Plug_Operation WHERE room_id = :ri and plug_id = :pi and time > now() - INTERVAL ':interval days' ORDER BY time desc""")
        ).params(interval=request.interval, ri=room_id, pi=plug_id).all()

        return results

    elif request.timespan_from == 0 and request.timespan_to == 0 and request.interval == 0:
        results = db_Session.query(Power_Plug_Operation).filter(Power_Plug_Operation.room_id == room_id,
                                                          Power_Plug_Operation.plug_id == plug_id).order_by(Power_Plug_Operation.time.desc()).all()
        return results

    else:
        raise HTTPException(
            status_code=400, detail=f'Bad arguments. Pass one value for interval, both values for from and to, or none for all data for the device.')

"""Triggers a manual save of the current device state of the power plug in a room"""
"""does not contain a body"""
@app.post("/Rooms/{room_id}/Power_Plugs/{plug_id}/ManualSavestate", status_code = status.HTTP_200_OK)
async def get_status_of_power_plug(room_id: str, plug_id: str):

    data = {}
    data["state"] = " "
    topic = f"zigbee2mqtt/{plug_id}/get"

    publish_message(topic, data)

    return {"code": "success", "message": "Manual save triggered"}

"""Post Operational Data for a power plug in a room"""
"""Example Operational Power Plug object 
    {
        "turnon": True
    }""" 
@app.post("/Rooms/{room_id}/Power_Plugs/{plug_id}/Operations", status_code = status.HTTP_200_OK)
async def post_operation_data_power_plugs(room_id: str, plug_id: str, body: Power_Plug_Storing_Object):
    new_operation = Power_Plug_Operation(room_id=room_id, plug_id=plug_id, time=datetime.now(), turnon = body.turnon)

    last_operation = db_Session.query(Power_Plug_Operation).filter(Power_Plug_Operation.room_id == room_id, Power_Plug_Operation.plug_id == plug_id).order_by(Power_Plug_Operation.time.desc()).first()

    #Lupus 12133 plugs are not completely compatible with zigbee2mqtt and tend to send multiple state events --> this ensures to only store one of the event states
    if last_operation == None or (last_operation != None and last_operation.turnon != new_operation.turnon):
        try:
            db_Session.add(new_operation)
            db_Session.flush()
            db_Session.commit()
        except Exception as ex:
            logger.error(f"{ex.__class__.__name__}: {ex}")
            db_Session.rollback()

    return new_operation

"""Toggles a power plug in a room with a specific plug_id"""
"""does not contain a body"""
@app.post("/Rooms/{room_id}/Power_Plugs/{plug_id}/Activation", status_code=status.HTTP_200_OK)
async def activate_Power_Plug(room_id: str, plug_id: str):

    data = {}
    data["state"] = "TOGGLE"
    topic = f"zigbee2mqtt/{plug_id}/set"

    publish_message(topic, data)

    return {"code": "success", "message": "Device toggled"}


#**Helper Methods**

"""Writes to devices.json after a new device is saved in the database"""
def write_to_json(device_type, device_room, device_key):
     with open("devices.json", 'r+') as f:
        devices = json.load(f)
    
        information = {}
        information["device_type"] = device_type
        information["device_room"] = device_room

        devices[device_key] = information

        f.seek(0)
        
        json.dump(devices, f, indent = 4)