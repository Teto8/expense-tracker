   USE ExpenseTracker;

USE ExpenseTracker;
GO

INSERT INTO Categories (Name) VALUES
('Food'), ('Transport'), ('Rent'), ('Study');

INSERT INTO Expenses (CategoryId, Amount, Description, ExpenseDate) VALUES
(1, 45.50,   'Groceries',                '2026-09-03'),
(2, 120.00,  'Monthly transport ticket', '2026-09-05'),
(1, 18.90,   'Lunch',                    '2026-09-12'),
(4, 60.00,   'Textbook',                 '2026-09-20'),
(1, 32.40,   'Groceries',                '2026-09-24'),
(3, 1500.00, 'Rent',                     '2026-09-01'),
(4, 25.00,   'Printing and notebooks',   '2026-09-28'),
(3, 1500.00, 'Rent',                     '2026-10-01'),
(1, 52.30,   'Groceries',                '2026-10-04'),
(2, 120.00,  'Monthly transport ticket', '2026-10-05'),
(1, 14.50,   'Coffee and sandwich',      '2026-10-07'),
(4, 39.99,   'Online course',            '2026-10-09'),
(1, 61.20,   'Groceries',                '2026-10-11'),
(2, 8.40,    'Bus single ticket',        '2026-10-12'),
(1, 22.00,   'Dinner with friends',      '2026-10-13');