from sqlite3 import Timestamp
from xmlrpc.client import DateTime
from pydantic import BaseModel
from datetime import datetime


class Room_Object(BaseModel):
    room_id: str
    room_size:int
    room_name: str
  
    class Config:
        orm_mode = True

class Update_RoomObject(BaseModel):
    room_size:int
    room_name: str
  
    class Config:
        orm_mode = True

class Lights_Object(BaseModel):
    light_id: str
    name: str
    

    class Config:
        orm_mode = True

class Update_LightObject(BaseModel):
    name: str

    class Config:
        orm_mode = True


class Light_Operation_Object(BaseModel):
    turnon:bool
    brightness: int
    hex: str

    
    class Config:
        orm_mode = True        

class Light_Operation_Storing_Object(BaseModel):
    turnon:bool
    brightness: int
    color_x: float
    color_y: float

    class Config:
        orm_mode = True  

class Light_Operation_Return_Object(BaseModel):
    turnon:bool
    brightness: int
    color_x: float
    color_y: float
    time: Timestamp
    
    class Config:
        orm_mode = True



class Time_Query_Object(BaseModel):
    interval: int
    timespan_from: int
    timespan_to: int
    


class Motion_Sensor_Object(BaseModel):
    sensor_id: str
    name: str

    class Config:
        orm_mode = True        

class Motion_Sensor_Update_Object(BaseModel):
    name: str

    class Config:
        orm_mode = True


class Motion_Sensor_Operation_Object(BaseModel):
    detection: bool
    time: Timestamp

    class Config:
        orm_mode = True

class Motion_Sensor_Storing_Object(BaseModel):
    detection:bool

    class Config:
        orm_mode = True


class Power_Plug_Object(BaseModel):
    room_id: str
    plug_id: str
    name: str
    is_active: bool
    time:Timestamp

    class Config:
        orm_mode = True

class Power_Plug_Operation_Object(BaseModel):
    is_active: bool

    class Config:
        orm_mode = True

