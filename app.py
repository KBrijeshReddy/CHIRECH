from flask import Flask, render_template, request, url_for, redirect, session
from flask_pymongo import PyMongo

language = ""

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/luxIncognito"
db = PyMongo(app).db
app.secret_key = "6g87G77hi8J7h4w7HuF7h"

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/leaderboard")
def leaderboard():
    users = db.users.find({}, {"_id": 0, "name": 1, "tests": 1})
    summ = []
    try:
        for user in users:
            summ.append((sum(list(dict(user["tests"]).values())), user["name"]))
        summ.sort(key=lambda x: x[0], reverse=True)
        print(summ)
    except Exception:
        pass
    return render_template("leaderboard.html", sum=summ)

@app.route("/questions", methods=["POST", "GET"])
def questions():
    if session.__contains__("name") and request.method == "POST":
        name = session["name"]
        test = dict(request.get_json())
        try:
            db.users.update_one({"name": name}, {"$set": {"tests."+test["language"]: 2 * test["correct"] - test["wrong"]}})
        except KeyError:
            pass
    return render_template("questions.html", language=language)

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        session.pop("name", None)
        name = request.form["name"]
        if db.users.find_one({"name": name}): return render_template("register.html", message="nameExists")
        else:
            db.users.insert_one({"name": name, "email": request.form["email"], "password": request.form["password"], "tests": {}})
            session["name"] = name
            return redirect("/profile")
    return render_template("register.html", message="")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.pop("name", None)
        name = request.form["name"]
        password = request.form["password"]
        user = db.users.find_one({"name": name})
        if not user: return render_template("login.html", message="nameNotFound")
        else:
            user = db.users.find_one({"name": name, "password": password})
            if not user: return render_template("login.html", message="wrongPassword")
            else:
                session["name"] = name
                return redirect("/profile")
    return render_template("login.html", message="")

@app.route("/logout")
def logout():
    session.pop("name", None)
    return redirect("/login")

@app.route("/profile")
def profile():
    try: name = session["name"]
    except KeyError:
        return redirect("/login")
    
    return render_template("profile.html", name=name, email=db.users.find_one({"name": name}, {"email": 1})["email"])

@app.route("/spanish")
def spanish():
    global language
    language = "spanish"
    return redirect("/questions")

@app.route("/french")
def french():
    global language
    language = "french"
    return redirect("/questions")

@app.route("/german")
def german():
    global language
    language = "german"
    return redirect("/questions")

@app.route("/english")
def italian():
    global language
    language = "english"
    return redirect("/questions")

@app.route("/japanese")
def japanese():
    global language
    language = "japanese"
    return redirect("/questions")

app.run(debug=True)