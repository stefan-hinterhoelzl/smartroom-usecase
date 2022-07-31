# Smartroom-API Deployment with Docker

## Important Notes
The services included in this docker container system are the following:
- fastAPI on port 8000
- grafana on port 3000
- pgadmin on port 5050

The database and mqtt subscriber are connected to the fastAPI via a bridge network. 




## Installation and Deployment
1. Open the locally cloned project and open the ```smartroom-api``` folder. Create a ```devices.json``` with an empty JSON object inside ```({})```. This file is mapped into two containers and used to maintain a list of all devices currently joined to the network.
2.  Use ```docker-compose up``` (```-d``` can be used to start in detached mode) to start the API. On the first start the database is initialized. For this reason on the first start the API itself will exit with an error code. Once the database is initialized, stop the containers again ```(Ctrl + C)``` and start again. 

## Endpoint Documentation
FastAPI provides an automatic documentation of the endpoints in the API. To view it, perform a get request on the ```/docs``` ressource. [Click here](http://localhost:8000/docs) if you are currently using the machine hosting the API to go to the documentation.

## Pair new Devices
Pairing devices to the zigbee network and adding them to the API are NOT connected. Meaning, you have to manually add the device to zigbee and the add the device to the API with the id used in the zigbee network. 

To add a device use the respective endpoint based on the device type (plug, sensor, light). By adding the device, the subscriber will start to listen for messages coming from this device and the database will be able to store and query timeseries status about the device. The endpoint for adding a device also takes the name for the device as meta data.

The ID used is the friendly name in zigbee. Per default this is the same as the unique ID. The frindly name can be changed, however be mindful about having unique names in one room! General recommendation - stick to the unique ID given by zigbee. 


## Troubleshooting



