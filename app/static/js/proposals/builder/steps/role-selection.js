import { ProposalState } from "../payload.js";


export class Step2RoleSelectionManager {
    constructor() {
        this.state = ProposalState;
    }

    init() {
        this.registerStep2Events();
    }

    registerStep2Events() {
        // Listen to native header card accordion clicks
        document.querySelectorAll('.role-accordion-trigger').forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                const roleId = e.currentTarget.getAttribute('data-target-id');
                this.toggleAccordion(roleId);
            });
        });

        // Listen to inside state toggle switches
        document.querySelectorAll('.role-toggle-switch').forEach(toggle => {
            toggle.addEventListener('click', (e) => {
                const btn = e.currentTarget;
                const card = btn.closest('[data-niche-id]');

                if (!card) return;

                // Extract all specified architectural dataset keys from card
                const roleData = {
                    industry_id: card.getAttribute('data-industry-id') || '',
                    niche_id: card.getAttribute('data-niche-id') || '',
                    niche_name: card.getAttribute('data-niche-name') || '',
                    role_amount: parseFloat(card.getAttribute('data-budget')) || 0.00,
                    proposed_amount: 0.00,
                    payment_plan: card.getAttribute('data-payment-plan') || 'split_50_50'
                };

                this.handleRoleToggleSelection(roleData, btn);
            });
        });
    }

    toggleAccordion(roleId) {
        const drawer = document.getElementById(`role-drawer-${roleId}`);
        const chevron = document.getElementById(`role-chevron-${roleId}`);
        if (!drawer) return;

        if (drawer.classList.contains('max-h-0')) {
            drawer.classList.remove('max-h-0', 'opacity-0', 'border-transparent');
            drawer.classList.add('max-h-[500px]', 'opacity-100', 'border-gray-200', 'dark:border-gray-800');
            if (chevron) chevron.classList.add('rotate-180');
        } else {
            drawer.classList.remove('max-h-[500px]', 'opacity-100', 'border-gray-200', 'dark:border-gray-800');
            drawer.classList.add('max-h-0', 'opacity-0', 'border-transparent');
            if (chevron) chevron.classList.remove('rotate-180');
        }
    }

    handleRoleToggleSelection(roleData, toggleButton) {
        const isChecked = toggleButton.getAttribute('aria-checked') === 'true';
        const shouldSelect = !isChecked;

        const knob = document.getElementById(`role-toggle-knob-${roleData.niche_id}`);
        const badge = document.getElementById(`role-badge-${roleData.niche_id}`);
        const dot = document.getElementById(`role-dot-${roleData.niche_id}`);

        toggleButton.setAttribute('aria-checked', String(shouldSelect));

        if (shouldSelect) {
            toggleButton.classList.remove('bg-gray-200', 'dark:bg-gray-800');
            toggleButton.classList.add('bg-brand-500');
            if (knob) knob.classList.add('translate-x-5');
            if (badge) badge.classList.remove('hidden');
            if (dot) {
                dot.classList.remove('bg-gray-300', 'dark:bg-gray-700');
                dot.classList.add('bg-brand-500');
            }

            if (!this.state.applied_roles.some(item => item.niche_id === roleData.niche_id)) {
                this.state.applied_roles.push({
                    industry_id: roleData.industry_id,
                    niche_id: roleData.niche_id,
                    niche_name: roleData.niche_name,
                    role_amount: roleData.role_amount,
                    proposed_amount: roleData.proposed_amount,
                    payment_plan: roleData.payment_plan,
                    deliverables: []
                });
            }
        } else {
            // Revert UI State styles to Inactive colors
            toggleButton.classList.remove('bg-brand-500');
            toggleButton.classList.add('bg-gray-200', 'dark:bg-gray-800');
            if (knob) knob.classList.remove('translate-x-5');
            if (badge) badge.classList.add('hidden');
            if (dot) {
                dot.classList.remove('bg-brand-500');
                dot.classList.add('bg-gray-300', 'dark:bg-gray-700');
            }

            // Strip the role object out of state completely
            this.state.applied_roles = this.state.applied_roles.filter(item => item.niche_id !== roleData.niche_id);
        }

        // console.log("Synchronized Applied Roles Array Context:", JSON.stringify(this.state.applied_roles, null, 2));
    }
}
