CREATE TABLE `customer` (
  `CID` int NOT NULL AUTO_INCREMENT,
  `FName` varchar(100) NOT NULL,
  `LName` varchar(100) NOT NULL,
  `EMail` varchar(100) NOT NULL,
  `Address` varchar(255) NOT NULL,
  `Phone` varchar(20) NOT NULL,
  `Status` varchar(10) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`CID`)
);