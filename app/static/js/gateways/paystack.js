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

        this.init();
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
        this.updateLog(`Starting checkout for ${this.provider}...`, 'success');
        if (this.status === "success") {
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

            const data = await response.json();

            if (response.ok && data.access_code) {
                this.updateLog(`200 OK: ${data.message}`, 'success');
                await sleep(1000); // 1 second pause

                this.updateLog('200 OK: Access code received, preparing ...', 'success');
                await sleep(1000);

                this.updateLog(`200 OK: ${data.title}`, 'success');
                await sleep(1000);

                this.launchPopup(data.access_code);
            } else {
                showToast(
                    data.message,
                    data.type || "error",
                    data.title || "Checkout Incomplete",
                );
                throw new Error(data.title || 'Initialization failed');
            }

        } catch (error) {
            this.updateLog(`Error: ${error.message}`, 'error');
        }
    }

    launchPopup(access_code) {
        this.updateLog(`Starting Paystack Checkout...`, 'success');

        const popup = new PaystackPop();
        popup.resumeTransaction(access_code, {
            onSuccess: (transaction) => {
                this.updateLog(`Payment Successful! Ref: ${transaction.reference}`, 'success');
                // Redirect to a success page or refresh
                window.location.href = `${this.verificationURL}?trxref=${transaction.reference}`;
            },
            onCancel: () => {
                console.log("User cancelled session");
                this.updateLog(`User cancelled payment session.`, 'error');
            }
        });
    }
}
