

document.addEventListener("DOMContentLoaded", () => {
    const themeToggle = document.getElementById("theme-toggle");
    const themeLink = document.getElementById("theme-link");

    themeToggle.addEventListener("click", () => {
        const isDark = themeLink.getAttribute("href").includes("theme_dark.css");

        if (isDark) {
            themeLink.setAttribute("href", "/static/css/theme_light.css");
            themeToggle.innerHTML = "🌙 Dark";
        } else {
            themeLink.setAttribute("href", "/static/css/theme_dark.css");
            themeToggle.innerHTML = "☀ Light";
        }
    });

    initAnalyzeButton();
    initResetButton();
    initAiLoadButtons();
    initModeSwitch();
    initSidebarSwitch();
    initAiLoadButtons();
});

/* -----------------------------------------------
   SIDEBAR SWITCH (FULL EDITOR / SPLIT MODE)
-------------------------------------------------- */
function initSidebarSwitch() {
    const sideItems = document.querySelectorAll(".side-item");
    const layout = document.getElementById("layout");
    const resultsPanel = document.getElementById("results-panel");
    const resultBoxes = document.querySelectorAll(".results-box");

    layout.classList.add("full-editor");  // default

    sideItems.forEach(item => {
        item.addEventListener("click", () => {

            const target = item.dataset.target;

            sideItems.forEach(i => i.classList.remove("active"));
            item.classList.add("active");

            if (target === "editor-panel") {
                layout.classList.add("full-editor");
                resultsPanel.classList.add("hidden");
                resultBoxes.forEach(b => b.classList.add("hidden"));
                return;
            }

            layout.classList.remove("full-editor");
            resultsPanel.classList.remove("hidden");

            // hide all boxes
            resultBoxes.forEach(b => b.classList.add("hidden"));

            // show selected
            document.getElementById(target)?.classList.remove("hidden");
        });
    });
}

/* -------------------------------------- */
function initModeSwitch() {
    const paste = document.getElementById("paste-panel");
    const file = document.getElementById("file-panel");

    document.querySelectorAll("input[name='mode']").forEach(r => {
        r.addEventListener("change", () => {
            const mode = document.querySelector("input[name='mode']:checked").value;

            paste.classList.toggle("hidden", mode !== "paste");
            file.classList.toggle("hidden", mode !== "file");
        });
    });
}

    // File Upload → Load into Editor
    const fileInput = document.getElementById("hidden-file");
    if (fileInput) {
        fileInput.addEventListener("change", async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const code = await file.text();
            setCode(code);

            document.getElementById("status").textContent =
                "✓ File loaded into editor";
        });
    }

function syncEditor() {
    document.getElementById("code-textarea").value = getCode();
}

/* -------------------------------------- */
function initAnalyzeButton() {
    if (window.ANALYZER_DISABLED) return;   // Playground safety

    const btn = document.getElementById("analyze-btn");
    const status = document.getElementById("status");

    if (!btn) return;

    btn.addEventListener("click", async () => {

        // 🔹 Sync editor content
        syncEditor();
        const code = getCode();

        // 🔴 EMPTY CODE GUARD (MAIN FIX)
        if (!code || !code.trim()) {
            status.textContent = "⚠️ Please enter Python code before analysis";
            status.style.color = "#ff4b4b";
            return; // ⛔ stop here, no API call
        }

        // reset status color if previously error
        status.style.color = "";

        const fd = new FormData();
        fd.append("mode", "paste");
        fd.append("code", code);

        status.textContent = "Analyzing...";

        const res = await fetch("/analyze", {
            method: "POST",
            body: fd
        });

        const data = await res.json();

        status.textContent = "✔ Analysis Complete";

        renderStatic(data);
        renderSecurity(data);
        renderDuplicate(data);
        renderAi(data.ai);
    });
}



/* -------------------------------------- */
function renderStatic(data) {
    const s = data.static;
    const box = document.getElementById("static-output");

    const syntaxBadge = s.syntax_ok
        ? `<span class="ok">✔ Passed Syntax Validation</span>`
        : `<span class="bad">❌ Syntax Errors Found</span>`;

    box.innerHTML = `
        <div class="sa-card">

            <div class="sa-row">
                <h3>Analysis Summary</h3>
                ${syntaxBadge}
            </div>

            <div class="sa-metrics">
                <div>
                    Total Lines of Code
                    <span>${s.total_lines}</span>
                </div>

                <div>
                    Total Functions Defined
                    <span>${s.total_functions}</span>
                </div>

                <div>
                    Largest Function Length
                    <span>${s.max_function_length}</span>
                </div>

                <div>
                    Warning Count
                    <span>${s.warnings.length}</span>
                </div>
            </div>

        </div>
    `;

    /* Dynamic warnings */
    if (s.warnings.length > 0) {
        s.warnings.forEach(w => {
            box.innerHTML += `
                <div class="issue-item bad">
                    ⚠ ${w}
                </div>
            `;
        });
    }
}

