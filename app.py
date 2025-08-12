from flask import Flask, render_template, redirect, url_for, request, session, flash
import random
from questions import questions

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Use env var in production

players = []
current_question = None
impostor_index = None
answers = []

@app.route("/")
def lobby():
    return render_template("lobby.html", players=players)

@app.route("/join", methods=["POST"])
def join():
    name = request.form.get("name", "").strip()
    if not name:
        flash("Please enter a name.")
        return redirect(url_for("lobby"))
    if name in players:
        flash("Name already taken, please choose another.")
        return redirect(url_for("lobby"))
    players.append(name)
    session["name"] = name
    return redirect(url_for("lobby"))

@app.route("/start")
def start():
    global current_question, impostor_index, answers
    if len(players) < 2:
        flash("At least 2 players needed to start.")
        return redirect(url_for("lobby"))
    current_question = random.choice(questions)
    impostor_index = random.randint(0, len(players) - 1)
    answers.clear()
    return redirect(url_for("game"))

@app.route("/game")
def game():
    player_name = session.get("name")
    if not player_name or player_name not in players:
        flash("You must join the lobby first.")
        return redirect(url_for("lobby"))
    player_index = players.index(player_name)
    question_text = current_question["impostor"] if player_index == impostor_index else current_question["normal"]
    answered = any(a["name"] == player_name for a in answers)
    return render_template("game.html", name=player_name, question=question_text, answered=answered)

@app.route("/answer", methods=["POST"])
def answer():
    player_name = session.get("name")
    if not player_name or player_name not in players:
        flash("You must join the lobby first.")
        return redirect(url_for("lobby"))

    if any(a["name"] == player_name for a in answers):
        flash("You already answered.")
        return redirect(url_for("game"))

    answer_text = request.form.get("answer", "").strip()
    if not answer_text:
        flash("Answer cannot be empty.")
        return redirect(url_for("game"))

    answers.append({"name": player_name, "answer": answer_text})

    if len(answers) == len(players):
        return redirect(url_for("reveal"))
    else:
        flash("Answer submitted. Waiting for others.")
        return redirect(url_for("game"))

@app.route("/reveal")
def reveal():
    if len(answers) < len(players):
        flash("Waiting for all players to answer.")
        return redirect(url_for("game"))
    return render_template("reveal.html", answers=answers, impostor=players[impostor_index])

@app.route("/reset")
def reset():
    global players, current_question, impostor_index, answers
    players.clear()
    current_question = None
    impostor_index = None
    answers.clear()
    session.clear()
    flash("Game reset.")
    return redirect(url_for("lobby"))
