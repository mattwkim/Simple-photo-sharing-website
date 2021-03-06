CREATE TABLE User (username VARCHAR(20) NOT NULL, firstname VARCHAR(20), lastname VARCHAR(20), password VARCHAR(20), email VARCHAR(40), PRIMARY KEY (username));

CREATE TABLE Album (albumid INT NOT NULL AUTO_INCREMENT, title VARCHAR(50), created TIMESTAMP DEFAULT CURRENT_TIMESTAMP, lastupdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP, username VARCHAR(20), PRIMARY KEY (albumid));

CREATE TABLE Contain (sequencenum INTEGER DEFAULT '0', albumid INT NOT NULL, picid VARCHAR(40), caption VARCHAR(255), PRIMARY KEY(sequencenum));

CREATE TABLE Photo(picid VARCHAR(40) NOT NULL, format CHAR(3), date TIMESTAMP, PRIMARY KEY(picid));
