from publisher import publish_message



data = {}
data["id"] = "0x804b50fffeb72fd9"
topic = "zigbee2mqtt/bridge/request/device/remove"

publish_message(topic, data)