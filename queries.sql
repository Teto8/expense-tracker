   USE ExpenseTracker;

SELECT c.Name, SUM(e.Amount) AS Total
FROM Expenses e
JOIN Categories c ON c.CategoryId = e.CategoryId
GROUP BY c.Name
ORDER BY Total DESC;

SELECT FORMAT(ExpenseDate, 'yyyy-MM') AS Month, SUM(Amount) AS Total
FROM Expenses
GROUP BY FORMAT(ExpenseDate, 'yyyy-MM')
ORDER BY Month;