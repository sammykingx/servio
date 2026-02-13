/* * DATA BRIDGE: renderPaymentPlans
 * -------------------------------------------------------------------------
 * Responsibilities:
 * 1. State Management: Controls selection permissions (canSelect).
 * 2. Data Ingestion: Deserializes the {{ payment_options }} JSON blob 
 * located in the <script id="payment-options-data"> template tag.
 * 3. Reactive State: Tracks the user's selected split-payment configuration.
 * -------------------------------------------------------------------------
 */

/**
 * Initializes the payment plan data component for the UI.
 * * This function extracts backend-provided percentage split options from a 
 * JSON script tag and prepares the reactive state for the template.
 * * @param {boolean} canSelect - Determines if the user has permission to toggle/select plans.
 * @returns {Object} An Alpine.js-compatible data object containing:
 * - {boolean} canSelect: Selection permission flag.
 * - {Array} plans: Parsed payment options from the 'payment-options-data' script tag.
 * - {string} selectedPaymentPlan: The currently active selection state.
 * - {Function} selectedPlan: Getter to retrieve the active payment plan.
 */
function renderPaymentPlans(canSelect) {
    return {
        canSelect,
        plans: JSON.parse(document.getElementById('payment-options-data').textContent),
        selectedPaymentPlan: '',

        selectedPlan() {
            return this.selectedPaymentPlan;
        }
    }
}