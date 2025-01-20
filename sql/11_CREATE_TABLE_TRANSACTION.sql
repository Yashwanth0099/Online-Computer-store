CREATE TABLE `transaction` (
  `bid` int NOT NULL AUTO_INCREMENT,
  `CCNumber` varchar(16) NOT NULL,
  `CID` int NOT NULL,
  `SAName` varchar(100) NOT NULL,
  `TDate` datetime NOT NULL,
  `TTag` varchar(10) NOT NULL,
  PRIMARY KEY (`bid`,`CID`,`CCNumber`,`SAName`),
  KEY `CCNumber` (`CCNumber`),
  KEY `CID` (`CID`),
  KEY `SAName` (`SAName`,`CID`),
  CONSTRAINT `fk_bid_basket` FOREIGN KEY (`bid`) REFERENCES `basket` (`BID`),
  CONSTRAINT `transaction_ibfk_1` FOREIGN KEY (`CCNumber`) REFERENCES `credit_card` (`CCNumber`),
  CONSTRAINT `transaction_ibfk_2` FOREIGN KEY (`CID`) REFERENCES `customer` (`CID`),
  CONSTRAINT `transaction_ibfk_3` FOREIGN KEY (`SAName`, `CID`) REFERENCES `shipping_address` (`SAName`, `CID`)
);