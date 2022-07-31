# Zigbee2Mqtt Server deployment with Docker
## Important Notes:
The zigbee2mqtt server is based on docker images and needs to be run on a host machine with Linux installed. In order to operate as intended the Sonoff dongle needs to be mapped to the docker container, this is not possible on Windows. 

## Installation and Deployment
Open the locally cloned project and open the zigbee2mqtt-server folder. Open the docker-compose file and change the device mount point if necessary. In Linux use the '''lsblk''' command to list all the mounted USB devices and figure out which one the Sonoff dongle is mounted to. 


