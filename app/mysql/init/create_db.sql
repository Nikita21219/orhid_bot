CREATE DATABASE IF NOT EXISTS orhid_bot;

USE orhid_bot;

CREATE TABLE IF NOT EXISTS Users
(
	id INT PRIMARY KEY AUTO_INCREMENT,
	tg_user_id VARCHAR(255) UNIQUE,
    state VARCHAR(30),
    doctor_id INT,
    date VARCHAR(255),
    time VARCHAR(255),
    phone_number VARCHAR(255),
    full_name VARCHAR(255),
    client_id INT
);
