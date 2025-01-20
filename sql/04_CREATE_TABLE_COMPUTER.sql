CREATE TABLE `computer` (
  `PID` int NOT NULL,
  `CPUType` varchar(100) NOT NULL,
  PRIMARY KEY (`PID`),
  CONSTRAINT `computer_ibfk_1` FOREIGN KEY (`PID`) REFERENCES `product` (`PID`)
);