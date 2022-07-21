CREATE TABLE Room(
	room_Id varchar PRIMARY KEY NOT NULL,
	room_Size int NOT NULL,
	room_Name varchar NOT NULL
);
				 		 
CREATE TABLE Lights(
	room_id varchar NOT NULL,
	light_id varchar NOT NULL,
	turnOn bool NOT NULL,
	name varchar NOT NULL,
	color_x float NOT NULL,
	color_y float NOT NULL,
	time timestamp NOT NULL,
	PRIMARY KEY (room_id, light_id),
	FOREIGN KEY (room_id)
    REFERENCES Room (room_id)
);

CREATE TABLE Motion_Sensors(
    room_Id varchar NOT NULL,
	sensor_Id varchar NOT NULL,
	name varchar NOT NULL,
	is_active boolean NOT NULL,
	time timestamp NOT NULL,
	PRIMARY KEY (room_id, sensor_Id),
	FOREIGN KEY (room_id),
	REFERENCES Room (room_id)
);

CREATE TABLE Power_Plug(
	room_Id varchar NOT NULL,
	plug_Id varchar NOT NULL,
	name varchar NOT NULL,
	is_active boolean NOT NULL,
	time timestamp NOT NULL,
	PRIMARY KEY (room_Id, plug_Id),
	FOREIGN KEY (room_Id),
	REFERENCES Room (room_Id)
);