function renderSecurity(data){
    const box = document.getElementById("security-output");
    box.innerHTML = "";

    if(!data.security || data.security.length === 0){
        box.innerHTML = `<div class="empty">✅ No security issues found</div>`;
        return;
    }

    data.security.forEach(i=>{
        const sev = i.severity.toLowerCase();
        const icon = sev === "high" ? "🔥" : sev === "medium" ? "⚠️" : "✅";

        box.innerHTML += `
            <div class="sec-item">
                <div class="sec-icon">${icon}</div>

                <div>
                    <div class="sec-msg">${i.message}</div>
                    <div class="sec-line">Line ${i.line}</div>
                </div>

                <div class="sec-badge sec-${sev}">
                    ${i.severity.toUpperCase()}
                </div>
            </div>
        `;
    });
}

function renderDuplicate(data){
    const box = document.getElementById("duplicate-output");
    box.innerHTML = "";

    if(!data.duplicates || data.duplicates.length === 0){
        box.innerHTML = "<p style='opacity:.6'>No duplicate code found 🎉</p>";
        return;
    }

    data.duplicates.forEach(d => {
        box.innerHTML += `
        <div class="dup-card">
          <div class="dup-header">
            <span class="dup-icon">🔁</span>
            <span class="dup-title">Duplicate Code</span>
            <span class="dup-lines">Line ${d.line_original} → ${d.line_duplicate}</span>
          </div>
          <div class="dup-body">
            <div class="dup-label">Duplicated Snippet</div>
            <pre class="dup-code">${d.text}</pre>
          </div>
        </div>
        `;
    });
}


function renderAi(ai) {
    if (!ai) return;

    document.getElementById("ai-summary").textContent = ai.summary ?? "";
    document.getElementById("ai-suggestions").innerHTML =
        (ai.suggestions || []).map(s => `<li>${s}</li>`).join("");

    document.querySelector("#ai-code-block code").textContent =
        ai.improved_code ?? "";

    document.querySelector("#ai-minimize-block code").textContent =
        ai.minimized_code ?? "";

    document.getElementById("ai-optimizations").innerHTML =
        (ai.optimizations || []).map(o => `<li>${o}</li>`).join("");
}

/* -------------------------------------- */
function initAiLoadButtons() {
    document.getElementById("load-ai").addEventListener("click", () => {
        setCode(document.querySelector("#ai-code-block code").textContent);
    });

    document.getElementById("load-ai-min").addEventListener("click", () => {
        setCode(document.querySelector("#ai-minimize-block code").textContent);
    });
}

/* -------------------------------------- */
function initResetButton() {
    document.getElementById("reset-btn").addEventListener("click", () => {
        setCode("");
        document.getElementById("static-output").textContent = "";
        document.getElementById("security-output").textContent = "";
        document.getElementById("duplicate-output").textContent = "";
        document.getElementById("ai-summary").textContent = "";
        document.getElementById("ai-suggestions").innerHTML = "";
        document.querySelector("#ai-code-block code").textContent = "";
        document.querySelector("#ai-minimize-block code").textContent = "";
        document.getElementById("ai-optimizations").innerHTML = "";
        document.getElementById("status").textContent = "";
    });
}

document.querySelectorAll(".ai-node").forEach(node => {

    node.addEventListener("click",async () => {
        let tool=node.dataset.tool;
        let code=getCode();

        node.classList.toggle("open");
        let output=document.getElementById("out-"+tool);
        output.style.display= output.style.display==="block"?"none":"block";

        const res = await fetch("/ai/tool",{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({tool,code})
        });

        let data=await res.json();
        output.textContent=data.response || "No response";
    });

});


// ============= AI PANEL EXPAND / LOAD CONTROL =============
document.querySelectorAll(".ai-toggle").forEach(t => {
    t.addEventListener("click", () => {
        const box = document.getElementById(t.dataset.box);
        box.style.display = (box.style.display === "block") ? "none" : "block";
    });
});

// Load AI result into Editor
document.querySelectorAll(".ai-load-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        const type = btn.dataset.load;
        let map = {
            refactor: "refactor-box",
            minimize: "minimize-box",
            fix: "fix-box",
            tests: "test-box"
        };
        setCode(document.getElementById(map[type]).textContent);
    });
});

// Catch AI Response & Render into Sections
function renderAI(data) {
    document.getElementById("refactor-box").textContent = data.improved_code;
    document.getElementById("minimize-box").textContent = data.minimized_code;
    document.getElementById("fix-box").textContent = data.auto_fixed;
    document.getElementById("test-box").textContent = data.tests;
    document.getElementById("perf-box").textContent = (data.optimizations||[]).join("\n");
    document.getElementById("explain-box").textContent = data.summary;
}
