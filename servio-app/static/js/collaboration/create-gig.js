function gigData() {
    return {
        payload: {
            title: '',
            description: '',
            visibility: 'public',
            startDate: null,
            endDate: null,
            projectBudget: 0,
            roles: [
                { nicheId: '', professionalId: '', budget: 0, description: '', workload: 'Full-time (40h/wk)' }
            ]
        },

        taxonomy: JSON.parse($refs.taxonomy.textContent),

        professionalsFor(nicheId) {
            return this.taxonomy.find(n => n.id == nicheId)?.subcategories || [];
        },

        totalBudgetDisplay: '$0',

        updateBudget() {
            const sum = this.payload.roles.reduce((acc, r) => acc + (r.budget || 0), 0);
            if (sum <= this.payload.projectBudget) {
                this.totalBudgetDisplay = `$${sum.toLocaleString()}`;
            } else {
                // exceed project budget -> alert & update display to sum
                this.totalBudgetDisplay = `$${sum.toLocaleString()}`;
                showToast(
                    'The sum of all roles budgets exceeds the project budget. Adjust roles budgets.',
                    'warning',
                    'Budget Mismatch'
                );
            }
        },

        validateBudget() {
            // Ensure projectBudget >= sum of roles budgets
            const sum = this.payload.roles.reduce((acc,r) => acc + (r.budget||0), 0);
            if(this.payload.projectBudget < sum) {
                this.payload.projectBudget = sum;
                showToast(
                    'Project budget adjusted to match sum of roles budgets.',
                    'info',
                    'Budget Updated',
                );
            }
            this.updateBudget();
        },

        addRole() {
            this.payload.roles.push({ nicheId:'', professionalId:'', budget:0, description:'', workload:'Full-time (40h/wk)' });
        },

        removeRole(index) {
            this.payload.roles.splice(index,1);
            this.updateBudget();
        }
    }
}
