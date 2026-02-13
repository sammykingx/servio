/* * COMPONENT: taxonomyPicker
 * -------------------------------------------------------------------------
 * SOURCE: Expects <script id="taxonomy-data"> containing a nested Industry -> Niche JSON.
 * * KEY LOGIC:
 * - Reactive Filtering: 'filteredSubcategories' computes the child list 
 * automatically when 'selectedIndustryId' changes.
 * - State Bridge: 'buildPayload' utilizes Alpine.$data to pull the selected 
 * payment plan from a separate DOM element, ensuring the backend receives 
 * a unified data structure.
 * -------------------------------------------------------------------------
 */

/**
 * Manages the hierarchical selection of Industries and Niches (Subcategories).
 * * Responsibilities:
 * 1. Data Hydration: Parses hierarchical industry/niche data from the 'taxonomy-data' script tag.
 * 2. Dependency Tracking: Dynamically filters subcategories based on the selected parent industry.
 * 3. Cross-Component Communication: Accesses the 'gigPaymentPlan' Alpine component via x-ref 
 * to aggregate disparate UI states into a single submission payload.
 * * @returns {Object} State-driven object for industry/niche selection and payload assembly.
 */
function taxonomyPicker() {
    return {
        industries: JSON.parse(document.getElementById('taxonomy-data').textContent),
        selectedIndustryId: '',
        subcategories: [],
        selectedNicheId: '',
        roleAmount: 0,
        payment_plan: '',

        filteredSubcategories() {
            const industry = this.industries.find(i => i.id == this.selectedIndustryId);
            return industry ? industry.subcategories : [];
        },

        buildPayload() {
            const paymentPlanEl = document.querySelector('[x-ref="gigPaymentPlan"]');
            if (paymentPlanEl) {
                return [{
                    industry_id: this.selectedIndustryId,
                    niche_id: this.selectedNicheId,
                    role_amount: this.roleAmount,
                    payment_plans: Alpine.$data(paymentPlanEl).selectedPlan(),
                }];
            } else {
                return null;
            }
        },
    }
}