/* * COMPONENT: deliverablesManager
 * -------------------------------------------------------------------------
 * OBJECTIVE: Orchestrates the creation and formatting of gig deliverables.
 * * KEY FEATURES:
 * - Dynamic Scaling: Allows users to add multiple items while ensuring at least one remains.
 * - Business Rules: 'getValueOptions' enforces specific limits (e.g., max 6 days, 4 weeks) 
 * to ensure data consistency before submission.
 * - Payload Mapping: Converts UI-friendly keys (title, unit) to backend-expected 
 * keys (description, duration_unit).
 * -------------------------------------------------------------------------
 */

/**
 * Manages a dynamic list of project deliverables and their associated timelines.
 * * Responsibilities:
 * 1. Lifecycle Management: Initializes with one empty deliverable and handles CRUD operations (Add/Remove).
 * 2. Input Validation Logic: Dynamically generates duration options (days, weeks, months) based on unit-specific limits.
 * 3. Identity Tracking: Uses high-entropy unique IDs (timestamp + random) for reliable DOM diffing in Alpine.js.
 * 4. Data Transformation: Maps internal UI state to the specific schema required by the backend API via buildPayload.
 * * @returns {Object} A reactive manager for handling deliverable line items.
 */
function deliverablesManager() {
    return {
        items: [],

        init() {
            this.addDeliverable();
        },

        addDeliverable() {
            this.items.push({
                id: Date.now() + Math.random(),
                title: '',
                unit: 'days',
                value: 1,
                due_by: ''
            });
        },

        removeItem(id) {
            if (this.items.length > 1) {
                this.items = this.items.filter(item => item.id !== id);
            }
        },

        getValueOptions(unit) {
            const limits = { 'days': 6, 'weeks': 4, 'months': 12 };
            const max = limits[unit] || 0;
            return Array.from({ length: max }, (_, i) => i + 1);
        },

        buildPayload() {
            return this.items.map(item => ({
                description: item.title,
                duration_unit: item.unit,
                duration_value: item.value,
                due_date: item.due_by
            }));
        },
    }
}