# Expense Tracker

A command-line expense tracker built with Python and SQL Server.
It stores expenses in a relational database and shows monthly
spending reports by category.

## Features
- Add expenses with a category, amount and description
- Monthly report per category with a total, using a stored procedure
- View the latest expenses
- Input validation and parameterized SQL queries

## Tech stack
- SQL Server Express
- Python 3 with pyodbc
- Git and GitHub

## Database design
Two tables: `Categories` and `Expenses`. Each expense belongs to a
category through a foreign key, and the amount must be greater than zero.

## Setup
1. Install SQL Server Express, SSMS and ODBC Driver 18 for SQL Server.
2. Create a database called `ExpenseTracker`.
3. Run the sql files in this order:
   `schema.sql`, `sample_data.sql`, `procedures.sql`
4. Install the dependency:
   `pip install -r requirements.txt`
5. The connection string in `app.py` assumes SQL Server Express at
`localhost\SQLEXPRESS` with Windows authentication. Change `CONN_STR`
if your server is different.
6. Run the app:
   `python app.py`




## What I learned
- Designing a relational schema with keys and constraints
- Writing joins, grouping queries and a stored procedure
- Connecting Python to SQL Server with pyodbc
- Using parameterized queries to prevent SQL injection
- Documenting a project on GitHub
