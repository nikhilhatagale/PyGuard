document.addEventListener("DOMContentLoaded", () => {

    const imp = document.getElementById("load-improved");
    if (imp) {
        imp.addEventListener("click", () => {
            const code = document.querySelector("#ai-code-block code")?.innerText.trim();
            if (!code) return alert("⚠ No improved code available");

            sessionStorage.setItem("play_code", code);
            window.location.href = "/playground";
        });
    }

    const min = document.getElementById("load-minimized");
    if (min) {
        min.addEventListener("click", () => {
            const code = document.querySelector("#ai-minimize-block code")?.innerText.trim();
            if (!code) return alert("⚠ No minimized code available");

            sessionStorage.setItem("play_code", code);
            window.location.href = "/playground";
        });
    }

});
