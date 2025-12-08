document.addEventListener("alpine:init", () => {
  // Main menu interactions (dropdowns, etc.)
  Alpine.data("menu", () => ({
    selected: "", // stores currently opened menu section
    select(menu) {
      this.selected = this.selected === menu ? "" : menu;
    },
  }));
  
// Modal management
  Alpine.store("modals", {
  profile: false,
  address: false,
  socials: false,

  // optional: helper methods
  open(modalName) {
    this[modalName] = true;
  },
  close(modalName) {
    this[modalName] = false;
  },
  toggle(modalName) {
    this[modalName] = !this[modalName];
  },
  closeAll() {
    this.profile = false;
    this.address = false;
    this.socials = false;
  }
});

  // Theme (dark/light mode)
  Alpine.data("themeHandler", () => ({
    darkMode: JSON.parse(localStorage.getItem("darkMode")) || false,
    toggleDarkMode() {
      this.darkMode = !this.darkMode;
      localStorage.setItem("darkMode", JSON.stringify(this.darkMode));
      document.documentElement.classList.toggle("dark", this.darkMode);
    },
  }));
  
});

