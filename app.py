from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "your-super-secret-key"

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="yourpassword",  
        database="movie",
        auth_plugin='mysql_native_password'
    )
    cursor = db.cursor(dictionary=True)
except mysql.connector.Error as err:
    print("Database Connection Error:", err)
    db = None
    cursor = None



@app.route("/")
def welcome():
    return render_template("welcome.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "hardik" and password == "pondi":
            session['user'] = username
            return redirect(url_for("search"))
        else:
            error = "Invalid username or password."

    return render_template("login.html", error=error)



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("welcome"))



@app.route("/search", methods=["GET", "POST"])
def search():
    if 'user' not in session:
        return redirect(url_for("login"))

    if not cursor:
        return "Database connection error.", 500

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        sql = "SELECT * FROM movie WHERE names LIKE %s"
        cursor.execute(sql, (f"%{query}%",))
        movies = cursor.fetchall()

        return render_template("results.html", movies=movies, query=query)

    return render_template("search.html")



@app.route("/add_movie", methods=["GET", "POST"])
def add_movie():
    if 'user' not in session:
        return redirect(url_for("login"))

    if not cursor:
        return "Database connection error.", 500

    if request.method == "POST":
        movie_data = (
            request.form.get("names"),
            request.form.get("year"),
            request.form.get("genre"),
            request.form.get("runtime"),
            request.form.get("score"),
            request.form.get("director"),
            request.form.get("writer"),
            request.form.get("star"),
            request.form.get("country"),
            request.form.get("budget"),
            request.form.get("gross"),
            request.form.get("company"),
            request.form.get("released")
        )

        sql = """
            INSERT INTO movie 
            (names, year, genre, runtime, score, director, writer, star,
            country, budget, gross, company, released)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        try:
            cursor.execute(sql, movie_data)
            db.commit()
            flash(f"✅ Movie '{movie_data[0]}' added successfully!", "success")
        except mysql.connector.Error as err:
            flash(f"👻 Database Error: {err}", "error")

        return redirect(url_for("add_movie"))

    return render_template("add_movie.html")



if __name__ == "__main__":
    app.run(debug=True)
