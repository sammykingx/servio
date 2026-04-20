class PaystackVerificationOrchestrator {
    constructor(config) {
        const required = ['reference', 'provider', 'endpoint'];
        const missing = required.filter(k => !config[k]);
        if (missing.length > 0) {
            showToast(
                'Missing required page initialization data fields',
                'warning',
                'Config Error',
            );
            return;
        }

        this.config = config;

        // DOM Elements
        this.statusText = document.getElementById('verification-status-text');
        this.progressBar = document.getElementById('verification-progress-bar');
        this.terminal = document.getElementById('verification-terminal');
        this.statusBadge = document.getElementById('verification-badge');
        this.mainIcon = document.getElementById('verification-main-icon');
        this.svgCircle = document.getElementById('verification-svg-circle');

        this.init();
    }

    async init() {
        this.log("INFO", `Syncing with ${this.config.provider} gateway...`);
        this.updateUI("Awaiting confirmation...", 30);

        await this.sleep(1500);
        this.verify();
    }

    async verify() {
        this.log("WAIT", "Checking payment status...");
        this.updateUI("Verifying payment...", 60);

        try {
            const response = await fetch(this.config.endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    reference: this.config.reference,
                    provider: this.config.provider
                })
            });

            const result = await response.json();

            if (response.ok && result.status) {
                this.handleSuccess(result);
            } else {
                this.handleFailure(result);
            }
        } catch (error) {
            const err = {
                title: "Network connection lost",
                message: "We couldn't complete the request. Please try again.",
            }
            this.handleFailure(err);
        }
    }

    handleSuccess(result) {
        this.log("DONE", "Transaction verification complete 🥳!");
        this.log('DONE', result.message);
        this.updateUI("Verification Complete", 100);

        // Update Badge and Icon
        if (this.statusBadge) {
            this.statusBadge.innerText = "Verified";
            this.statusBadge.className = "text-xs font-medium text-emerald-500";
        }

        // Stop SVG animation and swap icon
        this.stopSpinner("text-emerald-500", "check_circle");
        // setTimeout(() => {
        //     window.location.assign(this.config.successURL);
        // }, 2000);
    }

    handleFailure(result) {
        this.log("FAIL", result.title);
        this.log("REASON", result.message);
        this.updateUI("Verification Failed", 100, "bg-red-500");

        if (this.statusBadge) {
            this.statusBadge.innerText = "Failed";
            this.statusBadge.className = "text-xs font-medium text-red-500";
        }

        this.stopSpinner("text-red-500", "error");
    }

    // Helper: UI Updates
    updateUI(text, progress, colorClass = "bg-emerald-500") {
        if (this.statusText) this.statusText.innerText = text;
        if (this.progressBar) {
            this.progressBar.style.width = `${progress}%`;
            this.progressBar.className = `h-full rounded-full transition-all duration-700 ${colorClass}`;
        }
    }

    // Helper: Stop SVG Spinner
    stopSpinner(colorClass, iconName) {
        if (this.svgCircle) {
            this.svgCircle.classList.remove('animate-[dash_2s_ease-in-out_infinite]');
            this.svgCircle.classList.add(colorClass);
            this.svgCircle.setAttribute('stroke-dashoffset', '0');
        }
        if (this.mainIcon) {
            this.mainIcon.innerText = iconName;
            this.mainIcon.classList.remove('text-emerald-500');
            this.mainIcon.classList.add(colorClass);
        }
    }

    log(type, msg) {
        if (!this.terminal) return;
        const p = document.createElement('p');
        p.className = "flex gap-2";
        p.innerHTML = `<span>[${type}]</span> ${msg}`;
        this.terminal.appendChild(p);
    }

    sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
}