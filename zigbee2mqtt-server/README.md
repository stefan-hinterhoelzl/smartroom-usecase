# Zigbee2Mqtt Server deployment with Docker
## Important Notes:
The zigbee2mqtt server is based on docker images and needs to be run on a host machine with Linux installed. In order to operate as intended the Sonoff dongle needs to be mapped to the docker container, this is not possible on Windows. 

## Installation and Deployment
Open the locally cloned project and open the ```zigbee2mqtt-server``` folder. Open the docker-compose file and change the device mount point if necessary. In Linux use the ```lsblk``` command to list all the mounted USB devices and figure out which one the Sonoff dongle is mounted to. The USB mount point is specified in the ```devices``` section of the zigbee2mqtt image in the file

```
version: '3.8'
services:
  mqtt:
    image: eclipse-mosquitto:2.0
    restart: unless-stopped
    volumes:
      - "./mosquitto-data:/mosquitto"
    ports:
      - "1883:1883"
      - "9001:9001"
    command: "mosquitto -c /mosquitto-no-auth.conf"

  zigbee2mqtt:
    container_name: zigbee2mqtt
    restart: unless-stopped
    image: koenkk/zigbee2mqtt
    volumes:
      - ./zigbee2mqtt-data:/app/data
      - /run/udev:/run/udev:ro
    ports:
      - 8080:8080
    environment:
      - TZ=Europe/Berlin
    devices:
      - /dev/ttyUSB0:/dev/ttyUSB0
```

