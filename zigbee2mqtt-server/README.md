# Zigbee2Mqtt Server deployment with Docker
The zigbee2mqtt server creates a zigbee network and allows to pair devices to this network. The server relays messages from and to the zigbee network by converting zigbee event messages in the network into mqtt messages and vice versa. Zigbee2mqtt uses the mosquitto broker to receive and send messages. This allows for more interoperability with zigbee devices since many other software and hardware components provide functionality for dealing with mqtt messages. 

## Important Note
It is highly recommended to set the ```permit_join``` option to false once all devices are joined to the network. This prevents other unwanted devices from joining the network.

## Requirements
###### Software
To run the zigbee2mqtt server you will need to install [docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/) on a machine running any GNU/Linux distribution. Currently only Linux allows to map a USB port into a docker container. This is required for the Sonoff Dongle. 

###### Hardware
The centerpiece of the zigbee network is the sonoff dongle. It creates the zigbee network for the smartroom devices. This dongle (or a comparable product) needs to be plugged into the hosting machine of the server all the time. The hosting machine needs to have this zigbee2mqtt server locally cloned and running to work. It is recommended to run the zigbee2mqtt server on a [Raspberry Pi running Raspberry OS](https://www.raspberrypi.com/documentation/computers/getting-started.html). 

When it comes to zigbee hardware, several devices are necessary. Following devices are used for the zigbee network:
- [Sonoff 3.0 USB Dongle Plus](https://sonoff.tech/product/diy-smart-switch/sonoff-zigbee-dongle-plus-efr32mg21/)
- [Woox Motion Sensor RC7046](https://wooxhome.com/woox-r7046-smart-pir-motion-sensor-p46)
- [Lupus Power Plug 12133](https://www.reichelt.at/at/de/funksteckdose-zigbee-ls-12133-p282353.html?r=1)
- [Woox Security Remote RC7054](https://wooxhome.com/products-c10/security-c6/woox-r7054-smart-remote-control-p53)
- [Müller Licht LED Stripe 44435](https://www.amazon.de/M%C3%BCller-Licht-1800-6500K-Beleuchtung-vorprogrammierte-Lichtszenen/dp/B07ZPDPST1)

The system is designed to support the above listed devices. However, devices using the same data structure in zigbee2mqtt will also work. 

## Installation and Deployment
1. Open the  ```zigbee2mqtt-server``` folder locally on your machine.  Open the [```docker-compose.yaml```](./docker-compose.yaml) and change the device mount point if necessary. Use the following command ```ls -l /dev/serial/by-id``` to figure out which mount point the Sonoff dongle is mounted to. The USB mount point is specified in the ```devices``` section of the zigbee2mqtt container in the ```docker-compose.yaml```.

Example output for the above stated command:
```
pi@raspberry:/ $ ls -l /dev/serial/by-id
total 0
lrwxrwxrwx. 1 root root 13 Oct 19 19:26 usb-Texas_Instruments_TI_CC2531_USB_CDC___0X00124B0018ED3DDF-if00 -> ../../ttyACM0
```
In this case the correct mountpoint is /dev/ttyACM0. In the prepared docker-compose file the mount point is /dev/ttyUSB0.



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

4. Open any shell of your choice. Navigate into the ```zigbee2mqtt-server``` folder. Start the docker containers with ```docker-compose up``` (```-d``` can be used to start the containers in detached mode). 

## Pair new devices
Pairing devices to the zigbee network and adding them to the API are NOT connected. Meaning, you have to manually add the device to zigbee and then add the device to the API with the id used in the zigbee network. Click here for the instructions on how to pair devices to the API.

To add a device to the zigbee network first make sure the ```permit_join``` option is set to ```true``` in the ```configuration.yaml``` file. Otherwise the network will not allow devices to join. To perform the join, put the device into pairing mode (this highly depends on the device). The pairing mode will reset the device, delete the current connection and connect to a new available network. 
For the devices used in this projects pairing mode can be entered through following actions:
-For the motion sensors and the remote use a needle to press the reset button on the back of the devices for a few seconds. Once the devices start blinking they entered pairing mode. 
-For the LED strip turn the light on, then off and on again within 2 seconds, afterwards quicky turn it off and on again 4 times.
-For the power plugs, hold the power button until the LED in the power button starts to blink.

Be aware that in most cases the [zigbee2mqtt "supported devices" subpage] (https://www.zigbee2mqtt.io/supported-devices/) has instructions on how to pair officially supported devices (currently 2371 devices)

## Troubleshooting
1. Error related to duplicate network keys:
   This can happen if there are already zigbee networks nearby. The error can be avoided by marginally changing the ```pan_id```, ```ext_pan_id``` and ```network_key```. 
   
2. For Raspberry Pis running Raspberry OS 10 (Buster) it can be necessary to install ```libseccomp2```. Raspberry OS Buster is the oldstable version since August 14, 2021, so the recommended solution is to update to the new stable Raspberry OS version 11 (Bullseye).
