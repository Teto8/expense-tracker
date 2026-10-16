import pyodbc
from datetime import date
import csv

CONN_STR = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=ExpenseTracker;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)


def get_connection():
    return pyodbc.connect(CONN_STR)


def list_categories():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT Name FROM Categories ORDER BY Name")
        return [row.Name for row in cur.fetchall()]


def add_expense(category, amount, description, expense_date):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT CategoryId FROM Categories WHERE Name = ?", category)
        row = cur.fetchone()
        if row is None:
            print(f"Category '{category}' does not exist.")
            return
        cur.execute(
            "INSERT INTO Expenses (CategoryId, Amount, Description, ExpenseDate) "
            "VALUES (?, ?, ?, ?)",
            row.CategoryId, amount, description, expense_date,
        )
        conn.commit()
        print("Expense added.")


def monthly_report(year, month):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("EXEC dbo.usp_MonthlyReport ?, ?", year, month)
        rows = cur.fetchall()
        if not rows:
            print("No expenses for that month.")
            return
        print(f"\nSpending for {year}-{month:02d}")
        total = 0
        for r in rows:
            print(f"  {r.Category:<12} {r.Total:>10.2f}")
            total += r.Total
        print(f"  {'TOTAL':<12} {total:>10.2f}")


def recent_expenses(limit=10):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT TOP (?) e.ExpenseDate, c.Name, e.Amount, e.Description "
            "FROM Expenses e JOIN Categories c ON c.CategoryId = e.CategoryId "
            "ORDER BY e.ExpenseDate DESC, e.ExpenseId DESC",
            limit,
        )
        print("\nLatest expenses")
        for r in cur.fetchall():
            print(f"  {r.ExpenseDate}  {r.Name:<10} {r.Amount:>9.2f}  {r.Description}")

def export_report(year, month):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("EXEC dbo.usp_MonthlyReport ?, ?", year, month)
        rows = cur.fetchall()
    if not rows:
        print("No expenses for that month.")
        return
    filename = f"report_{year}_{month:02d}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Category", "Total"])
        for r in rows:
            writer.writerow([r.Category, f"{r.Total:.2f}"])
    print(f"Saved {filename}")

def main():
    while True:
        print("\n1) Add expense  2) Monthly report  3) Latest expenses  4) Export report  5) Quit")
        choice = input("Choose: ").strip()

        if choice == "1":
            print("Categories:", ", ".join(list_categories()))
            category = input("Category: ").strip()
            try:
                amount = float(input("Amount: "))
                if amount <= 0:
                    raise ValueError
            except ValueError:
                print("Amount must be a positive number.")
                continue
            description = input("Description: ").strip()
            add_expense(category, amount, description, date.today())

        elif choice == "2":
            try:
                year = int(input("Year (e.g. 2026): "))
                month = int(input("Month (1-12): "))
                if not 1 <= month <= 12:
                    raise ValueError
            except ValueError:
                print("Please enter a valid year and a month from 1 to 12.")
                continue
            monthly_report(year, month)

        elif choice == "3":
            recent_expenses()

        elif choice == "4":
            try:
                year = int(input("Year (e.g. 2026): "))
                month = int(input("Month (1-12): "))
                if not 1 <= month <= 12:
                    raise ValueError
            except ValueError:
                print("Please enter a valid year and a month from 1 to 12.")
                continue
            export_report(year, month)

        elif choice == "5":
            print("Goodbye!")
            break

        else:
            print("Please choose 1, 2, 3, 4 or 5.")


if __name__ == "__main__":
    main()