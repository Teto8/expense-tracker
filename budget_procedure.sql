USE ExpenseTracker;
GO

CREATE PROCEDURE dbo.usp_BudgetReport
    @Year INT,
    @Month INT
AS
BEGIN
    SELECT c.Name AS Category,
           b.MonthlyLimit,
           ISNULL(SUM(e.Amount), 0) AS Spent,
           b.MonthlyLimit - ISNULL(SUM(e.Amount), 0) AS Remaining
    FROM Budgets b
    JOIN Categories c ON c.CategoryId = b.CategoryId
    LEFT JOIN Expenses e
           ON e.CategoryId = b.CategoryId
          AND YEAR(e.ExpenseDate) = @Year
          AND MONTH(e.ExpenseDate) = @Month
    GROUP BY c.Name, b.MonthlyLimit
    ORDER BY c.Name;
END;
GO

