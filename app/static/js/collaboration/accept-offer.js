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
    const projectEndDate = gigSummary.dataset.endDate;
    const csrfToken = gigSummary.dataset.csrfToken;
    const endPoint = gigSummary.dataset.endPoint;

    let roleApplicationPayload;
    if (gigHasRoles) {
        roleApplicationPayload = Alpine.$data(roleApplicationsEl).buildPayload();
    } else {
        roleApplicationPayload = Alpine.$data(projectRoleEl).buildPayload();
    }

    // validating applied roles
    let { isValid, errorContext } = validateAppliedRoles(roleApplicationPayload);
    if (!isValid) {
        showToast(errorContext.message, errorContext.type, errorContext.title);
        return;
    }

    // validating deliverables
    isValid, errorContext = validateDeliverables(deliverablesPayload, projectEndDate);
    if (!isValid) {
        showToast(errorContext.message, errorContext.type, errorContext.title);
        return;
    }

    // 3. Construct the master payload
    const masterPayload = {
        deliverables: deliverablesPayload,
        applied_roles: roleApplicationPayload,
        sent_at: new Date().toISOString()
    };

    // console.log("Master Payload ready for Backend:", JSON.stringify(masterPayload, null, 2));

    try {
        const response = await sendPayload(masterPayload, endPoint, csrfToken);
        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            const msg = data.message || "Server rejected the request. Please check your input.";
            showToast(msg, "error", "Unable to send proposal");
            return;
        }
        showToast(
            data.message || "Your proposal is officially in the creator's hands. We'll ping you the moment they take a look.",
            "success",
            data.title || "Your Proposal is Live!"
        );
        if (data?.url) {
            setTimeout(() => {
                window.location.assign(result.url);
            }, 2000);
        }
    } catch (err) {
        // The "catch" in sendPayload already showed a toast, 
        // but you can do extra cleanup here if needed.
        return;
    }
}

const validateDeliverables = (deliverables, projectEndDateStr) => {
    if (!deliverables || deliverables.length === 0) {
        return {
            isValid: false,
            errorContext: {
                title: "Deliverables Required",
                message: "Your proposal must include at least one deliverable to outline the value you'll provide.",
                type: 'warning',
            }
        };
    }

    const projectEndDate = new Date(projectEndDateStr);
    const maxDueDate = new Date(projectEndDate);
    maxDueDate.setDate(maxDueDate.getDate() - 3);

    let errorContext = null;

    const isValid = deliverables.every((item, index) => {
        const itemNumber = index + 1;

        // 1. Check for empty fields
        for (const [key, value] of Object.entries(item)) {
            if (value === null || value === undefined || value === "") {
                errorContext = {
                    title: "Missing Required Info",
                    message: `Deliverable #${itemNumber} has an empty ${key.replace('_', ' ')}.`,
                    type: 'warning',
                };
                return false;
            }
        }

        // 2. Description length (Min 10 words)
        const wordCount = item.description.trim().split(/\s+/).length;
        if (wordCount < 10) {
            errorContext = {
                title: "Description Too Short",
                message: `Deliverable #${itemNumber} description needs at least 10 words (currently ${wordCount}).`,
                type: 'warning',
            };
            return false;
        }

        // 3. Due Date logic
        const itemDueDate = new Date(item.due_date);
        if (itemDueDate > maxDueDate) {
            errorContext = {
                title: "Invalid Due Date",
                message: `Deliverable #${itemNumber} must be due by ${maxDueDate.toLocaleDateString()} (3 days before project end).`,
                type: 'warning',
            };
            return false;
        }

        return true;
    });

    return { isValid, errorContext };
};

/**
 * Validates the applied roles array to ensure all object attributes are present and meaningful.
 * * Performs a strict check:
 * - Rejects null, undefined, or empty strings.
 * - Rejects strings consisting only of whitespace.
 * - Short-circuits on the first error found to optimize performance.
 * * @param {Array<Object>} appliedRoles - An array of role objects to validate.
 * @returns {Object} Result object containing:
 * @property {boolean} isValid - True if all roles pass validation.
 * @property {Object|null} errorContext - Details about the failure, or null if valid.
 * @property {string} errorContext.title - A user-friendly error category.
 * @property {string} errorContext.message - Specific details identifying the role index and field.
 * @property {string} errorContext.type - The severity level for UI components (e.g., 'warning').
 */
const validateAppliedRoles = (appliedRoles) => {
    if (!appliedRoles || appliedRoles.length === 0) {
        return {
            isValid: false,
            errorContext: {
                title: "Roles Required",
                message: "Please add at least one role you are applying for before proceeding.",
                type: 'warning',
            }
        };
    }

    let errorContext = null;
    const isValid = appliedRoles.every((role, index) => {
        const roleNumber = index + 1;

        for (const [key, value] of Object.entries(role)) {

            const isInvalidString = typeof value === 'string' && value.trim().length === 0;
            const isMissing = value === null || value === undefined || value === "";

            if (isMissing || isInvalidString) {
                errorContext = {
                    title: "Invalid Role Data",
                    message: `Role #${roleNumber} has an invalid or empty ${key.replace('_', ' ')}.`,
                    type: 'warning',
                };
                return false;
            }
        }
        return true;
    });

    return { isValid, errorContext };
};