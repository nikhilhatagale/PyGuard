import os
import zipfile
import shutil
from .errors import ValidationError


# ===========================
# READ A PYTHON FILE SAFELY
# ===========================
def read_file_as_text(file_path: str) -> str:
    if not os.path.isfile(file_path):
        raise ValidationError(f"File not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        raise ValidationError(f"Unable to read file: {e}")


# ===========================
# SECURE ZIP EXTRACTION
# No path traversal
# No overwriting outside folder
# ===========================
def extract_zip(zip_path: str, extract_to: str):
    if not zipfile.is_zipfile(zip_path):
        raise ValidationError("Invalid ZIP file.")

    # Clean old folder to avoid duplicates or conflicts
    if os.path.exists(extract_to):
        shutil.rmtree(extract_to)

    os.makedirs(extract_to, exist_ok=True)

    def is_safe(member, base):
        abs_target = os.path.abspath(os.path.join(base, member))
        abs_base = os.path.abspath(base)
        return abs_target.startswith(abs_base)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        for member in zip_ref.namelist():

            if not is_safe(member, extract_to):
                raise ValidationError(f"Unsafe path detected inside ZIP: {member}")

            # Only extract .py files and folders
            if member.endswith(".py") or member.endswith("/"):
                zip_ref.extract(member, extract_to)

    return extract_to


# ===========================
# LIST ALL PYTHON FILES
# ===========================
def list_py_files(root_dir: str):
    py_files = []
    for root, _, files in os.walk(root_dir):
        for f in files:
            if f.endswith(".py"):
                full_path = os.path.join(root, f)
                py_files.append(full_path)

    return py_files
