document.addEventListener("DOMContentLoaded", () => {

    const sideItems = document.querySelectorAll(".side-item");
    const layout = document.querySelector(".pro-layout");
    const editorPanel = document.getElementById("editor-panel");
    const resultsPanel = document.getElementById("results-panel");
    const resultsBoxes = document.querySelectorAll(".results-box");

    // Default = full editor
    layout.classList.add("full-editor");
    resultsPanel.classList.add("hidden");

    sideItems.forEach(item => {
        item.addEventListener("click", () => {

            const target = item.dataset.target;

            // active highlight
            sideItems.forEach(s => s.classList.remove("active"));
            item.classList.add("active");

            // EDITOR MODE
            if (target === "editor-panel") {
                layout.classList.add("full-editor");
                resultsPanel.classList.add("hidden");

                resultsBoxes.forEach(b => b.classList.add("hidden"));
                return;
            }

            // RESULT MODE
            layout.classList.remove("full-editor");
            resultsPanel.classList.remove("hidden");

            // hide all result boxes
            resultsBoxes.forEach(b => b.classList.add("hidden"));

            // show selected result box
            const box = document.getElementById(target);
            if (box) {
                box.classList.remove("hidden");
            }
        });
    });


    // ============================
    // MODE SWITCH (paste/file)
    // ============================
    const pastePanel = document.getElementById("paste-panel");
    const filePanel  = document.getElementById("file-panel");

    document.querySelectorAll("input[name='mode']").forEach(radio => {
        radio.addEventListener("change", () => {
            if (radio.value === "paste") {
                pastePanel.classList.remove("hidden");
                filePanel.classList.add("hidden");
            } else {
                pastePanel.classList.add("hidden");
                filePanel.classList.remove("hidden");
            }
        });
    });

});

