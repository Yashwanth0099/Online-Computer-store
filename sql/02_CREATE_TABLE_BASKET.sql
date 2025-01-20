CREATE TABLE `basket` (
  `CID` int NOT NULL,
  `BID` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`BID`),
  KEY `CID` (`CID`),
  CONSTRAINT `basket_ibfk_1` FOREIGN KEY (`CID`) REFERENCES `customer` (`CID`)
);