let playgroundEditor;

/* ===============================
   INIT CODEMIRROR
================================ */
document.addEventListener("DOMContentLoaded", () => {

  function initWhenReady() {
    const runBtn = document.getElementById("run-btn");
    if (!runBtn) {
      return setTimeout(initWhenReady, 200);
    }

    playgroundEditor = CodeMirror(
      document.getElementById("pg-editor"),
      {
        mode: "python",
        lineNumbers: true,
        theme: "default"
      }
    );

    loadIncomingCode();

    runBtn.addEventListener("click", runCode);
    document.getElementById("clear-btn")?.addEventListener("click", clearConsole);
    document.getElementById("ask-ai-btn")?.addEventListener("click", askAI);
  }

  initWhenReady();
});

/* ===============================
   LOAD CODE FROM DASHBOARD / ANALYZER
================================ */
function loadIncomingCode() {
  const stored = sessionStorage.getItem("play_code");

  if (stored && playgroundEditor) {
    playgroundEditor.setValue(stored);
    writeConsole("🔥 Code loaded from Dashboard\n");
    sessionStorage.removeItem("play_code");
  }
}

/* ===============================
   RUN CODE
================================ */
async function runCode() {
  const code = playgroundEditor.getValue();
  writeConsole("▶ Running...\n");

  const res = await fetch("/run-code", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code })
  });

  const data = await res.json();
  writeConsole(data.output + "\n");
}

/* ===============================
   AI EXPLAIN CODE
================================ */
async function askAI() {
  const code = playgroundEditor.getValue();
  writeConsole("\n🤖 Thinking...\n");

  const res = await fetch("/playground/ai", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: "Explain this code properly",
      code: code
    })
  });

  const data = await res.json();
  writeConsole("\n=== AI Reply ===\n" + data.reply + "\n");
}

/* ===============================
   CONSOLE UTILS
================================ */
function clearConsole() {
  document.getElementById("pg-console").textContent = "";
}

function writeConsole(text) {
  const con = document.getElementById("pg-console");
  con.textContent += text;
  con.scrollTop = con.scrollHeight;
}
