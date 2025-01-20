CREATE TABLE `offer_product` (
  `PID` int NOT NULL,
  `OfferPrice` decimal(10,2) NOT NULL,
  PRIMARY KEY (`PID`),
  CONSTRAINT `offer_product_ibfk_1` FOREIGN KEY (`PID`) REFERENCES `product` (`PID`)
);