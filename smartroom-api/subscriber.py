import paho.mqtt.client as mqtt
import time
import logging
import json
import requests

LOGGER = logging.getLogger()
BASE_URL = "http://simplerest:8000/Rooms/"

def on_message(client, userdata, message):
    print("message topic=", message.topic)
    print("message received ", str(message.payload.decode("utf-8")))

    with open("devices.json", "r") as f:
        devices = json.load(f)
    
    if len(message.topic) == 30:
        device = message.topic[12:]
        try:
            device_group = devices[device]["device_type"]
            device_room = devices[device]["device_room"]
            payload = json.loads(str(message.payload.decode("utf-8")))

            # map to the correct data type
            if device_group == "Lights":
                data = {}
                if payload["state"] == "OFF":
                    data["turnon"] = False
                else:
                    data["turnon"] = True
                data["brightness"] = int(payload["brightness"])
                data["color_x"] = float(payload["color"]["x"])
                data["color_y"] = float(payload["color"]["y"])

                print(data)
                
                res = requests.post(
                    f"{BASE_URL}{device_room}/Lights/{device}/Operations", json=data)
            
            elif device_group == "Motion_Sensors":
                data = {}
                data["detection"] = bool(payload["occupancy"])
                
                print(data)

                res = requests.post(
                    f"{BASE_URL}{device_room}/Motion_Sensors/{device}/Operations", json=data)

            elif device_group == "Power_Plugs":
                data = {}
                if payload["state"] == "OFF":
                    data["turnon"] = False
                else:
                    data["turnon"] = True
                
                print(data)

                res = requests.post(
                    f"{BASE_URL}{device_room}/Power_Plugs/{device}/Operations", json=data)

            elif device_group == "Remote":
                
                command = payload["action"]
                if command == "emergency":
                    #**DEFINE HERE WHAT TO DO ON EMERGENCY BUTTON**
                    requests.post(f"{BASE_URL}1/Lights/0x804b50fffeb72fd9/Activation")

                elif command == "arm_all_zones":
                    #**DEFINE HERE WHAT TO DO ON ALL ZONES BUTTON**
                    requests.post(f"{BASE_URL}1/Power_Plugs/0x847127fffe9f37ad/Activation")

                elif command == "arm_day_zones":
                    #**DEFINE HERE WHAT TO DO ON ALL ZONES BUTTON**
                    requests.post(f"{BASE_URL}1/Power_Plugs/0x847127fffe9c05c5/Activation")

                elif command == "disarm":
                    #**DEFINE HERE WHAT TO DO ON DISARM**
                    print("No Operation set")

        except KeyError:
            print("Key {device} was not found")
            
            

def on_connect(client, userdata, flags, rc):
    print("Connected to mqtt broker!")

    # use # as multiple level wildcard and + as single level wildcard
    client.subscribe("zigbee2mqtt/#")


client = mqtt.Client("subscriber_indocker")
client.on_message = on_message
client.on_connect = on_connect

# ****CHANGE IP ADDRESS HERE****
client.connect("192.168.1.35", 1883, 60)
client.loop_forever()
