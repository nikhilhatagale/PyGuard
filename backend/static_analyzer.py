import ast
from .errors import AnalysisError


def analyze_code(code: str):
    """
    SAFE Static Analyzer
    - Syntax check (no crash)
    - Function stats
    - Warnings (unused vars, empty functions, duplicate names)
    """

    result = {
        "syntax_ok": True,
        "syntax_errors": [],
        "total_lines": 0,
        "total_functions": 0,
        "max_function_length": 0,
        "warnings": [],
        "issues": []
    }

    # ----------------------------------------------------
    # 1. COUNT LINES
    # ----------------------------------------------------
    result["total_lines"] = len(code.splitlines())

    # ----------------------------------------------------
    # 2. PARSE CODE → SYNTAX CHECK FIRST
    # ----------------------------------------------------
    try:
        tree = ast.parse(code)

    except SyntaxError as e:
        # DON'T CRASH — return syntax error to UI
        result["syntax_ok"] = False
        result["syntax_errors"].append({
            "line": e.lineno,
            "column": e.offset,
            "text": e.text.strip() if e.text else "",
            "message": e.msg
        })
        return result

    except Exception as e:
        # Unknown cases
        raise AnalysisError(f"Invalid Python code: {e}")

    # ----------------------------------------------------
    # 3. FUNCTION INFO
    # ----------------------------------------------------
    functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    result["total_functions"] = len(functions)

    func_lengths = []
    for f in functions:
        try:
            start = f.lineno
            end = f.body[-1].lineno if f.body else f.lineno
            func_lengths.append(end - start)
        except:
            pass

    result["max_function_length"] = max(func_lengths) if func_lengths else 0

    # ----------------------------------------------------
    # 4. WARNINGS SYSTEM
    # ----------------------------------------------------

    # 4A — Empty functions
    for f in functions:
        if len(f.body) == 1 and isinstance(f.body[0], ast.Pass):
            result["warnings"].append(
                f"Function '{f.name}' is empty."
            )

    # 4B — Duplicate function names
    name_counter = {}
    for f in functions:
        name_counter[f.name] = name_counter.get(f.name, 0) + 1

    for name, count in name_counter.items():
        if count > 1:
            result["warnings"].append(
                f"Duplicate function name '{name}' used {count} times."
            )

    # 4C — Unused variables detection
    assigned = set()
    used = set()

    class VarTracker(ast.NodeVisitor):
        def visit_Name(self, node):
            if isinstance(node.ctx, ast.Store):
                assigned.add(node.id)
            elif isinstance(node.ctx, ast.Load):
                used.add(node.id)
            self.generic_visit(node)

    VarTracker().visit(tree)

    for var in assigned:
        if var not in used and not var.startswith("_"):
            result["warnings"].append(
                f"Variable '{var}' assigned but never used."
            )

    # ----------------------------------------------------
    # 5. FINAL RETURN
    # ----------------------------------------------------
    return result
