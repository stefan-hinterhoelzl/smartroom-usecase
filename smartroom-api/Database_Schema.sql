CREATE TABLE Room(
	room_Id varchar PRIMARY KEY NOT NULL,
	room_Size int NOT NULL,
	measurement_Unit varchar NOT NULL
);
				 
CREATE TABLE Doors(
	door_id varchar PRIMARY KEY NOT NULL,
	room_id varchar NOT NULL,
	door_lock bool  NOT NULL,
	connectsdoor varchar NOT NULL,
	time timestamp NOT NULL,
	FOREIGN KEY (room_id)
      REFERENCES Room (room_id)
);	
CREATE TABLE RoomToDoorRelations(
	room_id varchar NOT NULL,
	door_id varchar NOT NULL,
	PRIMARY KEY(room_id, door_id),
	FOREIGN KEY(room_id)
      REFERENCES Room (room_id),
	FOREIGN KEY(door_id)
      REFERENCES Doors(door_id)
);

CREATE TABLE AirQualityProperties(
	room_Id varchar  NOT NULL,
	ventilator varchar NOT NULL,
	totalNumberOfPeople int NOT NULL,
	co2 float NOT NULL,
	co2MeasurementUnit varchar NOT NULL,
	temperature float NOT NULL,
	temperatureMeasurementUnit varchar NOT NULL,
	humidity float NOT NULL,
	humidityMeasurementUnit varchar NOT NULL,
	time timestamp PRIMARY KEY NOT NULL,
	FOREIGN KEY (room_Id) REFERENCES Room (room_Id)
);


				 
CREATE TABLE Lights(
	room_id varchar NOT NULL,
	light_id varchar NOT NULL,
	turnOn bool NOT NULL,
	energyConsumption int  NOT NULL,
	energyConsumptionUnit varchar NOT NULL,
	time timestamp PRIMARY KEY NOT NULL,
	FOREIGN KEY (room_id)
    REFERENCES Room (room_id)
);
CREATE TABLE Windows(
	room_id varchar NOT NULL,
	window_id varchar NOT NULL,
	isOpen bool NOT NULL,
	time timestamp PRIMARY KEY NOT NULL,
	FOREIGN KEY (room_id)
      REFERENCES Room (room_id)
);	
CREATE TABLE Ventilators(
	room_id varchar NOT NULL,
	ventilator_id varchar NOT NULL,
	turnOn bool  NOT NULL,
	time timestamp PRIMARY KEY NOT NULL,
	FOREIGN KEY (room_id)
      REFERENCES Room (room_id)
);	