import { ProposalState } from "../payload.js";

export class Step5ReviewManager {
    constructor() {
        this.state = ProposalState;

        // Cache your explicit static HTML elements
        this.nicheDisplay = document.getElementById('review-niche');
        this.valueDisplay = document.getElementById('review-value');
        this.deliverablesCountDisplay = document.getElementById('review-deliverables-count');
        this.step5Container = document.getElementById('step-5');
    }

    init() {
        this.registerGlobalStepListener();
    }

    registerGlobalStepListener() {
        document.addEventListener('stepChanged', (e) => {
            if (e.detail && e.detail.step === 5) {
                this.hydrateReviewData();
                this.ensureIntegrityCheckbox();
            }
        });
    }

    /**
     * Safely reads state metrics and injects them directly into your static HTML structure
     */
    hydrateReviewData() {
        // 1. Map and format Niche Profiles string combinations
        if (this.nicheDisplay) {
            const niches = this.state.applied_roles?.map(role => role.niche_name) || [];
            this.nicheDisplay.textContent = niches.length > 0 ? niches.join(', ') : 'No tracks selected';
        }

        // 2. Compute gross value lock and format as premium financial currency
        if (this.valueDisplay) {
            const absoluteGrossSum = this.state.applied_roles?.reduce((sum, role) => sum + (Number(role.proposed_amount) || 0), 0) || 0;
            this.valueDisplay.textContent = new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD',
                minimumFractionDigits: 0
            }).format(absoluteGrossSum);
        }

        // 3. Count execution components / milestone totals
        if (this.deliverablesCountDisplay) {
            const totalDeliverables = this.state.applied_roles?.reduce((sum, role) => sum + (role.deliverables?.length || 0), 0) || 0;
            this.deliverablesCountDisplay.textContent = totalDeliverables;
        }
    }

    /**
     * Injects the validation requirement lock element at the bottom of the container if it doesn't exist yet
     */
    ensureIntegrityCheckbox() {
        if (!this.step5Container) return;

        // Check if the confirmation block has already been rendered to prevent duplication
        if (document.getElementById('chk-integrity-lock')) return;

        const acknowledgmentWrapper = document.createElement('div');
        acknowledgmentWrapper.className = "pt-4 border-t border-slate-100 dark:border-gray-800 animate-fade-in";
        acknowledgmentWrapper.innerHTML = `
            <div class="p-5 border border-gray-100 dark:border-gray-800/60 rounded-2xl bg-gray-50/50 dark:bg-gray-950/20 transition-all duration-300">
                <label class="flex items-start gap-3 cursor-pointer group select-none">
                    <input type="checkbox" id="chk-integrity-lock" class="mt-0.5 rounded border-gray-300 dark:border-gray-700 text-brand-500 focus:ring-brand-500 dark:bg-gray-950 h-4 w-4 transition-colors">
                    <div class="space-y-0.5">
                        <span class="text-xs font-semibold text-gray-800 dark:text-gray-300 group-hover:text-gray-900 dark:group-hover:text-white transition-colors">Confirm structural lifecycle deployment</span>
                        <p class="text-[11px] text-gray-400 dark:text-gray-500 leading-normal">I verify that all timelines, scoped specifications, and percentage release distributions comply with platform standards and requirements.</p>
                    </div>
                </label>
            </div>
        `;

        this.step5Container.appendChild(acknowledgmentWrapper);
    }
}