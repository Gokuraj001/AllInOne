// ================= FORCE THEME (DOUBLE SAFETY) =================
document.addEventListener("DOMContentLoaded", () => {
  const savedTheme = localStorage.getItem("theme") || "dark";
  document.documentElement.setAttribute("data-theme", savedTheme);

  updateIcon(savedTheme);
});

// ================= TOGGLE =================
function toggleMode() {
  let currentTheme = document.documentElement.getAttribute("data-theme");

  if (!currentTheme) currentTheme = "dark";

  const newTheme = currentTheme === "dark" ? "light" : "dark";

  document.documentElement.setAttribute("data-theme", newTheme);
  localStorage.setItem("theme", newTheme);

  updateIcon(newTheme);
}

// ================= ICON =================
function updateIcon(theme) {
  const icon = document.getElementById("floatIcon");
  if (icon) {
    icon.textContent = theme === "dark" ? "🌙" : "☀️";
  }
}