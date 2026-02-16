/* * COMPONENT: roleApplicationManager
 * -------------------------------------------------------------------------
 * OBJECTIVE: Manages a batch of potential job/role applications within a single view.
 * * KEY FEATURES:
 * - Reactive Initialization: Uses .map() to spread initial data while injecting 
 * defaults for 'proposed_amount' and 'isActive'.
 * - Smart Interaction: 'updateRoleField' includes a quality-of-life feature 
 * that auto-selects a checkbox if the user starts typing an amount.
 * - Submission Sanitization: 'buildPayload' ensures that only roles explicitly 
 * flagged as 'active' are sent to the server, preventing empty data submissions.
 * -------------------------------------------------------------------------
 */

// ---------------------------------------------------------------

/**
 * Orchestrates the selection and configuration of multiple role applications.
 * * Responsibilities:
 * 1. State Decoration: Transforms raw role data into reactive application objects with UI-specific flags (isActive).
 * 2. Intent-Based Logic: Automatically activates a role application when a user interacts with its specific fields.
 * 3. Conditional Access Control: Manages field disablement based on external 'canApply' permissions.
 * 4. Selective Payload Construction: Filters and sanitizes the local state to return only active applications for backend submission.
 * * @param {Array} initialRoles - Raw role data objects from the server.
 * @returns {Object} A reactive state manager for role-based applications.
 */
function roleApplicationManager(initialRoles = []) {
    return {
        applications: initialRoles.map(role => ({
            ...role,
            proposed_amount: role.role_amount,

        })),

        toggleRole(nicheId) {
            const role = this.applications.find(a => a.niche_id === nicheId);
            if (role) role.isActive = !role.isActive;
            updateProposalUI(this.getSummary());
        },

        updateRoleField(nicheId, field, value) {
            const role = this.applications.find(a => a.niche_id === nicheId);
            if (role) {
                role[field] = value;
                // Implicitly check the box if they interact with fields
                if (value !== '' && value !== null) {
                    role.isActive = true;
                }
                updateProposalUI(this.getSummary());
            }
        },

        isRoleActive(roleId) {
            const role = this.applications.find(a => a.niche_id === roleId);
            return role ? role.isActive : false;
        },

        isFieldDisabled(roleId, canApply) {
            if (!canApply) return true;
            return false;
        },

        /**
         * Returns calculated totals for active roles
         */
        getSummary() {
            const activeRoles = this.applications.filter(app => app.isActive);
            const subtotal = activeRoles.reduce((sum, app) => {
                const price = parseFloat(app.proposed_amount) || parseFloat(app.role_amount) || 0;
                return sum + price;
            }, 0);

            const serviceFee = subtotal * 0.05;

            return {
                count: activeRoles.length,
                subtotal: subtotal,
                serviceFee: serviceFee,
                total: subtotal + serviceFee
            };
        },

        buildPayload() {
            return this.applications
                .filter(app => app.isActive)
                .map(app => ({
                    industry_id: app.industry_id,
                    niche_id: app.niche_id,
                    role_amount: app.role_amount,
                    proposed_amount: app.proposed_amount,
                    payment_plan: app.payment_plan
                }));
        }
    }
}

