"""
3D Bharat - Backend API
Handles user signup, login, and Google-auth persistence.
Run with: python app.py
"""

import sqlite3
import os
import datetime
import jwt
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)  # allows your HTML/JS (loaded from a different origin/file) to call this API

SECRET_KEY = os.environ.get("JWT_SECRET", "dev-secret-change-this-before-deploying")
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,          -- NULL for Google-only accounts
            auth_provider TEXT DEFAULT 'password',  -- 'password' or 'google'
            picture TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def make_token(user_row):
    payload = {
        "user_id": user_row["id"],
        "email": user_row["email"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return None


# ---------- Routes ----------

@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json(force=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    conn = get_db()
    existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if existing:
        conn.close()
        return jsonify({"error": "An account with this email already exists"}), 409

    password_hash = generate_password_hash(password)
    cur = conn.execute(
        "INSERT INTO users (name, email, password_hash, auth_provider) VALUES (?, ?, ?, 'password')",
        (name, email, password_hash),
    )
    conn.commit()
    user_id = cur.lastrowid
    user_row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()

    token = make_token(user_row)
    return jsonify({"token": token, "name": name, "email": email}), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(force=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    conn = get_db()
    user_row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()

    if not user_row or not user_row["password_hash"]:
        return jsonify({"error": "Invalid email or password"}), 401

    if not check_password_hash(user_row["password_hash"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = make_token(user_row)
    return jsonify({"token": token, "name": user_row["name"], "email": user_row["email"]}), 200


@app.route("/api/save-user", methods=["POST"])
def save_user():
    """Called after Google Sign-In to persist/update the user record."""
    data = request.get_json(force=True) or {}
    email = (data.get("email") or "").strip().lower()
    name = data.get("name") or ""
    picture = data.get("picture") or ""

    if not email:
        return jsonify({"error": "Email is required"}), 400

    conn = get_db()
    existing = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

    if existing:
        conn.execute(
            "UPDATE users SET name = ?, picture = ? WHERE email = ?",
            (name, picture, email),
        )
        user_row = existing
    else:
        conn.execute(
            "INSERT INTO users (name, email, auth_provider, picture) VALUES (?, ?, 'google', ?)",
            (name, email, picture),
        )
        user_row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

    conn.commit()
    conn.close()

    token = make_token(user_row)
    return jsonify({"token": token, "name": name, "email": email}), 200


@app.route("/api/me", methods=["GET"])
def me():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401

    token = auth_header.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401

    conn = get_db()
    user_row = conn.execute("SELECT id, name, email, picture FROM users WHERE id = ?", (payload["user_id"],)).fetchone()
    conn.close()

    if not user_row:
        return jsonify({"error": "User not found"}), 404

    return jsonify(dict(user_row)), 200

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "message": "3D Bharat Flask API is running"
    })

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)