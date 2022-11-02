from flask import Flask, render_template, request, redirect, url_for, session, flash
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
    msg = " "
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        sql = "SELECT clients.*,budgets.MAXBUDGET FROM clients LEFT JOIN BUDGETS ON CLIENTs.ID=BUDGETS.ID WHERE username =? AND password =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        # print(account)
        if account:
            session["Loggedin"] = True
            session["id"] = account["ID"]
            session["email"] = account["EMAIL"]
            session["username"] = account["USERNAME"]
            session["budget"] = account["MAXBUDGET"]
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
    session.clear()
    return redirect("/")


@app.route("/dashboard")
def dashboard():
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
            ibm_db.bind_param(stmt, 2, session["id"])
            if ibm_db.execute(stmt):
                msg = "Successfully Changed Password!!!!"

        else:
            msg = "Passwords not equal"
    flash(msg)
    return redirect(url_for("dashboard"))


@app.route("/changeBudget/", methods=["POST", "GET"])
def changeBudget():
    msg = "Enter the new budget"
    if request.method == "POST":
        budgetAmount = request.form["budgetAmount"]
        sql = "UPDATE BUDGETS SET maxBudget=? where id=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, budgetAmount)
        ibm_db.bind_param(stmt, 2, session["id"])
        if ibm_db.execute(stmt):
            session["budget"] = budgetAmount
            msg = "Successfully Changed Budget!!!!"
        else:
            msg = "Budget not changed"
    flash(msg)
    return redirect(url_for("dashboard"))


@app.route("/addBudget/", methods=["POST", "GET"])
def addBudget():
    msg = "Enter the budget"
    if request.method == "POST":
        budgetAmount = request.form["budgetAmountToAdd"]
        sql = "INSERT INTO BUDGETS(id,maxbudget) VALUES(?,?)"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, session["id"])
        ibm_db.bind_param(stmt, 2, budgetAmount)
        if ibm_db.execute(stmt):
            session["budget"] = budgetAmount
            msg = "Successfully Set The Budget!!!!"
        else:
            msg = "Budget not set yet"
    flash(msg)
    return redirect(url_for("dashboard"))


def fetchall(stmt):
    ibm_db.bind_param(stmt, 1, session["id"])
    ibm_db.execute(stmt)
    results = []
    result_dict = ibm_db.fetch_assoc(stmt)
    results.append(result_dict)
    while result_dict is not False:
        result_dict = ibm_db.fetch_assoc(stmt)
        results.append(result_dict)
    return results


@app.route("/log_today")
def logToday():
    sql = "SELECT AMOUNT,NEED,EDUCATION,ENTERTAINMENT,TRAVEL,FOOD,HEALTH,OTHERS FROM Expenses WHERE ID=?"
    stmt = ibm_db.prepare(conn, sql)
    expenseData = fetchall(stmt)
    sql = "SELECT AMOUNT FROM income WHERE ID=?"
    stmt = ibm_db.prepare(conn, sql)
    incomeData = fetchall(stmt)
    return render_template(
        "sample.html",
        title="Today's Log",
        expenseData=expenseData,
        incomeData=incomeData,
    )


@app.route("/addExpense/", methods=["POST", "GET"])
def addExpense():
    msg = ""
    if request.method == "POST":
        amount = request.form["Amount"]
        need = request.form["Need/Want"]
        option = request.form.getlist("options")
        sql = "INSERT INTO ExpenseS(ID,AMOUNT,NEED"
        for o in option:
            sql = sql + "," + o
        sql = sql + ") VALUES(?,?,?" + (len(option) * ",TRUE") + ")"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, session["id"])
        ibm_db.bind_param(stmt, 2, amount)
        ibm_db.bind_param(stmt, 3, need)
        if ibm_db.execute(stmt):
            msg = "Successfully Added Expense!!!!"
        else:
            msg = "Expense not added"

    flash(msg)
    return redirect(url_for("logToday"))


@app.route("/addIncome/", methods=["POST", "GET"])
def addIncome():
    msg = ""
    if request.method == "POST":
        amount = request.form["AmountIncome"]
        sql = "INSERT INTO INCOME(ID,AMOUNT) VALUES(?,?)"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, session["id"])
        ibm_db.bind_param(stmt, 2, amount)
        if ibm_db.execute(stmt):
            msg = "Successfully Added Income!!!!"
        else:
            msg = "Income not added"

    flash(msg)
    return redirect(url_for("logToday"))
    # return render_template("sample.html", title="Today's Log", msg=msg)


# @app.route("/Edit")
###Visualization functions


if __name__ == "__main__":
    app.debug = True
    app.run()
