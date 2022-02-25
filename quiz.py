from flask import Flask, render_template, request, session, redirect, url_for, flash
import random
from flask_pymongo import PyMongo
import uuid
from model import get_flashcards, get_highscores, check_highscore, save_highscore

app = Flask(__name__)
app.secret_key = <my_secret>
app.config["MONGO_URI"] = "mongodb+srv://<my_username>:<my_password>@cluster0.enbio.mongodb.net/Quiz?retryWrites=true&w=majority"

mongo = PyMongo(app)
db = mongo.db
flashcards = get_flashcards(db)
number_of_questions = len(flashcards)

@app.route("/")
def welcome():
    """Set session variables and return the Home page."""
    countries = list(flashcards.keys())
    next_country = random.choice(countries)
    unique_id = str(uuid.uuid4())
    session["sess_id"] = unique_id
    session[unique_id + "counter"] = 0
    session[unique_id + "countries"] = countries
    session[unique_id + "country"] = next_country
    return render_template("welcome.html")

@app.route("/flashcard/", methods=["GET", "POST"])
def flashcard():
    """Show the Question page for a GET request. For POST requests check the user's answer and return the Question page for the next coutry."""
    if "sess_id" in session:
        unique_id = session["sess_id"]
        counter = session[unique_id + "counter"]
        countries = session[unique_id + "countries"]
        country = session[unique_id + "country"]
        if request.method == "GET":
            if country not in countries:
                return redirect(url_for("error"))
            else:
                return render_template("flashcard.html", country=country.title())
        else:
            capital = flashcards[country]
            countries.remove(country)
            session[unique_id + "countries"] = countries
            try:
                next_country = random.choice(countries)                
            except IndexError: # All flashcards have been shown
                next_country = "Finish"
        if request.form["answer"].lower() == capital:
            counter += 1
            session[unique_id + "counter"] = counter
            result = "Correct!"
        else:
            result = "Wrong."
        flash(f"{result} The capital of {country.title()} is {capital.title()}.")
        session[unique_id + "country"] = next_country
        return render_template("flashcard.html", country=next_country.title())
    else:
        return redirect(url_for("error"))

@app.route("/finish", methods=["GET", "POST"])
def finish():
    """For GET requests check if a high score was made and return the Finish page accordingly. For POST requests save the score in the database and redirect to the High Score page."""
    if "sess_id" in session:
        unique_id = session["sess_id"]
        counter = session[unique_id + "counter"]
        if request.method == "GET":
            highscore = check_highscore(counter, app)
            return render_template("finish.html", score=counter, max_score=number_of_questions, highscore=highscore)
        else:
            name = request.form["name"]
            save_highscore(name, counter, app)
            return redirect(url_for("highscore"))
    else:
        return redirect(url_for("error"))

@app.route("/highscore")
def highscore():
    """Get high scores from the database and show them."""
    scores = get_highscores(app)
    return render_template("highscore.html", scores=sorted(scores, key=lambda x:x[1], reverse=True))

@app.route("/error")
def error():
    """Show an error page."""
    return render_template("error.html")
