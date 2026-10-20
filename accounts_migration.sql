USE ExpenseTracker;
GO

CREATE TABLE Users (
    UserId INT IDENTITY(1,1) PRIMARY KEY,
    Email NVARCHAR(255) NOT NULL UNIQUE,
    PasswordHash NVARCHAR(255) NOT NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

ALTER TABLE Expenses ADD UserId INT NULL REFERENCES Users(UserId);
GO

DROP TABLE Budgets;
GO

CREATE TABLE Budgets (
    BudgetId INT IDENTITY(1,1) PRIMARY KEY,
    UserId INT NOT NULL REFERENCES Users(UserId),
    CategoryId INT NOT NULL REFERENCES Categories(CategoryId),
    MonthlyLimit DECIMAL(10,2) NOT NULL CHECK (MonthlyLimit > 0),
    CONSTRAINT UQ_Budgets_User_Category UNIQUE (UserId, CategoryId)
);
GO

ALTER PROCEDURE dbo.usp_MonthlyReport
    @Year INT,
    @Month INT,
    @UserId INT = NULL
AS
BEGIN
    SELECT c.Name AS Category, SUM(e.Amount) AS Total
    FROM Expenses e
    JOIN Categories c ON c.CategoryId = e.CategoryId
    WHERE YEAR(e.ExpenseDate) = @Year
      AND MONTH(e.ExpenseDate) = @Month
      AND (@UserId IS NULL OR e.UserId = @UserId)
    GROUP BY c.Name
    ORDER BY Total DESC;
END;
GO

ALTER PROCEDURE dbo.usp_BudgetReport
    @Year INT,
    @Month INT,
    @UserId INT
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
          AND e.UserId = b.UserId
          AND YEAR(e.ExpenseDate) = @Year
          AND MONTH(e.ExpenseDate) = @Month
    WHERE b.UserId = @UserId
    GROUP BY c.Name, b.MonthlyLimit
    ORDER BY c.Name;
END;
GO