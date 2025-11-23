CREATE DATABASE emergency_db;

USE emergency_db;

CREATE TABLE patients(
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    hr INT,
    bp INT,
    oxygen INT,
    temp FLOAT,
    priority VARCHAR(20)
);
