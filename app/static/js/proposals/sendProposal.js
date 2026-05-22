import { ProposalState, resetProposalState } from "./builder/payload.js";


export class ProposalSubmissionOrchestrator {
    constructor() {
        this.state = ProposalState;
        this.nextBtn = document.getElementById('next-btn');
        this.prevBtn = document.getElementById('prev-btn');
        this.wizardFrame = document.getElementById('proposal-form');
        this.currentStep = 1;
    }

    init() {
        this.monitorStepChanges();
        this.interceptNextActionButtonClick();
    }

    monitorStepChanges() {
        document.addEventListener('stepChanged', (e) => {
            if (!e.detail) return;
            this.currentStep = e.detail.step;
            this.morphNavigationButtonStyles();
        });
    }

    /**
     * Morphs the default state navigation parameters into an expressive CTA engine configuration
     */
    morphNavigationButtonStyles() {
        if (!this.nextBtn) return;

        if (this.currentStep === 5) {
            this.nextBtn.textContent = 'Send Proposal';
            this.nextBtn.className = "inline-flex items-center justify-center h-11 px-6 bg-gradient-to-r from-brand-500 to-brand-600 hover:from-brand-600 hover:to-brand-700 text-white rounded-xl text-sm font-semibold transition-all shadow-lg hover:shadow-brand-500/20 focus:outline-none ml-auto transform hover:-translate-y-0.5 active:translate-y-0";
        } else {
            this.nextBtn.textContent = 'Continue';
            this.nextBtn.className = "inline-flex items-center justify-center h-11 px-6 bg-brand-500 hover:bg-brand-600 dark:hover:bg-brand-400 text-white rounded-xl text-sm font-semibold transition-all shadow-md focus:outline-none ml-auto";
        }
    }

    /**
     * Intercepts standard coordinator steps to capture intentional submission workflows
     */
    interceptNextActionButtonClick() {
        this.nextBtn?.addEventListener('click', (e) => {
            if (this.currentStep === 5) {
                // Prevent standard progressive logic steps inside wizard manager controllers
                e.stopImmediatePropagation();
                this.executePayloadDispatchPipeline();
            }
        });
    }

    /**
     * Executes a deep structural validation check on the active ProposalState payload
     * @returns {boolean} True if payload passes all business logic and schema requirements
     */
    validatePayloadIntegrity() {
        if (!this.state.project_id || typeof this.state.project_id !== 'string') {
            this.logValidationFailure("Invalid or missing Project Identification reference.");
            return false;
        }

        if (!this.state.applied_roles || this.state.applied_roles.length === 0) {
            this.logValidationFailure("You must have at least one active role to submit a proposal.");
            return false;
        }

        for (const role of this.state.applied_roles) {
            if (!role.industry_id || !role.niche_id) {
                this.logValidationFailure(`Role metadata is missing identifiers.`);
                return false;
            }

            if (Number(role.proposed_amount) < 10.00) {
                this.logValidationFailure(`Proposed custom pricing for "${role.niche_name || 'Selected Role'}" must be at least $10.00.`);
                return false;
            }

            if (!role.deliverables || role.deliverables.length === 0) {
                this.logValidationFailure(`The role "${role.niche_name}" requires at least one project milestone or deliverable.`);
                return false;
            }

            // 3. Deliverable Milestone Validation
            let totalReleasePercentage = 0;

            for (const deliverable of role.deliverables) {
                if (!deliverable.phase || deliverable.phase.trim().length > 70) {
                    this.logValidationFailure("Milestone titles must be provided and capped at 70 characters.");
                    return false;
                }

                if (!deliverable.description || deliverable.description.trim().length > 2000) {
                    this.logValidationFailure("Milestone descriptions must be present and under 2,000 characters.");
                    return false;
                }

                if (!['days', 'weeks', 'months'].includes(deliverable.duration_unit)) {
                    this.logValidationFailure("Invalid milestone duration interval configuration flag.");
                    return false;
                }

                const pct = Number(deliverable.release_percentage) || 0;
                if (pct < 10.0 || pct > 100.0) {
                    this.logValidationFailure("Financial release milestone weights must fall between 10% and 100%.");
                    return false;
                }

                totalReleasePercentage += pct;
            }

            // Business Logic Guard: Escrow release milestones must add up to exactly 100%
            // Using an epsilon check to prevent floating-point rounding issues (e.g., 99.99999)
            if (Math.abs(totalReleasePercentage - 100.0) > 0.01) {
                this.logValidationFailure(`Milestone financial weights for "${role.niche_name}" must sum up to exactly 100%. Current total: ${totalReleasePercentage}%`);
                return false;
            }
        }

        return true;
    }

