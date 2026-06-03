/**
 * Servio Contract Activation / Payment Checkout Module
 * Implements automated geo-targeting and multi-gateway UI switching.
 */
const ContractPaymentCheckout = (() => {
    const GATEWAY_CONFIG = {
        paystack: { currency: "NGN", symbol: "₦", dataAttr: "ngnAmount" },
        stripe: { currency: "USD", symbol: "$", dataAttr: "usdAmount" }
    };

    // Private state containment fields
    let elements = {};

    /**
     * Updates text nodes, price nodes, and button state components globally
     */
    function updateUI(gatewayKey) {
        const config = GATEWAY_CONFIG[gatewayKey];
        if (!config || !elements.widget) return;

        // Strip any commas or characters injected by Django localized template formatting before parsing
        const rawAmount = elements.widget.dataset[config.dataAttr] || "0";
        const cleanAmount = parseFloat(rawAmount.replace(/,/g, ''));

        const formattedAmount = isNaN(cleanAmount) ? "0.00" : cleanAmount.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });

        const fullDisplayPrice = `${config.symbol}${formattedAmount}`;

        if (elements.summaryFeeTier) elements.summaryFeeTier.textContent = fullDisplayPrice;
        if (elements.summaryTotalPayable) elements.summaryTotalPayable.textContent = fullDisplayPrice;
        if (elements.btnText) elements.btnText.textContent = `Pay ${fullDisplayPrice} & Activate`;
    }

    /**
     * Forces selection checking down to programmatic radio inputs
     */
    function selectGateway(value) {
        const targetRadio = document.getElementById(`gateway-${value}`);
        if (targetRadio) {
            targetRadio.checked = true;
            updateUI(value);
        }
    }

    /**
     * Resolves ISP location context or falls back to locale/default configurations
     */
    function initializeDefaultGateway() {
        try {
            // Priority 1: High performance native browser runtime timezone analysis
            const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            if (timezone === "Africa/Lagos") {
                return selectGateway("paystack");
            }

            // Priority 2: System language locale indicators fallback check
            const locale = navigator.language || navigator.userLanguage || "";
            if (locale.includes("-NG") || ["ig", "yo", "ha"].some(lng => locale.startsWith(lng))) {
                return selectGateway("paystack");
            }

            // Priority 3: Asynchronous routing inspection metadata request
            fetch("https://ipapi.co/json/")
                .then(res => res.json())
                .then(data => selectGateway(data.country_code === "NG" ? "paystack" : "stripe"))
                .catch(() => selectGateway("stripe"));

        } catch (err) {
            selectGateway("stripe"); // Global safety catch guarantee
        }
    }

    /**
     * Orchestrates backend delivery and intermediate application state styling
     */
    async function handleFormSubmit(e) {
        e.preventDefault();

        const activeRadio = document.querySelector('input[name="payment_gateway"]:checked');
        const selectedGateway = activeRadio ? activeRadio.value : "stripe";
        const contractRef = elements.widget.dataset.reference;

        // Toggle UI Processing States
        if (elements.submitBtn) {
            elements.submitBtn.disabled = true;
            elements.submitBtn.classList.add("animate-pulse", "opacity-80");
        }

        if (elements.btnText) {
            elements.btnText.innerHTML = `
                <span class="flex items-center justify-center gap-2">
                    <svg class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Initiating contract activation...</span>
                </span>
            `;
        }

        try {
            const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
            const response = await fetch(elements.form.action || window.location.href, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfTokenElement ? csrfTokenElement.value : ""
                },
                body: JSON.stringify({
                    contract_reference: contractRef,
                    gateway: selectedGateway
                })
            });

            const result = await response.json();

            if (!response.ok) {
                if (typeof showToast === "function") {
                    showToast(result.message || "Activation handoff aborted.", "error", "Contract Activation Failed");
                } else {
                    alert(result.message || "Activation handoff aborted.");
                }
                return;
            }

            if (typeof showToast === "function") {
                showToast(result.message || "Contract activation initiated successfully. Redirecting...", "success", "Activation Initiated");
            }

            if (result.redirect_url) {
                window.location.href = result.redirect_url;
            }

        } catch (error) {
            console.error("Payment Execution Error:", error);
            if (typeof showToast === "function") {
                showToast(error.message || "Something went wrong. Please try again.", "error", "Connection Error");
            } else {
                alert(error.message || "Something went wrong. Please try again.");
            }
        } finally {
            if (elements.submitBtn) {
                elements.submitBtn.disabled = false;
                elements.submitBtn.classList.remove("animate-pulse", "opacity-80");
            }
            updateUI(selectedGateway);
        }
    }

    /**
     * Public Bootloader / Initialization Hook
     */
    const init = () => {
        elements = {
            widget: document.getElementById("payment-widget"),
            form: document.getElementById("checkout-payment-form"),
            submitBtn: document.getElementById("submit-btn"),
            btnText: document.getElementById("btn-text"),
            summaryFeeTier: document.getElementById("summary-fee-tier"), // Fixed syntax error (= to :)
            summaryTotalPayable: document.getElementById("summary-total-payable"), // Fixed syntax error (= to :)
            gatewayRadios: document.querySelectorAll('input[name="payment_gateway"]')
        };

        // Break early if target workspace page is completely unmounted 
        if (!elements.widget || !elements.form) return;

        // Register interactive element bindings
        elements.gatewayRadios.forEach(radio => {
            radio.addEventListener("change", (e) => updateUI(e.target.value));
        });
        elements.form.addEventListener("submit", handleFormSubmit);

        // Execute dynamic runtime geolocation defaults pipeline 
        initializeDefaultGateway();
    };

    return { init };
})();