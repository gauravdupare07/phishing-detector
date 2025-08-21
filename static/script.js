document.addEventListener("DOMContentLoaded", () => {
  const body = document.body;
  const themeButton = document.getElementById("themeButton");

  // Load saved theme
  if (localStorage.getItem("theme") === "dark") {
    body.classList.add("dark");
    themeButton.textContent = "☀️ Light Mode";
  }

  themeButton.addEventListener("click", () => {
    body.classList.toggle("dark");
    if (body.classList.contains("dark")) {
      themeButton.textContent = "☀️ Light Mode";
      localStorage.setItem("theme", "dark");
    } else {
      themeButton.textContent = "🌙 Dark Mode";
      localStorage.setItem("theme", "light");
    }
  });
});
