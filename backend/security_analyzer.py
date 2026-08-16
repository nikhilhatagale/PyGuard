import re

def scan_security(code: str):
    issues = []
    lines = code.splitlines()

    # -----------------------
    # exec() detection
    # -----------------------
    for i, line in enumerate(lines, 1):
        if "exec(" in line:
            issues.append({
                "line": i,
                "severity": "high",
                "message": "Dangerous use of exec(). Avoid executing dynamic strings."
            })

    # -----------------------
    # eval() detection
    # -----------------------
    for i, line in enumerate(lines, 1):
        if "eval(" in line:
            issues.append({
                "line": i,
                "severity": "medium",
                "message": "Use of eval() is unsafe and can lead to code injection."
            })

    # -----------------------
    # os.system(), subprocess, shell=True
    # -----------------------
    for i, line in enumerate(lines, 1):
        if ("os.system(" in line) or ("subprocess" in line and "shell=True" in line):
            issues.append({
                "line": i,
                "severity": "high",
                "message": "Command execution detected (os.system or subprocess shell=True)."
            })

    # -----------------------
    # Hardcoded passwords / tokens
    # -----------------------
    pwd_regex = r"(password|passwd|token|secret)\s*=\s*['\"].+['\"]"

    for i, line in enumerate(lines, 1):
        if re.search(pwd_regex, line, re.IGNORECASE):
            issues.append({
                "line": i,
                "severity": "medium",
                "message": "Possible hard-coded password or secret found."
            })

    return issues
