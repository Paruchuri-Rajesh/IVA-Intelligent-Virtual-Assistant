CREATE DATABASE Alarms;

USE Alarms;

CREATE TABLE Alarm(
time TIME,
AmPm VARCHAR(2),
name VARCHAR(50),
Status VARCHAR(50) default "ON",
PRIMARY KEY (time,AmPm)
);

insert into Alarm values("07:30","AM","Morning walk","OFF");

Create Table Reminders(
time TIME primary key,
AmPm VARCHAR(2),
Matter varchar(60),
status varchar(50)
);




select * from Alarm;
select * from Reminders;



