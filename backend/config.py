import os
from dotenv import load_dotenv

# ============================================================
# BASE DIRECTORY
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# LOAD .env (FORCE OVERRIDE WINDOWS ENV)
# ============================================================
ENV_PATH = os.path.join(BASE_DIR, "..", ".env")

if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH, override=True)
else:
    raise RuntimeError(f"❌ .env file not found at: {ENV_PATH}")

# ============================================================
# GROQ API KEY (SINGLE SOURCE OF TRUTH)
# ============================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY or not GROQ_API_KEY.startswith("gsk_"):
    raise RuntimeError(
        "❌ GROQ_API_KEY missing or invalid.\n"
        "➡️ Check .env file\n"
        "➡️ Ensure Windows ENV is NOT overriding it"
    )

# ============================================================
# LOGGING
# ============================================================
LOG_FOLDER = os.path.join(BASE_DIR, "..", "logs")
os.makedirs(LOG_FOLDER, exist_ok=True)

LOG_FILE = os.path.join(LOG_FOLDER, "app.log")

# ============================================================
# TEMP / UPLOAD PATHS
# ============================================================
TEMP_FOLDER = os.path.join(BASE_DIR, "temp")
os.makedirs(TEMP_FOLDER, exist_ok=True)

# ============================================================
# SECURITY LIMITS
# ============================================================
ALLOWED_EXTENSIONS = {".py", ".zip"}
MAX_FILE_SIZE_MB = 5
