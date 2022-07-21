import paho.mqtt.client as mqtt
import time
import logging
import json



def on_connect(client, userdata, flags, rc):
    print("Connected to mqtt broker!")

    publish_data(client)





def publish_data(client):

    data = {}
    data["state"] = "OFF"
    json_data = json.dumps(data)

    print(json_data)

    client.publish("zigbee2mqtt/0x804b50fffeb72fd9/set", payload = json_data, qos = 0, retain=False)

    client.disconnect()



client = mqtt.Client("zigbee2mqtt")
client.on_connect=on_connect
client.connect("localhost", 1883, 60)
client.loop_forever()

