# Smartroom-API deployment with Docker

## Requirements
This repository needs to be cloned to the desired server host. The host can be operated on any operating system. The host needs to have docker and docker-compose installed. 

## Important Notes
The services included in this docker container system are the following. The stated ports are preconfigured and can be changed in the docker configurations. 

#### fastAPI on port 8000
The fastAPI container starts the core python API in this system. The API communicates with the zigbee network through the [```publisher.py```}(/api/publisher.py) file. Files related to the API are stored in the ```api``` subfolder. The API itself is in the ```main.py``` file. Endpoints can directly be added in there. The ```fastAPI_models``` file can be used to define structures for objects to map received JSON structures to python dictionaries. The ```schema.py``` needs to contain the database structure. In case the database is extended with tables for more devices, they need to be added in this file addtionally to the database initialization sql file. The ```session.py``` and ```config.py``` contain configurations and connection strings. It is highly recommended to work with the predefined configuration there, however, in case the container name/port/database user/database name/database password are changed the changes also need to be propagated to the config files here. Devices currently added to the API are stored in the ```devices.json```. This file is in the root folder, since the api as well as the subscriber are accessing it. 

#### timescaledb on port 5432
The timescale database is started in its own docker container. In the ```environment``` of the ```docker-compose.yaml```  the userdata can be changed (username, database name, password). However, as stated above. It is recommended to stick to the default configuartion here. In the subfolder ```database``` the ```Database_Schema.sql``` file defines the sql script that is run on the first startup of the container. If the container already contains a database, the initialization is skipped. If the system is extended, this sql script needs to be also extended with the necessary tables. Please note the syntax to create hypertables and indices, which enable time series queries on the data. The database is connected to the other containers via a bridge network. The host of the database therefore is the container name (timeScaledb). Docker maps the container name to the given IP. 

#### grafana on port 3000
Grafana can be used to visualize data on the database. Grafana is connected to the timescale database.

#### pgadmin on port 5050
PGadmin can be used to manually read or write from/to the database without using the API. This is very helpful, especially during developement.

#### subscriber no exposed port
The subscriber is running in a standalone container. The subscriber listens to the mqtt network created by the zigbee2mqtt-server. If a message from a device listed in the ```devices.json``` is received it contains operational data for this device. The subscriber stores this data through an endpoint on the API. For this reason, both the subscriber and the API need to have access to the ```devices.json``` in the ```smartroom-api``` root folder. One exception is the remote, which does not exist on API level. Meaning the remote needs to be added to the ```devices.json``` manually. The ```subscriber.py``` file defines actions for the four buttons on the remote. Respective API calls are triggered. 


## Installation and Deployment
1. Open the locally cloned project and open the ```smartroom-api``` folder. Create a ```devices.json``` with an empty JSON object inside ```({})``` in this folder. This file is mapped into two containers and used to maintain a list of all devices currently joined to the network.
2.  Open any shell of your choice. Navigate into the ```smartroom-api``` folder. Use the command ```docker-compose up``` (```-d``` can be used to start in detached mode) to start the docker system. During the first start the database is initialized. For this reason, on the first startup the API container itself will exit with an error code. Although the ```docker-compose.yaml``` specifies that the API is depending on the database, the system does not recognize the database initialization and will start the API once the database container has started. Once the database is initialized, stop the containers again ```(Ctrl + C)``` and start again. Then everything should start in the right order and run without problems.

## Endpoint Documentation
FastAPI provides an automatic documentation of the endpoints in the API via [swagger](https://swagger.io/). To view it, perform a get request on the ```/docs``` ressource, prefearably by opening the resource via a web browser.  [Click here](http://localhost:8000/docs) if you are currently using the machine hosting the API to go to the documentation.

## Pair new Devices
Pairing devices to the zigbee network and adding them to the API are NOT connected. Meaning, you have to manually add the device to zigbee and then add the device to the API with the id used in the zigbee network. 

To add a device use the respective endpoint based on the device type (plug, sensor, light). By adding the device, the subscriber will start to listen for messages coming from this device, the device can be controlled via the API and the database will be able to store and query timeseries status data about the device. The endpoint for adding a device also takes the name for the device as meta data.

The ID used is the friendly name in zigbee. Per default this is the same as the unique ID. The frindly name can be changed in the ```configuration.yaml``` of the [zigbee server](https://github.com/stefan-hinterhoelzl/smartroom-usecase/tree/master/zigbee2mqtt-server), however be mindful about having unique names! Moreover, as of this time the API does not support changing the ID after initial adding. General recommendation - stick to the unique ID given by zigbee. 





