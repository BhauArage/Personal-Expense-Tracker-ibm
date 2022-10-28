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
    return render_template("home.html", title="Home", msg=" hiṇ ")


##this works
@app.route("/sample", methods=["POST", "GET"])
def sample():
    if request.method == "POST":
        amount = request.form["amount"]
        sql = "INSERT INTO BUDGETS(id,maxbudget) VALUES(?,?)"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, 100)
        ibm_db.bind_param(stmt, 2, amount)
        ibm_db.execute(stmt)
        return redirect(request.referrer)
    sql = "SELECT * FROM budgets WHERE id =100"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)

    return render_template(
        "sample.html", title="Sample", account=account, messa="<h1>BHAVIKA</h1>"
    )


@app.route("/dashboard")
def dashboard():
    sql = "SELECT * FROM clients WHERE id =?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, session["id"])
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    return render_template("dashboard.html", title="Dashboard", account=account)


@app.route("/logout")
def logout():
    session.pop("Loggedin", None)
    session.pop("id", None)
    session.pop("username", None)
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    global userid
    msg = " "
    print("heyoo")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        print("heyoo")
        sql = "SELECT * FROM clients WHERE username =? AND password =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            session["Loggedin"] = True
            session["id"] = account["ID"]
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


if __name__ == "__main__":
    app.debug = True
    app.run()
