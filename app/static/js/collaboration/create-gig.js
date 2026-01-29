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
        descriptionLength: 0,
        rolesTotalAmount: 0,
        maxDescriptionLength: 2000,
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

        initQuill() {
            this.editor = new Quill('#quill-editor', {
                theme: 'snow',
                modules: {
                    toolbar: '#quill-toolbar'
                },
                formats: [
                    'bold', 'italic', 'underline',
                    'list', 'header', 'font', 'align',
                ],
            });
           
            // this.editor.setSelection(0, 0);

            // this.editor.root.innerHTML = this.payload.description || '';

            this.editor.on('text-change', (delta, oldDelta, source) => {
                if (source !== 'user') return;

                const text = this.editor.getText().replace(/\n$/, '');
                const length = text.length;

                // Always update reactive counter
                this.descriptionLength = length;

                // If user exceeded limit, remove only the extra input
                if (length > this.maxDescriptionLength) {
                    const excess = length - this.maxDescriptionLength;

                    const range = this.editor.getSelection();
                    if (!range) return;

                    // Remove only the extra characters typed
                    this.editor.deleteText(range.index - excess, excess, 'silent');
                    this.editor.setSelection(this.maxDescriptionLength, 0, 'silent');

                    this.descriptionLength = this.maxDescriptionLength;
                    return;
                }

                // Normal update
                this.payload.description = this.editor.root.innerHTML;
            });

        },

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
        },

        setProjectBudget(amount) {
            this.payload.projectBudget = Number(amount) || 0;
        },

        enforceDescriptionLimit() {
            if (!this.payload.description) return;

            if (this.payload.description.length > this.maxDescriptionLength) {
                this.payload.description =
                    this.payload.description.slice(0, this.maxDescriptionLength);
            }
        },

        descriptionCount() {
            return this.descriptionLength;
        },
    };
}

async function submitBtn(action="publish") {
    const context = resolveGigPayload();
    if (!context) return;

    const ALLOWED_ACTIONS = ['publish', 'draft'];

    if (!ALLOWED_ACTIONS.includes(action)) {
        showToast(
            "Oops! Something went wrong. Please try again.",
            "error",
            "Invalid Action"
        );
        return;
    }

    const { gigPayload, endpoint, csrf_token } = context;

    const errors = validatePayload(gigPayload);

    if (errors.length) {
        errors.forEach(msg =>
            showToast(msg, "error", "Validation Error")
        );
        return;
    }

    const body = { action, payload: gigPayload };
    
    try {
        const response = await publishGig(body, endpoint, csrf_token);

        if (!response.ok) {
            // Server returned a non-2xx response
            const data = await response.json().catch(() => ({}));
            const msg = data.message || "Server rejected the request. Please check your input.";
            showToast(msg, "error", "Unable to publish gig");
            return;
        }

        const result = await response.json();

        showToast(result.message || "Gig successfully published!", "success", "Action Successfull");
        if (result?.url) {
            setTimeout(() => {
                window.location.assign(result.url);
            }, 2000);
        }
    } catch (err) {
        // Client-side error (network, fetch blocked, etc.)
        return;
    }

}

function resolveGigPayload() {
    const gigEl = document.querySelector('[data-gig-data]');
    if (!gigEl) {
        showToast(
            "Required gig data is missing. Please refresh the page and try again.",
            "error", "Initialization Error"
        );
        return null;
    }

    const endpoint = gigEl.dataset.endpoint;
    const csrf_token = gigEl.dataset.csrfToken;

    if (!endpoint) {
        showToast("API endpoint is not configured.", "error", "Configuration Error");
        return;
    }

    const gig = Alpine.$data(gigEl);

    if (!gig || !gig.payload) {
        showToast(
            "Something went wrong while preparing your gig. Please reload and try again.",
            "error",
            "Unable to publish gig"
        );
        return null;
    }

    return {
        gigPayload: gig.payload,
        endpoint,
        csrf_token,
    };
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

    if (wordCount < 6) {
        errors.push("Project description must be descriptive enough for professionals to understand");
    }

    if (description.length > 2000) {
        errors.push("Project description is too long. Maximum allowed length is 2000 characters.");
    }

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
            
            if (Number(role.budget < 30)) {
                errors.push("Minimum budget is $30");
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

                if (!role.paymentOption) {
                    errors.push("Please select a payment option");
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

async function publishGig(payload, endpoint, csrfToken) {
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify(payload),
        });

        return response;
    } catch (err) {
        showToast(
            "We couldn't reach the server. Please check your internet connection and try again.",
            "error",
            "Client Side Error"
        );
        throw err;
    }
}
