/* ===============================
   RESET PROFILE ANALYTICS
================================ */

function resetProfile(){
  if(!confirm("This will reset all your analytics. Continue?")) return;

  fetch("/profile/reset", { method:"POST" })
    .then(r => r.json())
    .then(d => {
      if(d.success){
        alert("Analytics reset successfully");
        location.reload();
      } else {
        alert("Reset failed");
      }
    })
    .catch(err => {
      console.error(err);
      alert("Server error");
    });
}

/* ===============================
   PROFILE THEME SYNC WITH NAVBAR
================================ */

document.addEventListener("DOMContentLoaded", () => {
  const profileRoot = document.querySelector(".profile-root");
  const toggleBtn = document.getElementById("theme-toggle");

  if(!profileRoot || !toggleBtn) return;

  // initial sync
  profileRoot.classList.toggle(
    "light",
    document.body.classList.contains("light")
  );

  const observer = new MutationObserver(() => {
    profileRoot.classList.toggle(
      "light",
      document.body.classList.contains("light")
    );
  });

  observer.observe(document.body, {
    attributes: true,
    attributeFilter: ["class"]
  });
});
