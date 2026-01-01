function gigData() {
    return {
        payload: {
            title: '',
            description: '',
            projectBudget: 5000,
            visibility: 'public',

            // composed later
            roles: [],
            startDate: null,
            endDate: null,
            isNegotiable: false,
        },
        budgetLocked: false,
        rolesTotalAmount: 0,

        setRoles(roles) {
            this.payload.roles = roles;
            
            const rolesTotal = roles.reduce(
                (sum, r) => sum + (Number(r.budget) || 0), 0
            );

            this.rolesTotalAmount = rolesTotal;

             const shouldLock = rolesTotal > this.payload.projectBudget;

            // Only reacting on state change
            if (shouldLock !== this.budgetLocked) {
                this.budgetLocked = shouldLock;

                if (shouldLock) {
                    this.payload.projectBudget = rolesTotal;

                    showToast(
                        'Project budget locked to match the total cost of required roles.',
                        'warning',
                        'Project Budget Locked'
                    );
                } else {
                    showToast(
                        'Project Budget is now unlocked for user interaction.',
                        'success',
                        'Project budget unlocked',
                    );
                }
            }

            // console.log(`Total budget: $${this.payload.projectBudget}, roles total: $${rolesTotal}`);
        },

        setProjectBudget(amount) {
            this.payload.projectBudget = Number(amount) || 0;
        },

        roleColors: [
            'bg-success-400',
            'bg-blue-500',
            'bg-purple-500',
            'bg-orange-500',
            'bg-pink-500',
            'bg-teal-500',
            'bg-indigo-500',
            'bg-emerald-500',
            'bg-rose-500',
            'bg-cyan-500',
        ],
    };
}

function submitBtn() {
    const gigEl = document.querySelector('[data-gig-data]');
    if (!gigEl) {
        showToast(
            "Required gig data is missing. Please refresh the page and try again.",
            "error", "Unable to publish gig"
        );
        return;
    }

    const gig = Alpine.$data(gigEl);

    if (!gig || !gig.payload) {
        showToast(
            "Something went wrong while preparing your gig. Please reload and try again.",
            "error",
            "Unable to publish gig"
        );
        return;
    }
    const payload = gig.payload;

    // data validation
    const errors = validatePayload(payload);

    if (errors.length) {
        errors.forEach(msg =>
            showToast(msg, "error", "Validation Error")
        );
        return;
    }

    console.log('Gig payload:', JSON.stringify(payload, null, 2));
    showToast("Payload collected! Check console", "success", "Gig ready");

    // ✅ Safe to submit
    // submitGig(payload);

}

function validatePayload(gigPayload) {
  const errors = [];

    if (!gigPayload) {
        errors.push("Gig data is missing.");
        return errors;
    }

    const { title, description, projectBudget, startDate, endDate, roles } = gigPayload;

    if (!title || title.trim().length < 10) {
        errors.push("Project title must be meaningful");
    }

    const wordCount = description.trim().match(/\b\w+\b/g)?.length || 0;

    if (wordCount < 10) {
        errors.push("Project description must be descriptive enough for professionals to understand");
    }

    // --- Date validation ---
    if (!startDate || !endDate) {
        errors.push("Project timeline(start/end dates) is required.");
    }

    if (!projectBudget || Number(projectBudget) <= 0) {
        errors.push("Project budget must be greater than 0.");
    }

    let totalRolesBudget = 0;

    if (Array.isArray(roles) && roles.length > 0) {
        roles.forEach((role, index) => {
            if (!role.professional) {
                errors.push(`Please select a professional for the role "${role.niche}"`);
            }
            
            // Only validate active roles
            if (role.niche && role.professional && Number(role.budget) > 0) {
                totalRolesBudget += Number(role.budget);

                if (totalRolesBudget <= 0) {
                    errors.push("Total roles budget must be greater than 0.");
                }

                const descriptionCount = role.description.trim().match(/\b\w+\b/g)?.length || 0;
            
                if (descriptionCount < 10) {
                    errors.push(`Please provide a meaningful description for "${role.professional || role.niche}" to understand.`);
                }
            }
        });
    }

    if (
        Number(projectBudget) < totalRolesBudget
    ) {
        errors.push(
            "Project budget cannot be lower than the total cost of all roles."
        );
    }

    return errors;
    
}