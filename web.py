from datetime import date

from flask import Flask, flash, redirect, render_template, request, url_for

from cli import get_connection, list_categories

app = Flask(__name__)
app.secret_key = "change-this-later"


@app.route("/")
def index():
    today = date.today()
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("EXEC dbo.usp_MonthlyReport ?, ?", today.year, today.month)
        summary = cur.fetchall()
        cur.execute(
            "SELECT TOP (10) e.ExpenseId, e.ExpenseDate, c.Name, e.Amount, e.Description "
            "FROM Expenses e JOIN Categories c ON c.CategoryId = e.CategoryId "
            "ORDER BY e.ExpenseDate DESC, e.ExpenseId DESC"
        )
        expenses = cur.fetchall()
    return render_template(
        "index.html",
        summary=summary,
        expenses=expenses,
        categories=list_categories(),
        today=today,
    )


@app.route("/add", methods=["POST"])
def add():
    category = request.form.get("category", "").strip()
    description = request.form.get("description", "").strip()
    try:
        amount = float(request.form.get("amount", ""))
        if amount <= 0:
            raise ValueError
    except ValueError:
        flash("Amount must be a positive number.")
        return redirect(url_for("index"))

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT CategoryId FROM Categories WHERE Name = ?", category)
        row = cur.fetchone()
        if row is None:
            flash("Please choose a valid category.")
            return redirect(url_for("index"))
        cur.execute(
            "INSERT INTO Expenses (CategoryId, Amount, Description, ExpenseDate) "
            "VALUES (?, ?, ?, ?)",
            row.CategoryId, amount, description, date.today(),
        )
        conn.commit()
    flash("Expense added.")
    return redirect(url_for("index"))


@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete(expense_id):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM Expenses WHERE ExpenseId = ?", expense_id)
        conn.commit()
    flash("Expense deleted.")
    return redirect(url_for("index"))


@app.route("/edit/<int:expense_id>", methods=["GET", "POST"])
def edit(expense_id):
    with get_connection() as conn:
        cur = conn.cursor()

        if request.method == "POST":
            category = request.form.get("category", "").strip()
            description = request.form.get("description", "").strip()
            try:
                amount = float(request.form.get("amount", ""))
                if amount <= 0:
                    raise ValueError
                expense_date = date.fromisoformat(request.form.get("expense_date", ""))
            except ValueError:
                flash("Please enter a positive amount and a valid date.")
                return redirect(url_for("edit", expense_id=expense_id))

            cur.execute("SELECT CategoryId FROM Categories WHERE Name = ?", category)
            row = cur.fetchone()
            if row is None:
                flash("Please choose a valid category.")
                return redirect(url_for("edit", expense_id=expense_id))

            cur.execute(
                "UPDATE Expenses SET CategoryId = ?, Amount = ?, Description = ?, ExpenseDate = ? "
                "WHERE ExpenseId = ?",
                row.CategoryId, amount, description, expense_date, expense_id,
            )
            conn.commit()
            flash("Expense updated.")
            return redirect(url_for("index"))

        cur.execute(
            "SELECT e.ExpenseId, c.Name, e.Amount, e.Description, e.ExpenseDate "
            "FROM Expenses e JOIN Categories c ON c.CategoryId = e.CategoryId "
            "WHERE e.ExpenseId = ?",
            expense_id,
        )
        expense = cur.fetchone()

    if expense is None:
        flash("That expense does not exist.")
        return redirect(url_for("index"))
    return render_template("edit.html", expense=expense, categories=list_categories())


@app.route("/budgets")
def budgets():
    today = date.today()
    period = request.args.get("period", today.strftime("%Y-%m"))
    try:
        year_text, month_text = period.split("-")
        year, month = int(year_text), int(month_text)
        if not 1 <= month <= 12:
            raise ValueError
    except ValueError:
        year, month = today.year, today.month

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("EXEC dbo.usp_BudgetReport ?, ?", year, month)
        rows = cur.fetchall()

    return render_template(
        "budgets.html",
        rows=rows,
        period=f"{year}-{month:02d}",
        categories=list_categories(),
    )


@app.route("/budgets/save", methods=["POST"])
def save_budget():
    category = request.form.get("category", "").strip()
    period = request.form.get("period", "")
    try:
        limit = float(request.form.get("limit", ""))
        if limit <= 0:
            raise ValueError
    except ValueError:
        flash("Budget must be a positive number.")
        return redirect(url_for("budgets", period=period))

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT CategoryId FROM Categories WHERE Name = ?", category)
        row = cur.fetchone()
        if row is None:
            flash("Please choose a valid category.")
            return redirect(url_for("budgets", period=period))
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
    flash(f"Budget for {category} saved.")
    return redirect(url_for("budgets", period=period))


if __name__ == "__main__":
    app.run(debug=True)

