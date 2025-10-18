document.addEventListener("alpine:init", () => {
  // Main menu interactions (dropdowns, etc.)
  Alpine.data("menu", () => ({
    selected: "", // stores currently opened menu section
    select(menu) {
      this.selected = this.selected === menu ? "" : menu;
    },
  }));
  console.log("Menu data read");

  // Theme (dark/light mode)
  Alpine.data("themeHandler", () => ({
    darkMode: JSON.parse(localStorage.getItem("darkMode")) || false,
    toggleDarkMode() {
      this.darkMode = !this.darkMode;
      localStorage.setItem("darkMode", JSON.stringify(this.darkMode));
      document.documentElement.classList.toggle("dark", this.darkMode);
    },
  }));
  console.log("inside alpine:int listener");
});
