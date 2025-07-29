from flask import Flask, request, redirect, render_template
import sqlite3
import string
import random
import os

app = Flask(__name__)
DATABASE = 'database.db'

# Ensure templates folder exists
os.makedirs('templates', exist_ok=True)

# Create HTML file if it doesn't exist
html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Simple URL Shortener</title>
</head>
<body>
    <h2>Enter URL to Shorten</h2>
    <form method="POST">
        <input type="url" name="long_url" placeholder="https://example.com" required>
        <button type="submit">Shorten</button>
    </form>

    {% if short_url %}
        <p>Short URL: <a href="{{ short_url }}" target="_blank">{{ short_url }}</a></p>
    {% endif %}
</body>
</html>
'''

# Save HTML to file
with open("templates/index.html", "w") as f:
    f.write(html_content)

# Initialize SQLite database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short_code TEXT UNIQUE,
                long_url TEXT
            )
        ''')
init_db()

# Generate a unique short code
def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

# Home route
@app.route("/", methods=["GET", "POST"])
def home():
    short_url = None
    if request.method == "POST":
        long_url = request.form["long_url"]
        short_code = generate_short_code()

        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            # Ensure short code is unique
            while True:
                cursor.execute("SELECT * FROM urls WHERE short_code = ?", (short_code,))
                if cursor.fetchone() is None:
                    break
                short_code = generate_short_code()

            cursor.execute("INSERT INTO urls (short_code, long_url) VALUES (?, ?)", (short_code, long_url))
            conn.commit()

        short_url = request.host_url + short_code
    return render_template("index.html", short_url=short_url)

# Redirect route
@app.route("/<short_code>")
def redirect_to_long_url(short_code):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT long_url FROM urls WHERE short_code = ?", (short_code,))
