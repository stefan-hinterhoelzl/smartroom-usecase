# A Smartroom Digital Twin Application based on Zigbee2Mqtt
This repository provides source code and documentation for setting up an example smartroom management with [zigbee2mqtt](https://www.zigbee2mqtt.io/). Status data of the devices is stored in a database to allow digital twin applications.  Currently the following devices are supported:  Motion sensors (RC7046), Müller LED strips, Lupus 12133 power plugs and the RC7054 remote. Other devices from the same category with the same data structure used in zigbee will also work. The data is stored in a [timescale database](https://www.timescale.com/), which provides extra functionality in querying timeseries data. This enables various digital twin applications. 


## Contents of the Repository
The system is based on three layers. 



1. Zigbee Layer:
The first layer is the zigbee network created by the Sonoff dongle. This network is not visible through the repository and is started as a component of the    zigbee2mqtt server. The devices are connected via the Sonoff dongle. 
2. Zigbee2MQTT Layer:   
The second layer is the [zigbee2mqtt server](https://github.com/stefan-hinterhoelzl/smartroom-usecase/tree/master/zigbee2mqtt-server). This server uses [mosquitto](https://mosquitto.org/) to relay messages going to and coming from the end devices. The zigbee2mqtt server and mosquitto broker are combined via separate docker        images in a docker compose file. 
3. Digital Twin Layer:
The [API](https://github.com/stefan-hinterhoelzl/smartroom-usecase/tree/master/smartroom-api) with the fastAPI combined with a mosquitto publisher to transmit messages to devices, the mosquitto subscriber which listens for messages, Grafana, pgadmin and the timscaledb all running in their own containers combined via a docker-compose file. The API maintains devices and stores operational data of these devices. This timeseries operational data can be queried with the capabilities of the timescale database. Moreover, the API allows to set properties of devices, for example turning devices on and off. 


