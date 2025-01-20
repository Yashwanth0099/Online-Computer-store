CREATE TABLE `credit_card` (
  `CCNumber` varchar(16) NOT NULL,
  `SecNumber` varchar(3) NOT NULL,
  `OwnerName` varchar(100) NOT NULL,
  `CCType` varchar(10) NOT NULL,
  `BilAddress` varchar(255) NOT NULL,
  `ExpDate` varchar(20) DEFAULT NULL,
  `StoredCardCID` int DEFAULT NULL,
  PRIMARY KEY (`CCNumber`),
  KEY `StoredCardCID` (`StoredCardCID`),
  CONSTRAINT `credit_card_ibfk_1` FOREIGN KEY (`StoredCardCID`) REFERENCES `customer` (`CID`)
);