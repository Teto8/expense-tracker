USE ExpenseTracker;
GO

CREATE TABLE Categories (
    CategoryId INT IDENTITY(1,1) PRIMARY KEY,
    Name NVARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE Expenses (
    ExpenseId INT IDENTITY(1,1) PRIMARY KEY,
    CategoryId INT NOT NULL REFERENCES Categories(CategoryId),
    Amount DECIMAL(10,2) NOT NULL CHECK (Amount > 0),
    Description NVARCHAR(200),
    ExpenseDate DATE NOT NULL DEFAULT GETDATE()
);