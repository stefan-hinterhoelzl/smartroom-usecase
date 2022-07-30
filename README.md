# A Smartroom Digital Twin Application based on Zigbee2Mqtt
This repository provides source code and documentation for setting up an example smartroom management. Status data of the devices is stored in a database to allow digital twin applications. 

## Use Case Description
This repository is designed to provide a custom-built exemplar for digital twins. Currently motion sensors (RC7046), Müller LED strips, Lupus 12133 power plugs and the RC7054 remote to control the devices are supported. Other devices from the same category with the same data structure used in zigbee will also work. The data is stored in a timescale database, which provides extra functionality in querying timeseries data. This enables various digital twin applications. 

## Requirements
######1.	Software
To run this smartroom application you will need to install docker and docker-compose on at least one machine. The two separate software system can and should preferably be run on two different host machines. The host running the zigbee2mqtt server needs to run Linux. Currently only Linux allows to map a USB port into a docker container. This is required for the Sonoff Dongle. 

######2.	Hardware
When it comes to Hardware several devices are necessary. Following devices are used for the zigbee network:
•	Sonoff 3.0 USB Dongle Plus (https://sonoff.tech/product/diy-smart-switch/sonoff-zigbee-dongle-plus-efr32mg21/)
•	Motion Sensor (https://wooxhome.com/woox-r7046-smart-pir-motion-sensor-p46)
•	Power Plug (https://www.reichelt.at/at/de/funksteckdose-zigbee-ls-12133-p282353.html?r=1)
•	Remote (https://wooxhome.com/products-c10/security-c6/woox-r7054-smart-remote-control-p53)

It is recommended to run the zigbee2mqtt server on a Raspberry Pi running Raspbian OS. 
The smartroom API can be run on any machine (Windows, Linux, Mac) which has docker and docker-compose installed. 

##Contents of the Repository
The system is based on three layers. The first layer is the zigbee network created by the Sonoff dongle. This network is not visible through the repository and is started as a component of the zigbee2mqtt service. The devices are connected via the Sonoff dongle. The second layer is the zigbee2mqtt server. This server uses mosquito to relay messages going to and coming from the end devices. The third and top layer is a Python API combined with a timescale database and mqtt publisher/subscriber to control and monitor the devices. 
The API includes Grafana and pgadmin to monitor and visualize the data. 

The system is divided into two separate components. Both are deployed via docker compose files. 
1.	The zigbee2mqtt server and mosquitto broker combined via separate docker images in a docker compose file. 
2.	The API with the faspAPI, the mosquitto subscriber, Grafana, pgadmin and the timscaledb all running in their own containers combined via a docker-compose file. 
