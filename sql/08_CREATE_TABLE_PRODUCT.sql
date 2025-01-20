CREATE TABLE `product` (
  `PID` int NOT NULL AUTO_INCREMENT,
  `PType` varchar(50) NOT NULL,
  `PName` varchar(100) NOT NULL,
  `pprice` float DEFAULT NULL,
  `Description` text,
  `PQuantity` int NOT NULL DEFAULT '0',
  `image` text,
  PRIMARY KEY (`PID`),
  UNIQUE KEY `unique_PName` (`PName`)
);