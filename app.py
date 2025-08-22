from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"  # needed for sessions

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT, stats INTEGER)''')
    conn.commit()
    conn.close()

init_db()

# --- Routes ---
@app.route("/")
def home():
    if "username" in session:
        return f"Hello, {session['username']}! Your stats: {get_stats(session['username'])}"
    return "Welcome! <a href='/login'>Login</a> or <a href='/register'>Register</a>"

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users VALUES (?, ?, ?)", (username, password, 0))
            conn.commit()
        except:
            return "Username already exists!"
        conn.close()
        return redirect(url_for("login"))
    return '''
        <form method="post">
            Username: <input name="username"><br>
            Password: <input name="password" type="password"><br>
            <input type="submit" value="Register">
        </form>
    '''

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["username"] = username
            return redirect(url_for("home"))
        return "Invalid credentials!"
    return '''
        <form method="post">
            Username: <input name="username"><br>
            Password: <input name="password" type="password"><br>
            <input type="submit" value="Login">
        </form>
    '''

@app.route("/add_stat")
def add_stat():
    if "username" in session:
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("UPDATE users SET stats = stats + 1 WHERE username=?", (session["username"],))
        conn.commit()
        conn.close()
        return redirect(url_for("home"))
    return redirect(url_for("login"))

def get_stats(username):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT stats FROM users WHERE username=?", (username,))
    stats = c.fetchone()[0]
    conn.close()
    return stats

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)

