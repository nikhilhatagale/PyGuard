document.addEventListener("DOMContentLoaded", () => {

  /* ===========================
     BASIC ELEMENTS
  ============================ */
  const bubble = document.getElementById("assistant-bubble");
  const overlay = document.getElementById("assistant-overlay");
  const modal = document.getElementById("assistant-modal");
  const closeBtn = document.getElementById("assistant-close");

  const chat = document.getElementById("assistant-chat");
  const input = document.getElementById("assistant-input");
  const send = document.getElementById("assistant-send");

  const micBtn = document.getElementById("assistant-mic");
  const fileInput = document.getElementById("assistant-file-input");


  /* ===========================
     OPEN / CLOSE
  ============================ */
  bubble?.addEventListener("click", openAssistant);
  closeBtn?.addEventListener("click", closeAssistant);
  overlay?.addEventListener("click", closeAssistant);

  function openAssistant() {
    document.body.classList.add("assistant-open");
    input?.focus();
  }

  function closeAssistant() {
    document.body.classList.remove("assistant-open");
  }

  /* ===========================
     SEND MESSAGE
  ============================ */
  send?.addEventListener("click", sendMessage);
  input?.addEventListener("keydown", e => {
    if (e.key === "Enter") sendMessage();
    if (e.key === "Escape") closeAssistant();
  });

  async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;

    addMessage(text, "u");
    input.value = "";

    const thinking = addMessage("Thinking...", "a");

    try {
      const res = await fetch("/assistant", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text })
      });

      const data = await res.json();
      thinking.remove();

      addMessage(data.reply || "⚠️ No response", "a");

    } catch (err) {
      thinking.remove();
      addMessage("⚠️ Server error", "a");
      console.error(err);
    }
  }

  /* ===========================
     ADD MESSAGE (CODE + COPY)
  ============================ */
  function addMessage(text, type) {
    const msg = document.createElement("div");
    msg.className = type === "u" ? "msg-u" : "msg-a";

    const codeRegex = /```([\s\S]*?)```/;
    const match = text.match(codeRegex);

    if (match) {
      const before = text.split("```")[0].trim();
      if (before) {
        const p = document.createElement("p");
        p.textContent = before;
        msg.appendChild(p);
      }

      const pre = document.createElement("pre");
      pre.className = "code-box";

      const code = document.createElement("code");
      code.textContent = match[1];

      const copyBtn = document.createElement("button");
      copyBtn.className = "copy-btn";
      copyBtn.textContent = "Copy";

      copyBtn.onclick = () => {
        navigator.clipboard.writeText(match[1]);
        copyBtn.textContent = "Copied!";
        setTimeout(() => copyBtn.textContent = "Copy", 1200);
      };

      pre.appendChild(copyBtn);
      pre.appendChild(code);
      msg.appendChild(pre);
    } else {
      msg.textContent = text;
    }

    chat.appendChild(msg);
    msg.scrollIntoView({ behavior: "smooth" });
    return msg; // 🔥 REQUIRED
  }

  /* ===========================
     MIC INPUT (WORKING)
  ============================ */
  if (micBtn && ("SpeechRecognition" in window || "webkitSpeechRecognition" in window)) {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";

    micBtn.addEventListener("click", () => {
      recognition.start();
      micBtn.classList.add("listening");
    });

    recognition.onresult = e => {
      input.value = e.results[0][0].transcript;
      micBtn.classList.remove("listening");
    };

    recognition.onerror = () => {
      micBtn.classList.remove("listening");
    };
  }


});
