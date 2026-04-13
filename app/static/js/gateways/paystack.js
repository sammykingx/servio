/**
 * PaystackOrchestrator
 * Handles the flow from Backend Initialization to Frontend Popup
 */
class PaystackOrchestrator {
    constructor(config) {
        this.reference = config.reference;
        this.provider = config.provider;
        this.csrfToken = config.csrfToken;
        this.backendURL = config.endpoint;
        this.verifcationURL = config.verifcationURL,
        this.logContainer = config.logContainer || document.getElementById('network-log');

        this.init();
    }

    // Helper to update the UI "Network Log"
    updateLog(message, status = 'pending') {
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
                this.updateLog('200 OK: Access code received, preparing ...', 'success');
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
        this.updateLog(`Launching Paystack Secure Popup...`, 'success');

        const popup = new PaystackPop();
        popup.resumeTransaction(access_code, {
            onSuccess: (transaction) => {
                this.updateLog(`Payment Successful! Ref: ${transaction.reference}`, 'success');
                // Redirect to a success page or refresh
                window.location.href = `${this.verifcationURL}?trxref=${transaction.reference}`;
            },
            onCancel: () => {
                this.updateLog(`User cancelled payment session.`, 'error');
            }
        });
    }
}



// class PaystackOrchestrator {
//     constructor(config) {
//         this.reference = config.reference;
//         this.provider = config.provider;
//         this.backendURL = config.backendURL; // Your backend POST endpoint
//         this.csrfToken = config.csrfToken;

//         // State for UI tracking
//         this.status = 'idle'; // idle, initializing, ready, failed
//         this.error = null;
//         this.accessCode = null;

//         // Callback for UI updates (ideal for Alpine.js)
//         this.onStateChange = config.onStateChange || (() => { });
//     }

//     updateState(newState, extra = {}) {
//         this.status = newState;
//         if (extra.error) this.error = extra.error;
//         if (extra.accessCode) this.accessCode = extra.accessCode;
//         this.onStateChange(this);
//     }

//     async initializePayment() {
//         this.updateState('initializing');

//         try {
//             const response = await fetch(this.backendURL, {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                     'X-CSRFToken': this.csrfToken,
//                 },
//                 body: JSON.stringify({
//                     reference: this.reference,
//                     provider: this.provider,
//                     // Add other data you decide on later here
//                 })
//             });

//             const data = await response.json();

//             if (response.ok && data.access_code) {
//                 this.updateState('ready', { accessCode: data.access_code });
//                 this.launchPopup(data.access_code);
//             } else {
//                 throw new Error(data.message || 'Initialization failed');
//             }
//         } catch (err) {
//             this.updateState('failed', { error: err.message });
//             console.error("Paystack Init Error:", err);
//         }
//     }

//     launchPopup(accessCode) {
//         const popup = new PaystackPop();
//         popup.resumeTransaction(accessCode);
//     }
// }