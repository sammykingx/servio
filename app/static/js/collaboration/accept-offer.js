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
