CREATE TABLE `appears_in` (
  `BID` int NOT NULL,
  `PID` int NOT NULL,
  `Quantity` int NOT NULL,
  `pricesold` float DEFAULT NULL,
  PRIMARY KEY (`PID`,`BID`),
  KEY `appears_in_ibfk_1` (`BID`),
  CONSTRAINT `appears_in_ibfk_1` FOREIGN KEY (`BID`) REFERENCES `basket` (`BID`),
  CONSTRAINT `appears_in_ibfk_2` FOREIGN KEY (`PID`) REFERENCES `product` (`PID`)
);