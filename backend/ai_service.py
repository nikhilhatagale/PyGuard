import json
import re
from .errors import AIServiceError
from .config import GROQ_API_KEY
from groq import Groq

client = Groq(api_key=GROQ_API_KEY)



# ============================================================
# ULTRA-STABLE JSON EXTRACTOR
# ============================================================
def extract_json(text: str):
    """
    Extracts ONLY the JSON object from the LLM output.
    Works even if AI prints:
    ✔ Markdown
    ✔ Extra explanations
    ✔ Extra braces
    ✔ Wrong formatting
    """

    # Remove code fences
    text = text.replace("```json", "").replace("```", "").strip()

    # Find JSON region
    start = text.find("{")
    end = text.rfind("}") + 1

    if start == -1 or end == -1:
        raise AIServiceError("AI did not output JSON.")

    chunk = text[start:end]

    # Remove trailing commas
    chunk = re.sub(r",\s*}", "}", chunk)
    chunk = re.sub(r",\s*]", "]", chunk)

    # Remove double spaces/newlines
    chunk = chunk.replace("\n", " ")

    try:
        return json.loads(chunk)
    except Exception:
        raise AIServiceError("AI returned invalid JSON format.")

def run_ai_chat(message: str, code_context: str = ""):
    """
    Clean AI assistant for chat-style help.
    Output is structured for frontend rendering.
    """

    prompt = f"""
You are PyGuard AI, a senior Python developer.

YOU MUST FOLLOW THIS OUTPUT FORMAT EXACTLY.
DO NOT SKIP ANY SECTION.

If you do not follow the format, your response is invalid.

========================
EXPLANATION:
(Write 3–5 clear bullet points explaining what the code does)

CODE:
```python
(Write clean, runnable Python code)

USER QUESTION:
{message}

USER CODE (if any):
{code_context}

RESPONSE FORMAT (FOLLOW EXACTLY):

EXPLANATION:
<2–4 lines, simple and clear>

CODE:
<ONLY code here, no explanation>

NOTES:
<optional tips or edge cases>
"""

    try:
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=900
        )
        return res.choices[0].message.content.strip()

    except Exception as e:
        return f"Error processing request: {e}"


# ============================================================
# MAIN AI ENGINE — 100% STABLE JSON MODE
# ============================================================
def run_ai_analysis(code: str):

    if not code.strip():
        return {
            "summary": "No code provided",
            "suggestions": [],
            "improved_code": "",
            "minimized_code": "",
            "optimizations": []
        }

    system_force_json = """
You MUST return ONLY valid JSON.
No text before JSON.
No text after JSON.
No markdown.
No explanation.
No comments.
"""

    prompt = f"""
Analyze the Python code and output EXACT JSON ONLY.

Python Code:
---------------------
{code}
---------------------

Return JSON exactly in this schema:

{{
  "summary": "<short summary>",
  "suggestions": ["s1", "s2"],
  "improved_code": "<PEP8 version>",
  "minimized_code": "<shortest equivalent version>",
  "optimizations": ["o1", "o2"]
}}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_force_json},
                {"role": "user", "content": prompt},
            ],
            temperature = 0.15,
            max_tokens = 1800
        )

        raw = response.choices[0].message.content.strip()

        data = extract_json(raw)

        return {
            "summary": data.get("summary", "No summary"),
            "suggestions": data.get("suggestions", []),
            "improved_code": data.get("improved_code", code),
            "minimized_code": data.get("minimized_code", ""),
            "optimizations": data.get("optimizations", [])
        }

    except Exception as e:
        # Never break UI
        return {
            "summary": f"AI error: {e}",
            "suggestions": [],
            "improved_code": "",
            "minimized_code": "",
            "optimizations": []
        }

# ===========================================================
# FINAL TOOL FUNCTIONS (Now app.py will detect them properly)
# ===========================================================

def ai_refactor_code(code: str):
    res = run_ai_analysis(code)
    return res.get("improved_code","")

def ai_minimize_code(code: str):
    res = run_ai_analysis(code)
    return res.get("minimized_code","")

def ai_fix_code(code: str):
    res = run_ai_analysis(code)
    return res.get("improved_code","")   # fix = improved clean version

def ai_generate_tests(code: str):
    res = run_ai_analysis(code)
    return res.get("tests","No tests generated")

def ai_performance_review(code: str):
    res = run_ai_analysis(code)
    return "\n".join(res.get("optimizations",[])) or "No optimization issues"
