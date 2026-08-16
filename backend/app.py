# ============================================================
#  PYGUARD - MAIN BACKEND (PROFILE SCORE + CHARTS ENABLED)
# ============================================================

import os
import json
import sys
import time
import subprocess
import multiprocessing

from flask import (
    Flask,
    flash,
    request,
    jsonify,
    render_template,
    redirect,
    session
)
from werkzeug.security import generate_password_hash, check_password_hash

# ============================================================
# INTERNAL MODULE IMPORTS
# ============================================================

from .assistant_api import assistant_bp
from .file_utils import read_file_as_text, extract_zip, list_py_files
from .static_analyzer import analyze_code
from .security_analyzer import scan_security
from .similarity_analyzer import find_duplicates
from .ai_service import run_ai_analysis, run_ai_chat
from .config import TEMP_FOLDER

# ============================================================
# BASIC SETUP
# ============================================================

os.makedirs(TEMP_FOLDER, exist_ok=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "..", "templates"),
    static_folder=os.path.join(BASE_DIR, "..", "static")
)

app.secret_key = "NIKHIL_SUPER_SECRET_KEY_2025"
app.register_blueprint(assistant_bp)

# ============================================================
# USER DATA STORAGE (STATS + ACTIVITY)
# ============================================================

USERS_FILE = "users.json"

DEFAULT_STATS = {
    "scans": 0,
    "threats": 0,
    "snippets": 0,
    "ai_chats": 0
}


def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    return json.load(open(USERS_FILE, "r"))


def save_users(data):
    json.dump(data, open(USERS_FILE, "w"), indent=2)


def get_user_stats(username):
    users = load_users()
    stats = users.get(username + "_stats", DEFAULT_STATS.copy())
    users[username + "_stats"] = stats
    save_users(users)
    return stats


def save_user_stats(username, stats):
    users = load_users()
    users[username + "_stats"] = stats
    save_users(users)


def push_activity(username, text):
    users = load_users()
    key = username + "_activity"
    activity = users.get(key, [])
    activity.append(text)
    users[key] = activity[-30:]
    save_users(users)


def get_activity(username):
    users = load_users()
    return users.get(username + "_activity", [])


# ============================================================
# PROFILE ANALYTICS (NEW – SAFE ADDITION)
# ============================================================

def calculate_analyzer_score(stats):
    """
    Score out of 100 based on real usage
    """
    score = (
        stats.get("scans", 0) * 4 +
        stats.get("threats", 0) * 2 +
        stats.get("ai_chats", 0)
    )
    return min(score, 100)


def build_profile_analytics(stats):
    """
    Chart-friendly analytics data
    """
    return {
        "labels": ["Scans", "Threats", "AI Chats", "Snippets"],
        "values": [
            stats.get("scans", 0),
            stats.get("threats", 0),
            stats.get("ai_chats", 0),
            stats.get("snippets", 0)
        ]
    }


# ============================================================
# CODE EXECUTION (PLAYGROUND)
# ============================================================

MAX_RUNTIME = 12  # seconds


