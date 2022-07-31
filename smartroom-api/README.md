# Smartroom-API Deployment with Docker

## Important Notes



## Installation and Deployment
1. Open the locally cloned project and open the ```smartroom-api``` folder. Create a ```devices.json``` with an empty JSON object inside ```({})```. This file is mapped into two containers and used to maintain a list of all devices currently joined to the network.
2.  Use ```docker-compose up``` (```-d``` can be used to start in detached mode) to start the API. On the first start the database is initialized. For this reason on the first start the API itself will exit with an error code. Once the database is initialized, stop the containers again ```(Ctrl + C)``` and start again. 

##Endpoint documentation
FastAPI provides an automatic documentation of the endpoints in the API. To view it, perform a get request on the ```/docs``` ressource. [Click here](localhost:8000/docs) if you are currently using the machine hosting the API to go to the documentation.

## Pair new devices

## Troubleshooting



