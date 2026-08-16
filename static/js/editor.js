let editor;

document.addEventListener("DOMContentLoaded", () => {
    editor = CodeMirror(document.getElementById("code-editor"), {
        mode: "python",
        lineNumbers: true,
        theme: "dracula",
        tabSize: 4,
        indentUnit: 4
    });
});

function getCode() {
    return editor.getValue();
}

function setCode(text) {
    editor.setValue(text);
}


/* ----------------------------------------------------------
   SYNC EDITOR -> HIDDEN TEXTAREA (backend needs this)
----------------------------------------------------------- */
function syncEditorToForm() {
    const textarea = document.getElementById("code-textarea");
    if (textarea && editor) {
        textarea.value = editor.getValue();
    }
}


/* ----------------------------------------------------------
   THEME SWITCHING (dark <-> light)
----------------------------------------------------------- */
function applyEditorTheme(themeName) {
    if (!editor) return;
    editor.setOption("theme", themeName);

    setTimeout(() => editor.refresh(), 100);
}


/* ----------------------------------------------------------
   EXPORT: editor object (optional)
----------------------------------------------------------- */
window._editor = editor;
