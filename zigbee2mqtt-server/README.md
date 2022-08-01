# Zigbee2Mqtt Server deployment with Docker
## Important Notes
The zigbee2mqtt server is based on docker images and needs to be run on a host machine with Linux installed. In order to operate as intended the Sonoff dongle needs to be mapped to the docker container. This is not possible on Windows. It is recommended to run this server on a Raspberry Pi 3 or 4 with Raspberry OS.

It is highly recommended to set the ```permit_join``` option to false once all devices are joined to the network. This prevents other unwanted devices from joining the network.

## Installation and Deployment
1. Open the locally cloned project and open the ```zigbee2mqtt-server``` folder. Open the ```docker-compose.yaml``` and change the device mount point if necessary. In Linux use the ```lsblk``` command to list all the mounted USB devices and figure out which one the Sonoff dongle is mounted to. The USB mount point is specified in the ```devices``` section of the zigbee2mqtt container in the file.

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

2. Create a subfolder ```zigbee2mqtt-data```. In the subfolder create a ```configuration.yaml```, which is used to configure the zigbee network. Use the following configuration.

```
homeassistant: false
permit_join: true
mqtt:
  base_topic: zigbee2mqtt
  server: mqtt://mqtt
serial:
  port: /dev/ttyUSB0
advanced:

  network_key:
    - 169
    - 241
    - 62
    - 51
    - 4
    - 227
    - 2
    - 216
    - 237
    - 244
    - 102
    - 228
    - 105
    - 246
    - 224
    - 129
  pan_id: 6755
  ext_pan_id:
    - 222
    - 222
    - 222
    - 222
    - 222
    - 222
    - 222
    - 222
  channel: 11
  homeassistant_legacy_entity_attributes: false
  legacy_api: false
  legacy_availability_payload: false
external_converters:
  - 12133.js
device_options:
  legacy: false
```

3. Create a second file ```12133.js``` in the subfolder. This is an external converter to provide support for the Lupus 12133 power plug, since this model is out of the box not supported by zigbee2mqtt. 

```
const fz = require('zigbee-herdsman-converters/converters/fromZigbee');
const tz = require('zigbee-herdsman-converters/converters/toZigbee');
const exposes = require('zigbee-herdsman-converters/lib/exposes');
const reporting = require('zigbee-herdsman-converters/lib/reporting');
const e = exposes.presets;

const definition = {
    zigbeeModel: ['TS011F'],
    model: '12133',
    vendor: 'Lupus',
    description: 'Power Plug',
    fromZigbee: [fz.on_off],
    toZigbee: [tz.on_off],
    exposes: [e.switch()],

    // The configure method below is needed to make the device reports on/off state changes
    // when the device is controlled manually through the button on it.
    configure: async (device, coordinatorEndpoint, logger) => {
        const endpoint = device.getEndpoint(1);
        await reporting.bind(endpoint, coordinatorEndpoint, ['genOnOff']);
    },
};
```

4. Start the docker containers with ```docker-compose up``` (```-d``` can be used to start the containers in detached mode). 

## Pair new devices
Pairing devices to the zigbee network and adding them to the API are NOT connected. Meaning, you have to manually add the device to zigbee and then add the device to the API with the id used in the zigbee network. 

To add a device to the zigbee network first make sure the ```permit_join``` option is set to ```true``` in the ```configuration.yaml``` file. Otherwise the network will not allow devices to join. To perform the join, put the device into pairing mode (this highly depends on the device). The pairing mode will reset the device, delete the current connection and connect to a new available network. 

## Troubleshooting
1. Error related to duplicate network keys:
   This can happen if there are already zigbee networks nearby. The error can be avoided by marginally changing the ```pan_id```, ```ext_pan_id``` and ```network_key```. 
   
2. For Raspberry Pis running Raspberry OS 10 (Buster) it can be necessary to install ```libseccomp2```. Raspberry OS Buster is the oldstable version since August 14, 2021, so the recommended solution is to update to the new stable Raspberry OS version 11 (Bullseye).
