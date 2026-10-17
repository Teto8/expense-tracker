USE ExpenseTracker;
GO

CREATE TABLE Budgets (
    BudgetId INT IDENTITY(1,1) PRIMARY KEY,
    CategoryId INT NOT NULL UNIQUE REFERENCES Categories(CategoryId),
    MonthlyLimit DECIMAL(10,2) NOT NULL CHECK (MonthlyLimit > 0)
);
GO

INSERT INTO Budgets (CategoryId, MonthlyLimit)
SELECT CategoryId, 400  FROM Categories WHERE Name = 'Food';
INSERT INTO Budgets (CategoryId, MonthlyLimit)
SELECT CategoryId, 150  FROM Categories WHERE Name = 'Transport';
INSERT INTO Budgets (CategoryId, MonthlyLimit)
SELECT CategoryId, 1500 FROM Categories WHERE Name = 'Rent';
INSERT INTO Budgets (CategoryId, MonthlyLimit)
SELECT CategoryId, 100  FROM Categories WHERE Name = 'Study';
GO