# Smartroom-API deployment with Docker

## Requirements
This repository needs to be cloned to the desired server host. The host can be operated on any operating system. The host needs to have docker and docker-compose installed. 

## Important Notes
The services included in this docker container system are the following. The stated ports are preconfigured and can be changed in the docker configurations. 

#### fastAPI on port 8001
The fastAPI container starts the core python API in this system. The API communicates with the zigbee network through the [```publisher.py```](./api/publisher.py) file. Files related to the API are stored in the [```api```](./api/) subfolder. The API itself is in the [```main.py```](./api/main.py) file. Endpoints can directly be added in there. The [```fastAPI_models.py```](./api/fastAPI_models.py) file can be used to define structures for objects to map received JSON structures to python dictionaries. The [```schema.py```](./api/schema.py) needs to contain the database structure. In case the database is extended with tables for more devices, they need to be added in this file addtionally to the database initialization sql file. The [```session.py```](./api/session.py) and [```config.py```](./api/config.py) contain configurations and connection strings. It is highly recommended to work with the predefined configuration there, however, in case the container name/port/database user/database name/database password are changed the changes also need to be propagated to the config files here. Devices currently added to the API are stored in the ```devices.json```. This file is in the smartroom-api root folder, since the api as well as the subscriber are accessing it. 

#### timescaledb on port 5432
The timescale database is started in its own docker container. In the ```environment``` of the [```docker-compose.yaml```](./docker-compose.yml)  the userdata can be changed (username, database name, password). However, as stated above. It is recommended to stick to the default configuartion here. In the subfolder [```database```](./database/) the [```Database_Schema.sql```](./database/Database_Schema.sql) file defines the sql script that is run on the first startup of the container. If the container already contains a database, the initialization is skipped. If the system is extended, this sql script needs to be also extended with the necessary tables. Please note the syntax to create hypertables and indices, which enable time series queries on the data. The database is connected to the other containers via a bridge network. The host of the database therefore is the container name (timeScaledb). Docker maps the container name to the given IP. 

#### grafana on port 3001
Grafana can be used to visualize data on the database. Grafana is connected to the timescale database.

#### pgadmin on port 5051
PGadmin can be used to manually read or write from/to the database without using the API. This is very helpful, especially during developement. The email and password for pgadmin can be configured in the [```docker-compose.yaml```](./docker-compose.yml).

#### subscriber no exposed port
The mqtt-subscriber is running in it's own container. The subscriber listens to the mqtt network created by the zigbee2mqtt-server. If a message from a device listed in the ```devices.json``` is received it contains operational data for this device. The subscriber stores this data through an endpoint on the API. For this reason, both the subscriber and the API need to have access to the ```devices.json``` in the ```smartroom-api``` root folder. One exception is the remote, which does not exist on API level. Meaning the remote needs to be added to the ```devices.json``` manually. The [```subscriber.py```](./subscriber/subscriber.py) file defines actions for the four buttons on the remote. Respective API calls are triggered. 


## Installation and Deployment
1. Open the locally cloned project and open the ```smartroom-api``` folder. Create a ```devices.json``` with an empty JSON object inside ```({})``` in this folder. This file is mapped into two containers and used to maintain a list of all devices currently joined to the network.
2.  Open any shell of your choice. Navigate into the ```smartroom-api``` folder. Use the command ```docker-compose up``` (```-d``` can be used to start in detached mode) to start the docker system. During the first start the database is initialized. For this reason, on the first startup the API container itself will exit with an error code. Although the [```docker-compose.yaml```](./docker-compose.yml) specifies that the API is depending on the database, the system does not recognize the database initialization and will start the API once the database container has started. Once the database is initialized, stop the containers again ```(Ctrl + C)``` and start again. Then everything should start in the right order and run without problems.

