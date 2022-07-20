from sqlite3 import Timestamp
from xmlrpc.client import DateTime
from pydantic import BaseModel
from datetime import datetime


class Room_Object(BaseModel):
    room_id: str
    room_size:int
    measurement_unit:str
  
    class Config:
        orm_mode = True

class Update_RoomObject(BaseModel):
    room_size:int
    measurement_unit:str
  
    class Config:
        orm_mode = True

class AirQuality_Properties_Object(BaseModel):
    room_id: str
    ventilator:str
    totalnumberofpeople:int
    co2:float
    co2measurementunit:str
    temperature:float
    temperaturemeasurementunit:str
    humidity:float
    humiditymeasurementunit:str
    time:Timestamp
    
    class Config:
        orm_mode = True

class AirQuality_Temperature_Object(BaseModel):
    room_id: str
    ventilator:str
    totalnumberofpeople:int
    temperature:float
    temperaturemeasurementunit:str
    time:Timestamp
    
    class Config:
        orm_mode = True

class AirQuality_Humidity_Object(BaseModel):
    room_id: str
    ventilator:str
    totalnumberofpeople:int
    humidity:float
    humiditymeasurementunit:str
    time:Timestamp
    
    class Config:
        orm_mode = True     

class AirQuality_Co2_Object(BaseModel):
    room_id: str
    ventilator:str
    totalnumberofpeople:int
    co2:float
    co2measurementunit:str
    time:Timestamp
    
    class Config:
        orm_mode = True             

class Doors_Object(BaseModel):
    room_id: str
    door_id:str
    door_lock:bool
    connectsdoor:str
    time:Timestamp
    class Config:
        orm_mode = True

class Lights_Object(BaseModel):
    room_id: str
    light_id:str
    turnon:bool
    energyconsumption:int
    energyconsumptionunit:str
    time:Timestamp
    class Config:
        orm_mode = True

class Light_Operation_Object(BaseModel):
    
    turnon:bool
    time:Timestamp
    class Config:
        orm_mode = True        

class Windows_Object(BaseModel):
    room_id: str
    window_id:str
    isopen:bool
    time:Timestamp
    class Config:
        orm_mode = True   

class Window_Operation_Object(BaseModel):
   
    isopen:bool
    time:Timestamp
  
    class Config:
        orm_mode = True

class Ventilators_Object(BaseModel):
    room_id: str
    ventilator_id:str
    turnon:bool
    time:Timestamp
    

    class Config:
        orm_mode = True

class Ventilator_Operation_Object(BaseModel):
   
    turnon:bool
    time:Timestamp
  
    class Config:
        orm_mode = True

class Door_Operation_Object(BaseModel):
   
    door_lock:bool
    time:Timestamp
  
    class Config:
        orm_mode = True

class Room_Door_Relation_Object(BaseModel):
   
    door_id:str
    room_id:str
  
    class Config:
        orm_mode = True
        
class Room_Door_Operation_Object(BaseModel):
   
    door_id:str
   
    class Config:
        orm_mode = True