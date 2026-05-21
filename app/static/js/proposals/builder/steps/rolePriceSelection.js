import { ProposalState } from "../payload.js";


export class Step3FinancialManager {
    constructor() {
        this.state = ProposalState;
        this.container = document.getElementById('financial-roles-container');
        this.paymentPlans = [];
    }

    init() {
        this.loadPaymentOptions();
        this.registerGlobalStepListener(); // Unlocked event receiver
    }

    /**
     * Safely reads the embedded JSON structural dictionary from the DOM layout block
     */
    loadPaymentOptions() {
        const jsonDataNode = document.getElementById('payment-options-data');
        if (jsonDataNode) {
            try {
                this.paymentPlans = JSON.parse(jsonDataNode.textContent);
            } catch (err) {
                showToast("Payment plan options failed to load, using fallback defaults.", 'error', 'Proposal Engine');
            }
        }
    }

    /**
     * Intercepts coordinator step updates to rebuild state components reactively
     */
    registerGlobalStepListener() {
        document.addEventListener('stepChanged', (e) => {
            if (e.detail && e.detail.step === 3) {
                this.renderActiveFinancialPanels();
            }
        });
    }

    /**
     * Iterates over selected data models within state to update layout interfaces dynamically
     */
    renderActiveFinancialPanels() {
        if (!this.container) return;
        this.container.innerHTML = '';

        if (!this.state.applied_roles || this.state.applied_roles.length === 0) {
            this.container.innerHTML = `
                <div class="text-center py-12 border-2 border-dashed border-gray-200 dark:border-gray-800 rounded-3xl p-8 max-w-md mx-auto">
                    <div class="h-10 w-10 bg-gray-50 dark:bg-gray-900 rounded-xl flex items-center justify-center mx-auto mb-3 border border-gray-100 dark:border-gray-800">
                        <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 13.5h3.86a2.25 2.25 0 0 1 2.008 1.24l.885 1.77a2.25 2.25 0 0 0 2.007 1.24h1.98a2.25 2.25 0 0 0 2.007-1.24l.885-1.77a2.25 2.25 0 0 1 2.007-1.24h3.86m-18 0h18" />
                        </svg>
                    </div>
                    <span class="text-sm font-medium text-gray-900 dark:text-white block">No roles selected</span>
                    <p class="text-xs text-gray-400 dark:text-gray-500 mt-1 max-w-xs mx-auto leading-relaxed">
                        Please go back to Step 2 and select at least one core track expertise to allocate financial terms.
                    </p>
                </div>`;
            return;
        }

        // Generate customized commercial card sections for each active record
        this.state.applied_roles.forEach((role) => {
            const cardNode = document.createElement('div');
            cardNode.id = `financial-card-${role.niche_id}`;

            // Premium layout transition frames
            cardNode.className = "border border-gray-200 dark:border-gray-800 rounded-2xl bg-white dark:bg-gray-900 overflow-hidden transition-all duration-300 shadow-xs p-5 sm:p-6 space-y-5";

            // Generate dropdown selection choices mapped out from parsed config matrix
            const dropdownOptionsHtml = this.paymentPlans.map(plan => `
                <option value="${plan.value}" ${role.payment_plan === plan.value ? 'selected' : ''}>
                    ${plan.label}
                </option>
            `).join('');

            cardNode.innerHTML = `
                <div class="flex items-center justify-between border-b border-gray-100 dark:border-gray-800/60 pb-3.5">
                    <div class="min-w-0">
                        <span class="text-[10px] tracking-wider font-bold uppercase text-brand-500 dark:text-brand-400 block antialiased">Target Assignment Track</span>
                        <h4 class="text-sm sm:text-base font-semibold text-gray-900 dark:text-white truncate mt-0.5 tracking-tight">${role.niche_name}</h4>
                    </div>
                    
                    <div class="flex items-center gap-2">
                        <span id="financial-status-label-${role.niche_id}" class="text-[11px] font-medium text-gray-400 dark:text-gray-500 transition-colors duration-300">Incomplete</span>
                        <div id="financial-indicator-badge-${role.niche_id}" class="h-2 w-2 rounded-full bg-gray-300 dark:bg-gray-700 transition-all duration-300 ring-4 ring-transparent"></div>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                    <div class="space-y-2">
                        <label class="text-xs font-semibold text-gray-700 dark:text-gray-300 tracking-tight block">Proposed Execution Value</label>
                        <div class="relative rounded-xl shadow-xs">
                            <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                                <span class="text-gray-400 dark:text-gray-500 text-sm font-medium">$</span>
                            </div>
                            <input type="text" 
                                   id="input-rate-${role.niche_id}" 
                                   class="financial-rate-input w-full pl-8 pr-4 py-2.5 text-sm bg-gray-25 dark:bg-gray-950 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-800 rounded-xl focus:outline-none focus:border-brand-500 dark:focus:border-brand-500 focus:bg-white dark:focus:bg-gray-950 transition-all placeholder-gray-400 font-mono tracking-wide shadow-xs"
                                   placeholder="0.00" 
                                   value="${role.proposed_amount > 0 ? role.proposed_amount : ''}"
                                   data-role-id="${role.niche_id}"
                                   inputmode="decimal">
                        </div>
                    </div>

                    <div class="space-y-2">
                        <label class="text-xs font-semibold text-gray-700 dark:text-gray-300 tracking-tight block">Payment Plan Distribution</label>
                        <div class="relative rounded-xl shadow-xs">
                            <select id="select-plan-${role.niche_id}" 
                                    class="financial-plan-select w-full pl-3.5 pr-10 py-2.5 text-sm bg-gray-25 dark:bg-gray-950 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-800 rounded-xl focus:outline-none focus:border-brand-500 dark:focus:border-brand-500 focus:bg-white dark:focus:bg-gray-950 transition-all cursor-pointer appearance-none shadow-xs"
                                    data-role-id="${role.niche_id}">
                                ${dropdownOptionsHtml}
                            </select>
                            <div class="absolute inset-y-0 right-0 pr-3.5 flex items-center pointer-events-none text-gray-400 dark:text-gray-500">
                                <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
                                </svg>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            this.container.appendChild(cardNode);

            this.evaluateCardCompleteness(role.niche_id);
            this.bindCardInteractions(role.niche_id);
            this.updateGrandTotalState();
        });
    }

    /**
     * Aggregates financial rates from all active structures and maps it back to state
     */
    updateGrandTotalState() {
        if (!this.state.applied_roles) {
            this.state.total_value = 0.00;
            return;
        }

        // Accrue a clean floating point arithmetic summation run across all assigned nodes
        const totalSum = this.state.applied_roles.reduce((acc, role) => {
            const amount = parseFloat(role.proposed_amount) || 0.00;
            return acc + amount;
        }, 0);

        this.state.total_value = parseFloat(totalSum.toFixed(2));
    }

    /**
     * STATE MUTATION CORE: Binds real-time interaction listeners to the role card components.
     * * This method serves as the bridge between user inputs and the data pipeline. It hooks 
     * into the DOM elements for an active role and updates the centralized payload state 
     * (`this.state.applied_roles`) reactively as modifications happen.
     * * STATE CHANGES MANAGED HERE:
     * 1. 'input' listener on rate input: Sanitizes numerical data and mutates `targetRole.proposed_amount`.
     * 2. 'change' listener on plan select: Captures choice values and mutates `targetRole.payment_plan`.
     * * @param {string|number} roleId - The unique `niche_id` used to pinpoint the target role within the state array.
     */
    bindCardInteractions(roleId) {
        const rateInput = document.getElementById(`input-rate-${roleId}`);
        const planSelect = document.getElementById(`select-plan-${roleId}`);

        if (rateInput) {
            rateInput.addEventListener('input', (e) => {
                let cleanVal = e.target.value.replace(/[^0-9.]/g, '');

                const points = cleanVal.split('.');
                if (points.length > 2) {
                    cleanVal = points[0] + '.' + points.slice(1).join('');
                }

                e.target.value = cleanVal;

                const targetRole = this.state.applied_roles.find(r => r.niche_id === roleId);
                if (targetRole) {
                    // ─── ROLE AMOUNT MUTATION
                    targetRole.proposed_amount = parseFloat(cleanVal) || 0.00;
                }

                this.evaluateCardCompleteness(roleId);
                this.updateGrandTotalState();
            });
        }

        if (planSelect) {
            planSelect.addEventListener('change', (e) => {
                const targetRole = this.state.applied_roles.find(r => r.niche_id === roleId);
                if (targetRole) {
                    // ─── PAYMENT PLAN MUTATION
                    targetRole.payment_plan = e.target.value;
                }
                this.evaluateCardCompleteness(roleId);
            });
        }
    }

    /**
     * Validates whether data criteria are met for a role card and updates border styles dynamically
     */
    evaluateCardCompleteness(roleId) {
        const card = document.getElementById(`financial-card-${roleId}`);
        const badge = document.getElementById(`financial-indicator-badge-${roleId}`);
        const statusLabel = document.getElementById(`financial-status-label-${roleId}`);
        const targetRole = this.state.applied_roles.find(r => r.niche_id === roleId);

        if (!card || !targetRole) return;

        const isComplete = targetRole.proposed_amount > 0 && targetRole.payment_plan !== '';

        if (isComplete) {
            // Apply Complete Visual Styles (Premium Emerald 500 Theme Accent)
            card.classList.remove('border-gray-200', 'dark:border-gray-800');
            card.classList.add('border-emerald-500', 'dark:border-emerald-400');

            if (badge) {
                badge.classList.remove('bg-gray-300', 'dark:bg-gray-700', 'ring-transparent');
                badge.classList.add('bg-emerald-500', 'ring-emerald-100', 'dark:ring-emerald-850/50');
            }
            if (statusLabel) {
                statusLabel.classList.remove('text-gray-400', 'dark:text-gray-500');
                statusLabel.classList.add('text-emerald-600', 'dark:text-emerald-400');
                statusLabel.textContent = "Ready";
            }
        } else {
            // Revert to Standard Base Gray Colors
            card.classList.remove('border-emerald-500', 'dark:border-emerald-400');
            card.classList.add('border-gray-200', 'dark:border-gray-800');

            if (badge) {
                badge.classList.remove('bg-emerald-500', 'ring-emerald-100', 'dark:ring-emerald-850/50');
                badge.classList.add('bg-gray-300', 'dark:bg-gray-700', 'ring-transparent');
            }
            if (statusLabel) {
                statusLabel.classList.remove('text-emerald-600', 'dark:text-emerald-400');
                statusLabel.classList.add('text-gray-400', 'dark:text-gray-500');
                statusLabel.textContent = "Incomplete";
            }
        }
    }
}