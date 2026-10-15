USE ExpenseTracker;
GO

CREATE PROCEDURE dbo.usp_MonthlyReport
    @Year INT,
    @Month INT
AS
BEGIN
    SELECT c.Name AS Category, SUM(e.Amount) AS Total
    FROM Expenses e
    JOIN Categories c ON c.CategoryId = e.CategoryId
    WHERE YEAR(e.ExpenseDate) = @Year
      AND MONTH(e.ExpenseDate) = @Month
    GROUP BY c.Name
    ORDER BY Total DESC;
END;
GO