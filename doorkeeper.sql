CREATE TABLE log (
  tokenID varchar(32) NOT NULL,
  answere varchar(1) NOT NULL ,
  timecode timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE token (
  tID varchar(32) NOT NULL,
  userID int(11) NOT NULL,
  tKey varchar(32) NOT NULL,
  tActive int(1) NOT NULL DEFAULT '1'
);

CREATE TABLE users (
  uID int(11) NOT NULL,
  uName varchar(35) NOT NULL,
  uPass varchar(32) NOT NULL,
  uSalt varchar(75) NOT NULL,
  session varchar(32) NOT NULL,
  uActive enum('false','true') NOT NULL DEFAULT 'true',
  expire timestamp NOT NULL DEFAULT '0000-00-00 00:00:00'
);