CREATE TABLE `laptop` (
  `PID` int NOT NULL,
  `BType` varchar(100) NOT NULL,
  `Weight` decimal(10,2) NOT NULL,
  PRIMARY KEY (`PID`),
  CONSTRAINT `fk_laptop_pid` FOREIGN KEY (`PID`) REFERENCES `product` (`PID`)
);