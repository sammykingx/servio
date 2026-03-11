document.addEventListener("alpine:init", () => {
    // Main menu interactions (dropdowns, etc.)
    Alpine.data("menu", () => ({
        selected: "",
        select(menu) {
            this.selected = this.selected === menu ? "" : menu;
        },
    }));

    Alpine.data('projectDates', () => ({
        startDate: '',
        goLiveDate: '',

        // Today in YYYY-MM-DD
        get today() {
            return this.formatDate(new Date());
        },

        // Go live must be start date + 1 day
        get goLiveMinDate() {
            if (!this.startDate) return '';
            return this.addDays(this.startDate, 1);
        },

        // Utilities (pure functions)
        formatDate(date) {
            return date.toISOString().split('T')[0];
        },

        addDays(dateString, days) {
            const date = new Date(dateString);
            date.setDate(date.getDate() + days);
            return this.formatDate(date);
        }
    }));

    Alpine.store("dropdown", {
        openId: null,

        toggle(id) {
            this.openId = this.openId === id ? null : id;
        },

        close() {
            this.openId = null;
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