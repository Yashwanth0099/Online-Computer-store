CREATE TABLE `shipping_address` (
  `CID` int NOT NULL,
  `SAName` varchar(100) NOT NULL,
  `RecepientName` varchar(100) NOT NULL,
  `Street` varchar(255) NOT NULL,
  `SNumber` varchar(10) NOT NULL,
  `City` varchar(100) NOT NULL,
  `Zip` varchar(10) NOT NULL,
  `state` varchar(20) DEFAULT NULL,
  `Country` varchar(100) NOT NULL,
  PRIMARY KEY (`CID`,`SAName`),
  KEY `transaction_ibfk_3` (`SAName`,`CID`),
  CONSTRAINT `shipping_address_ibfk_1` FOREIGN KEY (`CID`) REFERENCES `customer` (`CID`)
);