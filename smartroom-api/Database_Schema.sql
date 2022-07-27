CREATE TABLE Room(
	room_Id varchar PRIMARY KEY NOT NULL,
	room_Size int NOT NULL,
	room_Name varchar NOT NULL
);
				 		 
CREATE TABLE Light(
	room_id varchar NOT NULL,
	light_id varchar NOT NULL,
	name varchar NOT NULL,
	PRIMARY KEY (room_id, light_id),
	FOREIGN KEY (room_id) REFERENCES Room (room_id)
);

CREATE TABLE Light_Operation(
	light_id varchar NOT NULL,
	room_id varchar NOT NULL,
	time timestamp NOT NULL,
	turnon BOOLEAN NOT NULL,
	color_x DECIMAL NOT NULL,
	color_y DECIMAL NOT NULL,
	brightness INTEGER NOT NULL,
	PRIMARY KEY (light_id, time),
	FOREIGN KEY (room_id, light_id) REFERENCES Light (room_id, light_id)
);

SELECT create_hypertable('Light_Operation', 'time');
CREATE INDEX ix_light_id_room_id_time ON Light_Operation (light_id, room_id, time DESC);

CREATE TABLE Motion_Sensors(
    room_Id varchar NOT NULL,
	sensor_Id varchar NOT NULL,
	name varchar NOT NULL,
	is_active boolean NOT NULL,
	time timestamp NOT NULL,
	PRIMARY KEY (room_id, sensor_Id),
	FOREIGN KEY (room_id) REFERENCES Room (room_id)
);

CREATE TABLE Power_Plug(
	room_Id varchar NOT NULL,
	plug_Id varchar NOT NULL,
	name varchar NOT NULL,
	is_active boolean NOT NULL,
	time timestamp NOT NULL,
	PRIMARY KEY (room_Id, plug_Id),
	FOREIGN KEY (room_Id) REFERENCES Room (room_Id)
);
