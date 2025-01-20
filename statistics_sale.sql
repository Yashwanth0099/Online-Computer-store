/*Compute the total amount charged per credit card. */
SELECT CCNumber, ROUND(SUM(pricesold * quantity),2) AS TotalCharged
FROM TRANSACTION
JOIN BASKET ON TRANSACTION.BID = BASKET.BID
JOIN APPEARS_IN ON BASKET.BID = APPEARS_IN.BID
GROUP BY CCNumber;


/*Compute the 10 best customers (in terms of money spent) in descending order.*/
SELECT CUSTOMER.CID, CUSTOMER.FName, CUSTOMER.LName, ROUND(SUM(pricesold * quantity),2) AS MoneySpent
FROM CUSTOMER
JOIN TRANSACTION ON CUSTOMER.CID = TRANSACTION.CID
JOIN APPEARS_IN ON TRANSACTION.BID = APPEARS_IN.BID
GROUP BY CUSTOMER.CID
ORDER BY MoneySpent DESC
LIMIT 10;

/*For a given time period (begin date and end date) compute the most frequently sold products.*/

SELECT APPEARS_IN.PID, PName, COUNT(*) AS TimesSold
FROM APPEARS_IN
JOIN PRODUCT ON APPEARS_IN.PID = PRODUCT.PID
JOIN TRANSACTION ON APPEARS_IN.BID = TRANSACTION.BID
WHERE TDate BETWEEN '2023-12-10' AND '2023-12-14' 
GROUP BY PID
ORDER BY TimesSold DESC
LIMIT 1;

/*For a given time period (begin date and end date) compute the products which are sold to the highest number of distinct customers.*/
SELECT PRODUCT.PID, PRODUCT.PName, COUNT(DISTINCT TRANSACTION.CID) AS DistinctCustomers
FROM PRODUCT
JOIN APPEARS_IN ON PRODUCT.PID = APPEARS_IN.PID
JOIN TRANSACTION ON APPEARS_IN.BID = TRANSACTION.BID
WHERE TDate BETWEEN '2023-12-10' AND '2023-12-14' 
GROUP BY PRODUCT.PID
ORDER BY DistinctCustomers DESC
LIMIT 10;

/*For a given time period (begin date and end date) compute the maximum basket total amount per credit card.*/
SELECT CCNumber, ROUND(MAX(TotalAmount),2) AS MaxBasketTotal
FROM (
    SELECT TRANSACTION.CCNumber, TRANSACTION.BID, SUM(APPEARS_IN.pricesold * APPEARS_IN.quantity) AS TotalAmount
    FROM TRANSACTION
    JOIN APPEARS_IN ON TRANSACTION.BID = APPEARS_IN.BID
    WHERE TDate BETWEEN '2023-12-10' AND '2023-12-14' 
    GROUP BY TRANSACTION.CCNumber, TRANSACTION.BID
) AS BasketTotals
GROUP BY CCNumber;

/*For a given time period (begin date and end date) compute the average selling product price per product type (desktop, laptop and printer).*/
SELECT PRODUCT.PType, ROUND(AVG(pricesold),2) AS AvgPrice
FROM PRODUCT
JOIN APPEARS_IN ON PRODUCT.PID = APPEARS_IN.PID
JOIN TRANSACTION ON APPEARS_IN.BID = TRANSACTION.BID
WHERE TDate BETWEEN '2023-12-10' AND '2023-12-14' 
GROUP BY PRODUCT.PType;