def execute_python(code, pipe):
    try:
        with open("temp_exec.py", "w", encoding="utf-8") as f:
            f.write(code)

        process = subprocess.Popen(
            [sys.executable, "temp_exec.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        start = time.time()

        while True:
            if process.poll() is not None:
                break

            line = process.stdout.readline()
            if line:
                pipe.send(line)

            if time.time() - start > MAX_RUNTIME:
                process.kill()
                pipe.send("⚠ Execution timeout\n")
                break

        error = process.stderr.read()
        if error:
            pipe.send("⚠ ERROR:\n" + error)

    except Exception as e:
        pipe.send("Runtime crash: " + str(e))


@app.route("/run-code", methods=["POST"])
def run_code():
    code = request.json.get("code", "")

    if not code.strip():
        return jsonify({"output": "❌ No code provided"}), 400

    parent, child = multiprocessing.Pipe()
    job = multiprocessing.Process(
        target=execute_python,
        args=(code, child)
    )
    job.start()

    output = ""
    start = time.time()

    while job.is_alive():
        if parent.poll():
            output += parent.recv()
        if time.time() - start > MAX_RUNTIME + 2:
            job.kill()
            break

    return jsonify({"output": output})


# ============================================================
# ANALYZE ENDPOINT (PASTE / FILE / ZIP)
# ============================================================

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        mode = request.form.get("mode")
        user = session.get("user")

        if mode == "paste":
            code = request.form.get("code", "")
            security = scan_security(code)

            if user:
                stats = get_user_stats(user)
                stats["scans"] += 1
                stats["threats"] += len(security)
                save_user_stats(user, stats)
                push_activity(user, f"🔍 Paste Scan • {len(security)} threats")

            return jsonify({
                "success": True,
                "static": analyze_code(code),
                "security": security,
                "duplicates": find_duplicates(code),
                "ai": run_ai_analysis(code)
            })

        if mode == "file":
            file = request.files.get("file")
            path = os.path.join(TEMP_FOLDER, "uploaded.py")
            file.save(path)

            code = read_file_as_text(path)
            security = scan_security(code)

            if user:
                stats = get_user_stats(user)
                stats["scans"] += 1
                stats["threats"] += len(security)
                save_user_stats(user, stats)
                push_activity(user, f"📄 File Scan • {file.filename}")

            return jsonify({
                "success": True,
                "static": analyze_code(code),
                "security": security,
                "duplicates": find_duplicates(code),
                "ai": run_ai_analysis(code)
            })

        if mode == "zip":
            file = request.files.get("file")
            zip_path = os.path.join(TEMP_FOLDER, "project.zip")
            extract_dir = os.path.join(TEMP_FOLDER, "unzipped")

            file.save(zip_path)
            extract_zip(zip_path, extract_dir)

            files = list_py_files(extract_dir)
            total_threats = 0

            for f in files:
                code = read_file_as_text(f)
                total_threats += len(scan_security(code))

            if user:
                stats = get_user_stats(user)
                stats["scans"] += len(files)
                stats["threats"] += total_threats
                save_user_stats(user, stats)
                push_activity(user, f"🗂 Project Scan • {total_threats} issues")

            return jsonify({"success": True})

        return jsonify({"error": "Invalid mode"})

    except Exception as e:
        return jsonify({"error": str(e)})


# ============================================================
# AUTH ROUTES
# ============================================================

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        users = load_users()
        username = request.form["user"]
        password = request.form["pass"]

        if username in users and check_password_hash(users[username], password):
            session["user"] = username
            return redirect("/dashboard")

        # ❌ SAME PAGE ERROR MESSAGE
        flash("❌ Invalid username or password", "error")
        return redirect("/login")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        users = load_users()
        username = request.form["user"]
        password = request.form["pass"]

        if username in users:
            return "⚠ User already exists"

        users[username] = generate_password_hash(password)
        save_users(users)
        return redirect("/login")

    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ============================================================
# MAIN PAGES
# ============================================================

@app.route("/dashboard")
def dashboard():
    return render_template("index.html")


@app.route("/playground")
def playground():
    return render_template("playground.html")


@app.route("/playground/ai", methods=["POST"])
def playground_ai():
    try:
        data = request.json
        code = data.get("code", "")
        question = data.get("message", "")

        if not code.strip():
            return jsonify({"reply": "⚠ No code provided"})

        prompt = (
            "You are a Python code analysis assistant.\n"
            "Explain the code step by step, highlight bugs and improvements.\n\n"
            f"CODE:\n{code}\n\nQUESTION:\n{question}"
        )

        reply = run_ai_chat(prompt)

        user = session.get("user")
        if user:
            stats = get_user_stats(user)
            stats["ai_chats"] += 1
            save_user_stats(user, stats)
            push_activity(user, "🤖 Playground AI used")

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"AI Error: {str(e)}"})


# ============================================================
# PROFILE PAGE (UPDATED, NO DATA LOSS)
# ============================================================

@app.route("/profile")
def profile():
    if not session.get("user"):
        return redirect("/login")

    user = session["user"]
    stats = get_user_stats(user)

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        activity=get_activity(user),
        score=calculate_analyzer_score(stats),
        analytics=build_profile_analytics(stats)
    )

@app.route("/profile/reset", methods=["POST"])
def reset_profile():
    if not session.get("user"):
        return jsonify({"success": False}), 401

    user = session.get("user")
    reset_user_data(user)

    return jsonify({"success": True})


def reset_user_data(username):
    users = load_users()

    users[username + "_stats"] = {
        "scans": 0,
        "threats": 0,
        "snippets": 0,
        "ai_chats": 0
    }

    users[username + "_activity"] = []

    save_users(users)

