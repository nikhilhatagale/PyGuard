# ============================================================
#  FINAL WORKING ASSISTANT API (STABLE + SAFE)
# ============================================================

from flask import Blueprint, request, jsonify
from groq import Groq
from .config import GROQ_API_KEY

assistant_bp = Blueprint("assistant_bp", __name__)

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """
You are PyGuard Assistant.
Help debug code, explain errors, improve performance.
Response must be short, smart and accurate.
"""

@assistant_bp.route("/assistant", methods=["POST"])
def assistant_reply():
    try:
        data = request.get_json(silent=True) or {}
        msg = (data.get("message") or "").strip()

        if not msg:
            return jsonify({"reply": "Write something first."})

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": msg}
            ],
            temperature=0.3,
            max_tokens=500
        )

        content = response.choices[0].message.content

        return jsonify({
            "reply": content.strip() if content else "⚠ AI returned empty response."
        })

    except Exception as e:
        return jsonify({
            "reply": f"⚠ Assistant Error: {str(e)}"
        })
