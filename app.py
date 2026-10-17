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
            "SELECT TOP (?) e.ExpenseId, e.ExpenseDate, c.Name, e.Amount, e.Description "
            "FROM Expenses e JOIN Categories c ON c.CategoryId = e.CategoryId "
            "ORDER BY e.ExpenseDate DESC, e.ExpenseId DESC",
            limit,
        )
        print("\nLatest expenses")
        for r in cur.fetchall():
            print(f"  #{r.ExpenseId:<4} {r.ExpenseDate}  {r.Name:<10} {r.Amount:>9.2f}  {r.Description}")

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

def edit_expense(expense_id):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT c.Name, e.Amount, e.Description, e.ExpenseDate "
            "FROM Expenses e JOIN Categories c ON c.CategoryId = e.CategoryId "
            "WHERE e.ExpenseId = ?",
            expense_id,
        )
        row = cur.fetchone()
        if row is None:
            print("No expense with that ID.")
            return

        print("Press Enter to keep the current value.")

        category = input(f"Category [{row.Name}]: ").strip() or row.Name
        cur.execute("SELECT CategoryId FROM Categories WHERE Name = ?", category)
        cat_row = cur.fetchone()
        if cat_row is None:
            print(f"Category '{category}' does not exist.")
            return

        amount_text = input(f"Amount [{row.Amount}]: ").strip()
        if amount_text:
            try:
                amount = float(amount_text)
                if amount <= 0:
                    raise ValueError
            except ValueError:
                print("Amount must be a positive number.")
                return
        else:
            amount = row.Amount

        description = input(f"Description [{row.Description}]: ").strip() or row.Description

        date_text = input(f"Date YYYY-MM-DD [{row.ExpenseDate}]: ").strip()
        if date_text:
            try:
                expense_date = date.fromisoformat(date_text)
            except ValueError:
                print("Date must look like 2026-10-15.")
                return
        else:
            expense_date = row.ExpenseDate

        cur.execute(
            "UPDATE Expenses SET CategoryId = ?, Amount = ?, Description = ?, ExpenseDate = ? "
            "WHERE ExpenseId = ?",
            cat_row.CategoryId, amount, description, expense_date, expense_id,
        )
        conn.commit()
        print("Expense updated.")


def delete_expense(expense_id):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT e.ExpenseDate, c.Name, e.Amount, e.Description "
            "FROM Expenses e JOIN Categories c ON c.CategoryId = e.CategoryId "
            "WHERE e.ExpenseId = ?",
            expense_id,
        )
        row = cur.fetchone()
        if row is None:
            print("No expense with that ID.")
            return
        print(f"{row.ExpenseDate}  {row.Name}  {row.Amount:.2f}  {row.Description}")
        answer = input("Delete this expense? (yes/no): ").strip().lower()
        if answer != "yes":
            print("Cancelled.")
            return
        cur.execute("DELETE FROM Expenses WHERE ExpenseId = ?", expense_id)
        conn.commit()
        print("Expense deleted.")


def ask_expense_id():
    try:
        return int(input("Expense ID (the number after #): "))
    except ValueError:
        print("Please enter a number.")
        return None

def set_budget(category, limit):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT CategoryId FROM Categories WHERE Name = ?", category)
        row = cur.fetchone()
        if row is None:
            print(f"Category '{category}' does not exist.")
            return
        cur.execute(
            "UPDATE Budgets SET MonthlyLimit = ? WHERE CategoryId = ?",
            limit, row.CategoryId,
        )
        if cur.rowcount == 0:
            cur.execute(
                "INSERT INTO Budgets (CategoryId, MonthlyLimit) VALUES (?, ?)",
                row.CategoryId, limit,
            )
        conn.commit()
        print(f"Budget for {category} set to {limit:.2f} per month.")


def budget_report(year, month):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("EXEC dbo.usp_BudgetReport ?, ?", year, month)
        rows = cur.fetchall()
        if not rows:
            print("No budgets set yet. Use option 7 to set one.")
            return
        print(f"\nBudget report for {year}-{month:02d}")
        print(f"  {'Category':<12} {'Budget':>9} {'Spent':>9} {'Left':>9}")
        for r in rows:
            status = "  <-- OVER BUDGET" if r.Spent > r.MonthlyLimit else ""
            print(
                f"  {r.Category:<12} {r.MonthlyLimit:>9.2f} "
                f"{r.Spent:>9.2f} {r.Remaining:>9.2f}{status}"
            )        

def ask_year_month():
    try:
        year = int(input("Year (e.g. 2026): "))
        month = int(input("Month (1-12): "))
        if not 1 <= month <= 12:
            raise ValueError
        return year, month
    except ValueError:
        print("Please enter a valid year and a month from 1 to 12.")
        return None
        
def main():
    while True:
        print("\n1) Add expense  2) Monthly report  3) Latest expenses")
        print("4) Export report  5) Edit expense  6) Delete expense")
        print("7) Set budget  8) Budget report  9) Quit")
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
            period = ask_year_month()
            if period:
                monthly_report(*period)

        elif choice == "3":
            recent_expenses()

        elif choice == "4":
            period = ask_year_month()
            if period:
                export_report(*period)

        elif choice == "5":
            recent_expenses()
            expense_id = ask_expense_id()
            if expense_id is not None:
                edit_expense(expense_id)

        elif choice == "6":
            recent_expenses()
            expense_id = ask_expense_id()
            if expense_id is not None:
                delete_expense(expense_id)

        elif choice == "7":
            print("Categories:", ", ".join(list_categories()))
            category = input("Category: ").strip()
            try:
                limit = float(input("Monthly budget: "))
                if limit <= 0:
                    raise ValueError
            except ValueError:
                print("Budget must be a positive number.")
                continue
            set_budget(category, limit)

        elif choice == "8":
            period = ask_year_month()
            if period:
                budget_report(*period)

        elif choice == "9":
            print("Goodbye!")
            break

        else:
            print("Please choose a number from 1 to 9.")


if __name__ == "__main__":
    main()