from multiprocessing.spawn import prepare
from turtle import title
from flask import Flask, render_template, request, redirect, url_for, session
import ibm_db
import re

app = Flask(__name__)
app.secret_key = "Zenik"

conn = ibm_db.connect(
    "DATABASE=bludb;"
    "HOSTNAME=6667d8e9-9d4d-4ccb-ba32-21da3bb5aafc.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;"
    "PORT=30376;"
    "SECURITY=SSL;"
    "SSLServerCertificate=C:/Users/bhaua/OneDrive/Desktop/SEM Stuff KCT/IBM/DigiCertGlobalRootCA.crt;"
    "UID=bcv24102;"
    "PWD=ilZgx2Zokf2nJOCW;",
    "",
    "",
)


@app.route("/", methods=["POST", "GET"])
@app.route("/home")
def home():
    return render_template("home.html", title="Home")


@app.route("/login", methods=["GET", "POST"])
def login():
    global userid
    msg = " "
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        sql = "SELECT * FROM clients WHERE username =? AND password =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account:
            session["Loggedin"] = True
            session["id"] = account["ID"]
            session["email"] = account["EMAIL"]
            userid = account["ID"]
            session["username"] = account["USERNAME"]
            return redirect("/dashboard")
        else:
            msg = "Incorrect login credentials"

    return render_template("login.html", title="Login", msg=msg)


@app.route("/register", methods=["GET", "POST"])
def register():
    msg = " "
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        password1 = request.form["password1"]
        sql = "SELECT * FROM CLIENTS WHERE username =? or email=? "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.bind_param(stmt, 2, email)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg = "Account already exists"
        elif password1 != password:
            msg = "re-entered password doesnt match"
        elif not re.match(r"[A-Za-z0-9]+", username):
            msg = "Username should be only alphabets and numbers"
        else:
            sql = "INSERT INTO clients(EMAIL,USERNAME,PASSWORD) VALUES (?,?,?)"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, email)
            ibm_db.bind_param(stmt, 2, username)
            ibm_db.bind_param(stmt, 3, password)
            ibm_db.execute(stmt)
            return redirect("/login")
    return render_template("register.html", msg=msg, title="Register")


@app.route("/logout")
def logout():
    session.pop("Loggedin", None)
    session.pop("id", None)
    session.pop("username", None)
    return redirect("/")


@app.route("/dashboard")
def dashboard():
    sql = "SELECT * FROM clients WHERE id =?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, session["id"])
    ibm_db.execute(stmt)
    return render_template("dashboard.html", title="Dashboard")


@app.route("/changePassword/", methods=["POST", "GET"])
def changePassword():
    msg = "Enter the new password"
    if request.method == "POST":
        pass1 = request.form["pass1"]
        pass2 = request.form["pass2"]
        if pass1 == pass2:
            sql = "UPDATE CLIENTS SET password=? where id=?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, pass1)
            ibm_db.bind_param(stmt, 2, userid)
            if ibm_db.execute(stmt):
                msg = "Successfully Changed Password!!!!"

        else:
            msg = "Passwords not equal"
    return render_template("dashboard.html", msg=msg, title="DashBoard")


@app.route("/changeBudget/", methods=["POST", "GET"])
def changeBudget():
    msg = "Enter the new budget"
    if request.method == "POST":
        budgetAmount = request.form["budgetAmount"]
        sql = "UPDATE BUDGETS SET password=? where id=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, budgetAmount)
        ibm_db.bind_param(stmt, 2, userid)
        if ibm_db.execute(stmt):
            msg = "Successfully Changed Budget!!!!"
        else:
            msg = "Budget not changed"
    return render_template("dashboard.html", msg=msg, title="DashBoard")


@app.route("/addBudget")
def addBudget():
    pass


@app.route("/log_today")
def logToday():
    pass


@app.route("/addExpense/")
def addExpense():
    pass


@app.route("/addIncome/")
def addIncome():
    pass


# @app.route("/Edit")
###Visualization functions


if __name__ == "__main__":
    app.debug = True
    app.run()
