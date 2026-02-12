async function sendProposal() {

    const gigSummary = document.getElementById('gig-summary-section');
    const roleApplicationsEl = document.querySelector('[x-ref="roleApplicationsUnit"]');
    const projectRoleEl = document.querySelector('[x-ref="projectRole"]');
    const deliverablesEl = document.querySelector('[x-ref="deliverablesUnit"]');

    const errorTitle = "Session Out of Sync";
    const errorMsg = "Required project data could not be loaded. A quick refresh will resolvee/fix this.";

    if (!gigSummary) {
        showToast(errorMsg, "info", errorTitle)
        return;
    }

    const gigHasRoles = gigSummary.dataset.hasRoles === 'true';

    const deliverablesPayload = Alpine.$data(deliverablesEl).buildPayload();

    let roleApplicationPayload;
    if (gigHasRoles) {
        roleApplicationPayload = Alpine.$data(roleApplicationsEl).buildPayload();
    } else {
        roleApplicationPayload = Alpine.$data(projectRoleEl).buildPayload();
    }

    // 3. Construct the master payload
    const masterPayload = {
        deliverables: deliverablesPayload,
        applied_roles: roleApplicationPayload,
        // client: clientPayload,
        sent_at: new Date().toISOString()
    };

    console.log("Master Payload ready for Backend:", JSON.stringify(masterPayload, null, 2));

    // await fetch('/api/proposals', { method: 'POST', body: JSON.stringify(masterPayload) });
}

function roleApplicationManager(initialRoles = []) {
    return {
        applications: initialRoles.map(role => ({
            ...role,
            isActive: false,
            proposed_amount: role.role_amount,
            payment_plan: ''
        })),

        toggleRole(nicheId) {
            const role = this.applications.find(a => a.niche_id === nicheId);
            if (role) role.isActive = !role.isActive;
        },

        updateRoleField(nicheId, field, value) {
            const role = this.applications.find(a => a.niche_id === nicheId);
            if (role) {
                role[field] = value;
                // Implicitly check the box if they interact with fields
                if (value !== '' && value !== null) {
                    role.isActive = true;
                }
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