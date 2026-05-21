/**
 * ============================================================================
 * PROPOSAL DATA STRUCTURES
 * 
 * NOTE TO DEVELOPERS: 
 * The `ProposalState` object acts as the baseline state on the client side. 
 * Before submission to the backend API, this object is mutated and validated 
 * against a strict Pydantic schema in Python.
 * 
 * Mapping to Backend Pydantic Models:
 * - ProposalState      ==>  ProposalSubmissionPayload (Root)
 * - applied_roles[]    ==>  ProposedRole
 * - deliverables[]     ==>  ProposalDeliverable
 * ============================================================================
 */

/**
 * @typedef {Object} ProposalDeliverable
 * @property {string} phase - Specific task/milestone title (max 70 chars).
 * @property {string} description - Detailed task breakdown (max 2000 chars).
 * @property {string} duration_unit - Time unit: 'DAYS', 'WEEKS', or 'MONTHS'.
 * @property {number} duration_value - Numeric duration constrained by the unit.
 * @property {number} release_percentage - Financial weight of milestone (Min 10.0, Max 100.0).
 * @property {number} rendering_order - Sequence position for UI rendering.
 */

/**
 * @typedef {Object} ProposedRole
 * @property {number} industry_id - Top-level service category ID.
 * @property {number} niche_id - Specific skill/expertise level ID.
 * @property {string} niche_name - Human-readable name of the expertise.
 * @property {number|null} role_amount - Standard cost of the role.
 * @property {number} proposed_amount - Custom price for this proposal (Min: $10.00).
 * @property {string} payment_plan - Strategy for release (e.g., 'SPLIT_50_50').
 * @property {ProposalDeliverable[]} deliverables - Array of milestones (Must sum to exactly 100%).
 */

/**
 * Initial baseline state for a proposal.
 * This structure is mutated by frontend interactions before payload compilation.
 * 
 * @type {Object}
 * @property {string} project_id - Becomes a UUID on submission.
 * @property {number} total_value - Sum of all proposed amounts (Min: $5.00).
 * @property {string} currency - Fixed to 'USD'.
 * @property {string|null} sent_at - ISO DateTime string set at dispatch.
 * @property {ProposedRole[]} applied_roles - At least one role must be applied for.
 */
export const ProposalState = {
    project_id: '',
    total_value: 0.00,
    currency: 'USD',
    sent_at: null,
    applied_roles: []
};

export const resetProposalState = () => {
    ProposalState.project_id = '';
    ProposalState.total_value = 0.00;
    ProposalState.currency = 'USD';
    ProposalState.sent_at = null;
    if (ProposalState.applied_roles) {
        ProposalState.applied_roles.length = 0;
    }
};