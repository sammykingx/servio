/**
 * PaystackOrchestrator
 * Handles the flow from Backend Initialization to Frontend Popup
 */
class PaystackOrchestrator {
    constructor(config) {
        const requiredFields = ['status', 'reference', 'provider', 'csrfToken', 'endpoint', 'verificationURL', 'summaryURL'];
        const missing = requiredFields.filter(field => !config[field]);

        if (missing.length > 0) {
            showToast(
                'Missing required initialization data fields',
                'warning',
                'Config Error',
            );
            return;
        }

        this.status = config.status;
        this.reference = config.reference;
        this.provider = config.provider;
        this.csrfToken = config.csrfToken;
        this.backendURL = config.endpoint;
        this.verificationURL = config.verificationURL;
        this.summaryURL = config.summaryURL;
        this.logContainer = config.logContainer || document.getElementById('network-log');
        this.statusTextEl = config.statusTextEl || document.getElementById('payment-status-text');
        this.progressBarEl = config.progressBarEl || document.getElementById('payment-progress-bar');

        this.init();
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Updates the main UI status text and progress bar width
     */
    updateUI(message, percentage) {
        if (this.statusTextEl) {
            this.statusTextEl.innerText = message;
        }
        if (this.progressBarEl) {
            this.progressBarEl.style.width = `${percentage}%`;

            if (percentage >= 100) {
                this.progressBarEl.classList.remove('animate-[progress_3s_ease-in-out_infinite]');
            }
        }
    }

    updateLog(message, status = 'pending') {
        if (!this.logContainer) return;

        const p = document.createElement('p');
        p.className = 'flex items-center gap-2 transition-all duration-300';

        let dotColor = 'text-brand-500 animate-pulse';
        if (status === 'success') dotColor = 'text-emerald-500';
        if (status === 'error') dotColor = 'text-red-500';

        p.innerHTML = `<span class="${dotColor}">●</span> ${message}`;
        this.logContainer.appendChild(p);

        // Auto-scroll to bottom of log if it grows
        this.logContainer.scrollTop = this.logContainer.scrollHeight;
    }

    async init() {
        this.updateUI(`Initializing ${this.provider}...`, 20);
        this.updateLog(`Starting checkout for ${this.provider}...`, 'success');
        if (this.status === "success") {
            this.updateUI("Redirecting to summary...", 100);
            this.updateLog(`Checkout complete for ${this.provider}...`, 'success');
            window.location.assign(this.summaryURL);
            return;
        }

        try {
            this.updateLog(`POST /api/v1/initialize ... requesting access_code`, 'pending');

            const response = await fetch(this.backendURL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken,
                },
                body: JSON.stringify({
                    reference: this.reference,
                    provider: this.provider
                })
            });

            const resp_data = await response.json();

            if (response.ok && resp_data.data.access_code) {
                this.updateUI("Finalizing ...", 70);
                this.updateLog(`200 OK: ${resp_data.message}`, 'success');
                this.updateLog(`200 OK: ${resp_data.title}`, 'success');

                await this.sleep(1500);

                this.updateLog('200 OK: Handing over to secure payment portal ...', 'success');
                this.launchPopup(resp_data.data.access_code);
            } else {
                showToast(
                    resp_data.message,
                    resp_data.response_type || "error",
                    resp_data.title || "Checkout Incomplete",
                );
                throw new Error(resp_data.title || 'Initialization failed');
            }

        } catch (error) {
            this.updateLog(`Error: ${error.message}`, 'error');
        }
    }

    launchPopup(access_code) {
        this.updateLog(`Starting Paystack Checkout Modal...`, 'success');

        const popup = new PaystackPop();
        popup.resumeTransaction(access_code, {
            onSuccess: (transaction) => {
                this.updateUI("Payment Complete!", 100);
                this.updateLog(`Payment Successful! Ref: ${transaction.reference}`, 'success');
                this.updateLog(`verification started...: ${transaction.reference}`, 'pending');
                // Redirect to a success page or refresh
                window.location.href = `${this.verificationURL}?trxref=${transaction.reference}`;
            },
            onCancel: () => {
                this.updateUI("Payment Cancelled!", 100);
                this.updateLog(`User cancelled payment session.`, 'error');
            }
        });
    }
}
