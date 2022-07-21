from publisher import publish_message



data = {}
data["state"] = "OFF"
topic = "zigbee2mqtt/0x804b50fffeb72fd9/set"

publish_message(topic, data)