## Endpoint Documentation
FastAPI provides an automatic documentation of the endpoints in the API via [swagger](https://swagger.io/). To view it, perform a get request on the ```/docs``` ressource, prefearably by opening the resource via a web browser.  [Click here](http://localhost:8000/docs) if you are currently using the machine hosting the API to go to the documentation.

## Pair new Devices
Pairing devices to the zigbee network and adding them to the API are NOT connected. Meaning, you have to manually add the device to zigbee and then add the device to the API with the id used in the zigbee network. 

To add a device use the respective endpoint based on the device type (plug, sensor, light). By adding the device, the subscriber will start to listen for messages coming from this device, the device can be controlled via the API and the database will be able to store and query timeseries status data about the device. The endpoint for adding a device also takes the name for the device as meta data.

The ID used is the friendly name in zigbee. Per default this is the same as the unique ID. The frindly name can be changed in the ```configuration.yaml``` of the [zigbee server](https://github.com/stefan-hinterhoelzl/smartroom-usecase/tree/master/zigbee2mqtt-server), however be mindful about having unique names! Moreover, as of this time the API does not support changing the ID after initial adding. General recommendation - stick to the unique ID given by zigbee. 

## Usecase Running Example
This section shows a running example of pairing a device in the API and reading data through the api and with pgadmin. 
At this point it is assumed that the device has already been paired to the zigbee network as stated in the documentation of the [zigbee2mqtt-server](https://github.com/stefan-hinterhoelzl/smartroom-usecase/tree/master/zigbee2mqtt-server).


![Layer Graphic](/assets/images/Architektur.png)


#### Pairing the device to the API
1. The device needs to be associated to a specific room. The device is addressed via the room. Therefore, before adding a device, we need to create a room on the post endpoint ```/Rooms```. 

![Post Room](/assets/images/create_room.png)

2. A device can now be added to an existing room. If the ```room_id``` used is not found the endpoint returns an error. For this running example it is assumed that a light is added to the API. The post endpoint for this operation is ```/Rooms/{room_id}/Lights```. The ```light_id``` provided to this endpoint needs to match the friendly name used in the zigbee network. 

![Post Light](/assets/images/create_light.png)
#### Requesting State data
Devices paired to the zigbee network send data about their current state. This happens either on first joining the network, after a change was made to their state or when requested by the zigbee2mqtt server. The light for example transmit an updated state event every time it is toggled or the color/brightness change. An update can be requested by sending a message to the topic ```zigbee2mqtt/{friendly_name_of_the_device}/get```. The post endpoint ```/Rooms/{room_id}/Lights/{light_id}/ManualSavestate``` essentially does exactly that. The API store every state update of any device paired to the API, no matter how the state transmit was triggered. 

![Manual Savestate](/assets/images/manual_savestate.png)
#### Reading data through the API (interval and from-to in UNIX timestamps)
Operational data of devices stored in the database can be queried with the post! endpoint ```/Rooms/{room_id}/Lights/{light_id}/GetOperations```. Althoug this is a get request in nature, a body is required for this request, therefore it needs to be done via a post request. The JSON body has three arguments: ```interval```, ```timespan_from```, ```timespan_to```. The interval is represented by days. The integer states how many days back operationl data should be returned. The timespan arguments are connected. They represent UNIX timestamps. Operational Data between those timespans is returned. If all arguments are set to ```0```, all data for the specfic device is returned. If one time constraint is filled, the other one needs to be ```0```. Setting both will result in a error from the API. 

![Get Operation](/assets/images/get_operations.png)
#### Reading data in pgadmin
1. Pgadmin is per default available in the browser on the host's IP on port 5051. When accessing admin for the first time the database connection needs to be configured. This is done by clicking on ```Add New Server``` in the quick links section. 

![PG Admin 1](/assets/images/pgadmin_1.png)

2. The connection uses the configuration from the [```docker-compose.yaml```](./docker-compose.yml) file. As Hostname the container name of the timescale database is entered. 

![PG Admin 1](/assets/images/pgadmin_2.png)

3. On the left hand side in the menu the tables can be found as shown in the figure below. Through this interface data can be added, deleted, modified or simply read. 

![PG Admin 1](/assets/images/pgadmin_3.png)
#### Deleting device from the API
Data from the API can be deleted with the respective endpoint. For lights the delete request is ```Rooms/{room_id}/Lights/{light_id```. The API performs a casacding delete, meaning once a light is removed all the operational data for the light is removed. The same is true for rooms. If a room is deleted, all the devices and corresponding operational data is deleted. 

![PG Admin 1](/assets/images/delete_light.png)



