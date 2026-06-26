from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Create Database
def init_db():
    conn = sqlite3.connect("portfolio.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS portfolio(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_name TEXT,
        quantity INTEGER,
        price REAL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        action TEXT,
        stock_name TEXT,
        quantity INTEGER,
        price REAL,
        amount REAL
    )
    """)

    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    conn = sqlite3.connect("portfolio.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM portfolio")
    stocks = cur.fetchall()

    cur.execute("SELECT * FROM history ORDER BY id DESC")
    history = cur.fetchall()

    total_value = sum(row[2] * row[3] for row in stocks)
    total_invested = sum(row[6] for row in history if row[2] == "Buy")
    total_sold = sum(row[6] for row in history if row[2] == "Sell")
    net_investment = total_invested - total_sold
    profit_loss = total_value - net_investment

    conn.close()

    return render_template(
        "index.html",
        stocks=stocks,
        total_value=total_value,
        total_invested=total_invested,
        total_sold=total_sold,
        net_investment=net_investment,
        profit_loss=profit_loss,
        history=history,
    )

@app.route("/add", methods=["POST"])
def add_stock():

    stock = request.form["stock"]
    quantity = int(request.form["quantity"])
    price = float(request.form["price"])
    amount = quantity * price
    timestamp = datetime.utcnow().isoformat()

    conn = sqlite3.connect("portfolio.db")
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO portfolio(stock_name, quantity, price) VALUES(?,?,?)",
        (stock, quantity, price)
    )

    cur.execute(
        "INSERT INTO history(timestamp, action, stock_name, quantity, price, amount) VALUES(?,?,?,?,?,?)",
        (timestamp, "Buy", stock, quantity, price, amount)
    )

    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/delete/<int:id>")
def delete(id):

    conn = sqlite3.connect("portfolio.db")
    cur = conn.cursor()

    cur.execute("SELECT stock_name, quantity, price FROM portfolio WHERE id=?", (id,))
    stock = cur.fetchone()

    if stock:
        stock_name, quantity, price = stock
        amount = quantity * price
        timestamp = datetime.utcnow().isoformat()

        cur.execute(
            "INSERT INTO history(timestamp, action, stock_name, quantity, price, amount) VALUES(?,?,?,?,?,?)",
            (timestamp, "Sell", stock_name, quantity, price, amount)
        )

    cur.execute("DELETE FROM portfolio WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
