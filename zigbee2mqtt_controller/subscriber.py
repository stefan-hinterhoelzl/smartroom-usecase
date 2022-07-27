import paho.mqtt.client as mqtt
import time
import logging
import json
import requests

LOGGER = logging.getLogger()
BASE_URL = "http://localhost:8000/Rooms/"

# Add new Devices here
devices_types = {}
devices_types["0x804b50fffeb72fd9"] = "Lights"

devices_rooms = {}
devices_rooms["0x804b50fffeb72fd9"] = "1"


def on_message(client, userdata, message):
    print("message topic=", message.topic)
    print("message received ", str(message.payload.decode("utf-8")))

    if len(message.topic) == 30:
        device = message.topic[12:]
        device_group = devices_types[device]
        device_room = devices_rooms[device]
        payload = json.loads(str(message.payload.decode("utf-8")))

        # map to the correct data type
        if device_group == "Lights":
            data = {}
            data["turnon"] = bool(payload["state"])
            data["brightness"] = int(payload["brightness"])
            data["color_x"] = float(payload["color"]["x"])
            data["color_y"] = float(payload["color"]["y"])

            print(data)
            
            res = requests.post(
                f"{BASE_URL}{device_room}/Lights/{device}/Operations", json=data)


def on_connect(client, userdata, flags, rc):
    print("Connected to mqtt broker!")

    # use # as multiple level wildcard and + as single level wildcard
    client.subscribe("zigbee2mqtt/#")


client = mqtt.Client("subscriber")
client.on_message = on_message
client.on_connect = on_connect

# Port Change here
client.connect("192.168.1.35", 1883, 60)
client.loop_forever()
