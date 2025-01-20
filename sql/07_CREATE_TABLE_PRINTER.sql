CREATE TABLE `printer` (
  `PID` int NOT NULL,
  `PrinterType` varchar(100) NOT NULL,
  `Resolution` varchar(100) NOT NULL,
  PRIMARY KEY (`PID`),
  CONSTRAINT `printer_ibfk_1` FOREIGN KEY (`PID`) REFERENCES `product` (`PID`)
);