    logValidationFailure(reason) {
        if (typeof showToast === 'function') {
            showToast(reason, "warning", "Validation Error");
        } else {
            console.warn(`[Payload Validation Failure]: ${reason}`);
        }
    }

    async executePayloadDispatchPipeline() {
        const container = document.getElementById('proposal-container');
        if (container && container.dataset.hasSubmitted === 'true') {
            showToast("This proposal has already been transmitted successfully.", "info", "Action Restrained");
            setTimeout(() => {
                const url = container.dataset.marketplaceUrl || '/collaboration/oppurtunities/for-you/';
                window.location.replace(url);
            }, 2000);
            return;
        }
        if (!this.validatePayloadIntegrity()) {
            return;
        }

        // Optional: Ensure validation lock has been checked prior to data transmission
        const integrityCheckbox = document.getElementById('chk-integrity-lock');
        if (integrityCheckbox && !integrityCheckbox.checked) {
            integrityCheckbox.closest('div').classList.add('animate-shake', 'border-rose-500/30');
            setTimeout(() => integrityCheckbox.closest('div').classList.remove('animate-shake'), 400);
            return;
        }

        // Calculate and append the precise submission timeline metric
        this.state.sent_at = new Date().toISOString();

        // Also dynamically calculate total valuation from active role records to keep numbers honest
        this.state.total_value = this.state.applied_roles?.reduce(
            (sum, role) => sum + (Number(role.proposed_amount) || 0), 0
        ) || 0;

        // 1. Establish the locked, immutable architecture footprint
        const finalizedImmutablePayload = Object.freeze(JSON.parse(JSON.stringify(this.state)));

        // 2. Extract network destination vectors and CSRF indicators

        const endpoint = container.dataset.submissionEndpoint || window.location.href;
        const csrfToken = container.dataset.csrfToken || document.querySelector('[name="csrfmiddlewaretoken"]')?.value;

        // 3. Mutate UX environment to show heavy calculation states
        this.toggleProcessingInterfaceVisualState(true);

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(finalizedImmutablePayload)
            });

            const responseData = await response.json();

            if (response.ok) {
                if (container) container.dataset.hasSubmitted = 'true';
                showToast(responseData.message, responseData.status, responseData.title);
                this.dispatchGlobalLifecycleNotification('proposalSubmittedSuccess', responseData);
                setTimeout(() => {
                    resetProposalState();
                    window.location.assign(responseData.url);
                }, 2000);
            } else {
                showToast(responseData.message, responseData.status, responseData.error);
                this.dispatchGlobalLifecycleNotification('proposalSubmittedFailure', responseData);
            }
        } catch (error) {
            showToast(
                "Unable to reach the server. Please check your connection and try again.",
                "error",
                "Connection Error"
            );
            this.dispatchGlobalLifecycleNotification('proposalSubmittedFailure', { error: error.message });
        } finally {
            this.toggleProcessingInterfaceVisualState(false);
        }
    }

    /**
     * Controls interface elements, application layers, pointer bindings, and processing animations
     */
    toggleProcessingInterfaceVisualState(isProcessing) {
        if (!this.nextBtn) return;

        if (isProcessing) {
            // Disable navigation steps
            this.nextBtn.disabled = true;
            if (this.prevBtn) this.prevBtn.disabled = true;

            // Apply high-end professional blur and loading state
            this.nextBtn.innerHTML = `
                <svg class="animate-spin -ml-1 mr-2.5 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Transmitting data...
            `;
            this.nextBtn.classList.add('opacity-75', 'cursor-not-allowed');

            if (this.wizardFrame) {
                this.wizardFrame.classList.add('pointer-events-none', 'blur-sm', 'scale-[0.99]', 'transition-all', 'duration-500');
            }
        } else {
            // Restore interactive components safely if processing failure matches criteria
            this.nextBtn.disabled = false;
            if (this.prevBtn) this.prevBtn.disabled = false;
            this.morphNavigationButtonStyles();

            if (this.wizardFrame) {
                this.wizardFrame.classList.remove('pointer-events-none', 'blur-sm', 'scale-[0.99]');
            }
        }
    }

    dispatchGlobalLifecycleNotification(eventName, contextDetails) {
        const structuralEvent = new CustomEvent(eventName, { detail: contextDetails });
        document.dispatchEvent(structuralEvent);
    }
}