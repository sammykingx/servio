class ProjectDataCollector {
    constructor() {
        this.selectors = {
            currencyFields: '[data-currency-format]',
            startDate: '#start-date',
            endDate: '#end-date',
            totalBudget: '#total-budget',
            // Specifically targeted data attribute
            roleInputs: '[data-role-budget-input]'
        };
    }

    /**
     * HEALTH CHECK: Ensures the DOM has everything the class needs
     */
    verify() {
        const criticalFields = ['startDate', 'endDate', 'totalBudget', 'currencyFields'];
        const missing = [];

        criticalFields.forEach(key => {
            if (!document.querySelector(this.selectors[key])) {
                missing.push(this.selectors[key]);
            }
        });

        if (missing.length > 0) {
            if (typeof showToast === 'function') {
                showToast("Project editor failed to load core components.", "error", "Configuration Error");
            }
            return false;
        }
        return true;
    }

    /**
     * Applies live formatting to all currency fields
    */
    init() {
        if (!this.verify()) return;

        document.querySelectorAll(this.selectors.currencyFields).forEach(input => {
            input.addEventListener('input', (e) => this.formatDisplay(e));
        });
    }

    /**
     * UI Layer - Prevents alphabets and adds commas live
     */
    formatDisplay(e) {
        let cursorPosition = e.target.selectionStart;
        let originalLength = e.target.value.length;

        // Strip everything except numbers and one decimal point
        let value = e.target.value.replace(/[^0-9.]/g, '');
        const parts = value.split('.');
        if (parts.length > 2) value = parts[0] + '.' + parts.slice(1).join('');

        if (value !== '') {
            const [integerPart, decimalPart] = value.split('.');
            let formatted = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
            if (decimalPart !== undefined) formatted += '.' + decimalPart.substring(0, 2);
            e.target.value = formatted;
        }

        // Fix cursor jumping
        let newLength = e.target.value.length;
        cursorPosition = cursorPosition + (newLength - originalLength);
        e.target.setSelectionRange(cursorPosition, cursorPosition);
    }

    static sanitizeCurrency(value) {
        if (!value) return 0;
        return parseFloat(value.toString().replace(/,/g, '')) || 0;
    }

    getIdentityData() {
        return {
            start_date: document.querySelector(this.selectors.startDate)?.value || null,
            end_date: document.querySelector(this.selectors.endDate)?.value || null,
            project_budget: ProjectDataCollector.sanitizeCurrency(
                document.querySelector(this.selectors.totalBudget)?.value
            )
        };
    }

    /**
     * Roles data array: 
     * iterate directly over the inputs and pull data from their own dataset.
     */
    getRolesData() {
        const inputs = document.querySelectorAll(this.selectors.roleInputs);

        return Array.from(inputs).map(input => ({
            industry_id: input.dataset.industryId,
            role_id: input.dataset.roleId,
            amount: ProjectDataCollector.sanitizeCurrency(input.value)
        }));
    }

    getPayload() {
        return this.validate({
            ...this.getIdentityData(),
            roles: this.getRolesData()
        });
    }

    validate(payload) {
        const rolesTotal = payload.roles.reduce((sum, r) => sum + r.amount, 0);

        return {
            ...payload,
            metadata: {
                roles_sum: rolesTotal,
                is_balanced: rolesTotal === payload.project_budget,
            }
        };
    }
}