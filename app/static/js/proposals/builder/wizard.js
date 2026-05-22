import { ProposalState } from "./payload.js";
import { Step2RoleSelectionManager } from "./steps/role-selection.js"
import { Step3FinancialManager } from "./steps/rolePriceSelection.js"
import { Step4DeliverablesManager } from "./steps/delieverables.js";
import { Step5ReviewManager } from "./steps/reviewProposal.js";
import { ProposalSubmissionOrchestrator } from "../sendProposal.js";


class ProposalWizardCoordinator {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 5;
        this.state = ProposalState;

        // Cache persistent DOM containers
        this.prevBtn = document.getElementById('prev-btn');
        this.nextBtn = document.getElementById('next-btn');
        this.currentStepBadge = document.getElementById('current-step-badge');
        this.progressLine = document.getElementById('progress-line');
        this.stepIndicators = document.querySelectorAll('.step-indicator');
    }

    init() {
        this.extractBackendContext();
        this.registerEvents();
        this.updateUI();
    }

    /**
     * Reads variables sent down by the backend template
     */
    extractBackendContext() {
        const step1Section = document.getElementById('step-1');
        if (step1Section) {
            const contextProjectId = step1Section.getAttribute('data-project-id');
            // Check to ensure context rendering is operational
            this.state.project_id = contextProjectId && !contextProjectId.includes('{{') ? contextProjectId : 'dev-placeholder-123';
        }
    }

    registerEvents() {
        if (this.nextBtn) this.nextBtn.addEventListener('click', () => this.next());
        if (this.prevBtn) this.prevBtn.addEventListener('click', () => this.prev());

        // Intercept header tracker button clicks to enforce linear navigation
        this.stepIndicators.forEach(indicator => {
            indicator.addEventListener('click', (e) => {
                e.preventDefault();
                const targetStep = parseInt(e.currentTarget.getAttribute('data-step'), 10);

                // Allow users to revisit previous steps, but block jumping ahead
                if (targetStep && targetStep < this.currentStep) {
                    this.goToStep(targetStep);
                } else if (targetStep && targetStep > this.currentStep) {
                    showToast(`Please use the action button at the bottom to proceed to Step ${this.currentStep + 1}.`, 'warning', 'Proposal Engine');
                }
            });
        });

    }

    /**
     * Delegates validation rules based on active step index
     */
    validateCurrentStep() {
        switch (this.currentStep) {
            case 1:
                return true;
            case 2:
                // Ensure at least one role has been selected in the state array
                if (!this.state.applied_roles || this.state.applied_roles.length === 0) {
                    showToast("Please select and include at least one role to proceed.", "warning", "Validation Error");
                    return false;
                }
                return true;
            case 3:
                console.log(JSON.stringify(this.state, null, 2));
                if (!this.state.applied_roles || this.state.applied_roles.length === 0) {
                    showToast("No applied roles detected in proposal state. Return to step 2.", "error", "Validation Error");
                    return false;
                }

                const allRolesFullyConfigured = this.state.applied_roles.every(role => {
                    return (
                        role.industry_id && String(role.industry_id).trim() !== '' &&
                        role.niche_id && String(role.niche_id).trim() !== '' &&
                        role.niche_name && String(role.niche_name).trim() !== '' &&
                        role.payment_plan && String(role.payment_plan).trim() !== '' &&
                        typeof role.proposed_amount === 'number' && role.proposed_amount > 0
                    );
                });

                if (!allRolesFullyConfigured) {
                    showToast("Role data is incomplete. Please go back a step to finish setting up your tracks.", "warning", "Validation Error");
                    return false;
                }
                // console.log(JSON.stringify(this.state, null, 2));
                return true;
            case 4:
                if (!this.state.applied_roles || this.state.applied_roles.length === 0) return false;

                for (const role of this.state.applied_roles) {
                    if (!role.deliverables || role.deliverables.length === 0) {
                        showToast(`Please append at least one core deliverable strategy for the tracking framework: "${role.niche_name}".`, "warning", "Validation Error");
                        return false;
                    }

                    // 1. Data Shape Completeness Verification Check Loop
                    const allFieldsValid = role.deliverables.every(d => {
                        return d.phase.trim() !== '' && d.description.trim() !== '' && d.release_percentage > 0;
                    });

                    if (!allFieldsValid) {
                        showToast(`Please fill out all fields (Title, Description & Percent) within the "${role.niche_name}" category sheets.`, "warning", "Validation Error");
                        return false;
                    }

                    // 2. Exact Cumulative Percentage Distribution Arithmetic Audit Rule
                    const totalSum = role.deliverables.reduce((acc, d) => acc + d.release_percentage, 0);
                    if (totalSum !== 100) {
                        showToast(`The cumulative tracking release percentage for "${role.niche_name}" sums to ${totalSum}%. It must equal exactly 100% to proceed.`, "warning", "Validation Error");
                        return false;
                    }
                }
                // console.log(JSON.stringify(this.state, null, 2));
                return true;
            default:
                return true;
        }
    }

    /**
     * Updates visibility matrices, navigation constraints, and progress mechanics
     */
    updateUI() {
        // 1. Sync current badge values
        if (this.currentStepBadge) this.currentStepBadge.textContent = this.currentStep;

        // 2. Hide Back button completely when viewing stage 1
        if (this.currentStep === 1) {
            this.prevBtn.classList.add('invisible');
        } else {
            this.prevBtn.classList.remove('invisible');
        }

        // 3. Coordinate progress-line dimensions fluidly
        if (this.progressLine) {
            const progressPercent = ((this.currentStep - 1) / (this.totalSteps - 1)) * 100;
            this.progressLine.style.width = `${progressPercent}%`;
        }

        // 4. Update Step Visibility panels
        document.querySelectorAll('.wizard-step').forEach((stepSection, index) => {
            const stepNum = index + 1;
            if (stepNum === this.currentStep) {
                stepSection.classList.remove('step-hidden');
                stepSection.classList.add('step-active');
            } else {
                stepSection.classList.remove('step-active');
                stepSection.classList.add('step-hidden');
            }
        });

        // 5. Stylize step dot active states clean mapping
        this.stepIndicators.forEach(dot => {
            const dotStep = parseInt(dot.getAttribute('data-step'), 10);
            if (dotStep <= this.currentStep) {
                dot.classList.add('bg-brand-500', 'text-white', 'border-brand-500');
                dot.classList.remove('bg-white', 'dark:bg-gray-900', 'text-gray-400', 'dark:text-gray-500', 'border-gray-200', 'dark:border-gray-800');
            } else {
                dot.classList.remove('bg-brand-500', 'text-white', 'border-brand-500');
                dot.classList.add('bg-white', 'dark:bg-gray-900', 'text-gray-400', 'dark:text-gray-500', 'border-gray-200', 'dark:border-gray-800');
            }
        });
    }

    goToStep(stepNumber) {
        if (stepNumber >= 1 && stepNumber <= this.totalSteps) {
            this.currentStep = stepNumber;
            this.updateUI();
            this.notifyStepChange();
        }
    }

    next() {
        // Run validations for the current step before advancing
        if (!this.validateCurrentStep()) {
            return;
        }

        if (this.currentStep < this.totalSteps) {
            this.currentStep++;
            this.updateUI();
            this.notifyStepChange();
        }
    }

    prev() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.updateUI();
            this.notifyStepChange();
        }
    }
    notifyStepChange() {
        document.dispatchEvent(new CustomEvent('stepChanged', {
            detail: { step: this.currentStep }
        }));
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const coordinatorInstance = new ProposalWizardCoordinator();
    const roleManager = new Step2RoleSelectionManager();
    const financialManager = new Step3FinancialManager();
    const deliverablesManager = new Step4DeliverablesManager();
    const proposalReview = new Step5ReviewManager();
    const submissionOrchestrator = new ProposalSubmissionOrchestrator();

    roleManager.init();
    financialManager.init();
    deliverablesManager.init();
    proposalReview.init();
    submissionOrchestrator.init();
    coordinatorInstance.init();
});