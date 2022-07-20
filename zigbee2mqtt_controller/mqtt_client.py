import paho.mqtt.client as mqtt
import time
import logging

LOGGER = logging.getLogger()

def on_message(client, userdata, message):
    print("message received ", str(message.payload.decode("utf-8")))
    print("message topic=", message.topic)

def on_connect(client, userdata, flags, rc):
    print("Connected to mqtt broker!")

    client.subscribe("zigbee2mqtt/0xbc33acfffe108988")



client = mqtt.Client("Zigbee2Mqtt")
client.on_message=on_message
client.on_connect=on_connect

client.connect("localhost", 1883, 60)
client.loop_forever()


