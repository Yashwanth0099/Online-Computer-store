CREATE TABLE `silver_and_above` (
  `cid` int NOT NULL,
  `creditline` float DEFAULT NULL,
  PRIMARY KEY (`cid`),
  CONSTRAINT `silver_and_above_ibfk_1` FOREIGN KEY (`cid`) REFERENCES `customer` (`CID`)
);