/**
 * Servio Infrastructure Core
 * Modules: ToastManager, CountdownTimer, WaitlistUI
 */

class ToastManager {
    constructor(containerId = 'toast-container') {
        this.container = document.getElementById(containerId);
        this.config = {
            success: { color: 'border-emerald-500/50 bg-emerald-500/10 text-emerald-400', icon: 'check_circle' },
            error: { color: 'border-rose-500/50 bg-rose-500/10 text-rose-400', icon: 'error' }
        };
    }

    show(message, type = 'success') {
        const settings = this.config[type];
        const toast = document.createElement('div');

        toast.className = `pointer-events-auto flex items-center gap-3 px-6 py-4 rounded-2xl border backdrop-blur-xl shadow-2xl transition-all duration-500 translate-x-full opacity-0 ${settings.color}`;
        toast.innerHTML = `
            <span class="material-symbols-outlined text-xl">${settings.icon}</span>
            <p class="text-sm font-bold tracking-wide">${message}</p>
        `;

        this.container.appendChild(toast);

        // Trigger Animation
        requestAnimationFrame(() => {
            toast.classList.replace('translate-x-full', 'translate-x-0');
            toast.classList.replace('opacity-0', 'opacity-100');
        });

        // Self-Destruct
        setTimeout(() => this.hide(toast), 5000);
    }

    hide(toast) {
        toast.classList.replace('translate-x-0', 'translate-x-full');
        toast.classList.replace('opacity-100', 'opacity-0');
        setTimeout(() => toast.remove(), 500);
    }
}

class CountdownTimer {
    constructor(elementId) {
        this.el = document.getElementById(elementId);
        if (!this.el) return;

        this.targetDate = new Date(this.el.dataset.launchDate).getTime();
        this.elements = {
            days: document.getElementById('days'),
            hours: document.getElementById('hours'),
            minutes: document.getElementById('minutes')
        };

        this.init();
    }

    init() {
        this.update();
        setInterval(() => this.update(), 1000);
    }

    update() {
        const distance = this.targetDate - new Date().getTime();
        if (distance < 0) return;

        this.render({
            days: Math.floor(distance / (1000 * 60 * 60 * 24)),
            hours: Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
            minutes: Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60))
        });
    }

    render(data) {
        Object.keys(data).forEach(unit => {
            if (this.elements[unit]) {
                this.elements[unit].innerText = data[unit].toString().padStart(2, '0');
            }
        });
    }
}

class WaitlistManager {
    constructor(toastManager) {
        this.forms = document.querySelectorAll('.waitlist-form');
        this.toast = toastManager;
        this.endpoint = window.location.href;
        this.init();
    }

    init() {
        this.forms.forEach(form => {
            form.addEventListener('submit', (e) => this.handleSubmit(e));
        });
    }

    setLoading(form, isLoading) {
        const btn = form.querySelector('button[type="submit"]');
        if (isLoading) {
            form.dataset.originalContent = btn.innerHTML;
            form.classList.add('pointer-events-none', 'blur-[2px]', 'opacity-60');
            btn.disabled = true;
            btn.innerHTML = `<span class="animate-pulse">Processing...</span>`;
        } else {
            form.classList.remove('pointer-events-none', 'blur-[2px]', 'opacity-60');
            btn.disabled = false;
            btn.innerHTML = form.dataset.originalContent;
        }
    }

    async handleSubmit(e) {
        e.preventDefault();
        const form = e.currentTarget;
        this.setLoading(form, true);

        try {
            const response = await fetch(this.endpoint, {
                method: 'POST',
                body: new FormData(form),
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const result = await response.json();

            if (response.ok && result.status === 'success') {
                this.toast.show(result.message);
                form.reset();
            } else {
                this.toast.show(result.message || 'Validation failed.', 'error');
            }
        } catch (err) {
            this.toast.show('Network error. Check your connection.', 'error');
        } finally {
            this.setLoading(form, false);
        }
    }

    getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }
}

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    const toast = new ToastManager();
    new CountdownTimer('countdown-timer');
    new WaitlistManager(toast);
});