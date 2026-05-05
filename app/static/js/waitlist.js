/**
 * Countdown Timer
 * Reads target date from a data attribute so Django can inject it server-side.
 * Usage: <div data-countdown="2025-09-01T00:00:00"></div>
 */
class Countdown {
    constructor(selector) {
        this.targets = document.querySelectorAll(selector);
        if (!this.targets.length) return;

        this.endDate = new Date(this.targets[0].dataset.countdown).getTime();
        if (isNaN(this.endDate)) {
            console.warn("Countdown: invalid date on", this.targets[0]);
            return;
        }

        this._tick();
        this._interval = setInterval(() => this._tick(), 1000);
    }

    _tick() {
        const delta = this.endDate - Date.now();

        if (delta <= 0) {
            clearInterval(this._interval);
            this._render(0, 0, 0, 0);
            return;
        }

        const days = Math.floor(delta / 864e5);
        const hours = Math.floor((delta % 864e5) / 36e5);
        const minutes = Math.floor((delta % 36e5) / 6e4);
        const seconds = Math.floor((delta % 6e4) / 1e3);

        this._render(days, hours, minutes, seconds);
    }

    _render(d, h, m, s) {
        this.targets.forEach(el => {
            // Expects children with [data-unit="days|hrs|mins|secs"]
            const set = (unit, val) => {
                const node = el.querySelector(`[data-unit="${unit}"]`);
                if (node) node.textContent = String(val).padStart(2, "0");
            };
            set("days", d);
            set("hrs", h);
            set("mins", m);
            set("secs", s);
        });
    }
}


/**
 * Waitlist Form Handler
 * Handles AJAX submission for any number of forms matching the selector.
 */
class WaitlistForm {
    constructor(selector, options = {}) {
        this.forms = document.querySelectorAll(selector);
        this.options = {
            endpoint: "/waiting-list/",
            onSuccess: this._defaultSuccess.bind(this),
            onError: this._defaultError.bind(this),
            ...options,
        };

        this.forms.forEach(form => this._bind(form));
    }

    /** Returns Django's CSRF token from the cookie. */
    _csrf() {
        return document.cookie
            .split("; ")
            .find(row => row.startsWith("csrftoken="))
            ?.split("=")[1] ?? "";
    }

    _bind(form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            const btn = form.querySelector("[type=submit]");
            const originalText = btn.textContent.trim();

            this._setLoading(btn, true);

            try {
                const res = await fetch(this.options.endpoint, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": this._csrf(),
                        "X-Requested-With": "XMLHttpRequest",
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(Object.fromEntries(new FormData(form))),
                });

                const data = await res.json();

                if (res.ok) {
                    this.options.onSuccess(form, data);
                } else {
                    this.options.onError(form, data);
                }
            } catch (err) {
                this.options.onError(form, { message: "Network error. Please try again." });
                console.error("Waitlist submission failed:", err);
            } finally {
                this._setLoading(btn, false, originalText);
            }
        });
    }

    _setLoading(btn, isLoading, originalText = "") {
        btn.disabled = isLoading;
        btn.textContent = isLoading ? "Joining…" : originalText;
        btn.classList.toggle("opacity-60", isLoading);
        btn.classList.toggle("cursor-not-allowed", isLoading);
    }

    _defaultSuccess(form, data) {
        // Replace the form with a confirmation message styled to match
        const msg = document.createElement("p");
        msg.className = "text-center text-emerald-400 font-semibold py-4 tracking-wide";
        msg.textContent = data.message ?? "You're on the list! We'll be in touch.";
        form.replaceWith(msg);
    }

    _defaultError(form, data) {
        // Show inline error beneath the form
        let err = form.querySelector(".js-form-error");
        if (!err) {
            err = document.createElement("p");
            err.className = "js-form-error text-rose-400 text-sm mt-3 text-center";
            form.appendChild(err);
        }
        err.textContent = data.message ?? "Something went wrong. Please try again.";
    }
}


document.addEventListener("DOMContentLoaded", () => {
    // Countdown — targets every [data-countdown] block on the page
    new Countdown("[data-countdown]");

    // Waitlist forms — targets both the hero form and the CTA form
    new WaitlistForm(".js-waitlist-form");
});