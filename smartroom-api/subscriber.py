import paho.mqtt.client as mqtt
import time
import logging

LOGGER = logging.getLogger()

def on_message(client, userdata, message):
    print("message topic=", message.topic)
    print("message received ", str(message.payload.decode("utf-8")))
    

def on_connect(client, userdata, flags, rc):
    print("Connected to mqtt broker!")


    #use # as multiple level wildcard and + as single level wildcard
    client.subscribe("zigbee2mqtt/#")



client = mqtt.Client("zigbee2mqtt")
client.on_message=on_message
client.on_connect=on_connect

client.connect("localhost", 1883, 60)
client.loop_forever()


