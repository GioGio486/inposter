from flask import Flask, render_template, redirect, url_for, request, session, flash
from questions import questions

app = Flask(__name__)
app.secret_key = "supersecretkey"

players = []
answers = []

# Fixed question for all players
current_question = questions[0]  # always use the first question

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
    global answers
    if len(players) < 2:
        flash("At least 2 players needed to start.")
        return redirect(url_for("lobby"))
    answers.clear()
    return redirect(url_for("game"))

@app.route("/game")
def game():
    player_name = session.get("name")
    if not player_name or player_name not in players:
        flash("You must join the lobby first.")
        return redirect(url_for("lobby"))

    answered = any(a["name"] == player_name for a in answers)
    question_text = current_question["normal"]  # all get same question now
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

    return render_template(
        "reveal.html",
        question=current_question["normal"],
        answers=answers
    )

@app.route("/reset")
def reset():
    global players, answers
    players.clear()
    answers.clear()
    session.clear()
    flash("Game reset.")
    return redirect(url_for("lobby"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
