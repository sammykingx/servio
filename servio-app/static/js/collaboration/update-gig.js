function updateGigData(el) {
    return {
        payload: {
            title: el.dataset.title || '',
            description: el.dataset.description || '',
            projectBudget: Number(el.dataset.budget) || 0,
            visibility: el.dataset.visibility || 'public',
            startDate: el.dataset.startDate || '',
            endDate: el.dataset.endDate || '',

            // composed later
            roles: [],
            isNegotiable: false,
        },
        status: el.dataset.status,
        locked: false,
        budgetLocked: false,
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

        init() {
            this.locked = this.status === 'in_progress';
        },

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
           
            // Set initial content from payload
            this.editor.root.innerHTML = this.payload.description || '';

            // Listen for changes
            this.editor.on('text-change', (delta, oldDelta, source) => {
                if (source !== 'user') return; // only block user typing

                const plainText = this.editor.getText(); // includes trailing newline
                if (plainText.length > this.maxDescriptionLength) {
                    // Reject this input by undoing it
                    this.editor.updateContents(oldDelta.diff(this.editor.getContents()));
                } else {
                    // Normal update
                    this.payload.description = this.editor.root.innerHTML;
                }
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
            return this.payload.description
                ? this.payload.description.length
                : 0;
        },
    };
}

async function saveChanges() {
    const context = resolveGigPayload();
    
    if (!context) return;

    const { gigPayload, endpoint, csrf_token } = context;
    const errors = validatePayload(gigPayload);

    if (errors.length) {
        errors.forEach(msg =>
            showToast(msg, "error", "Validation Error")
        );
        return;
    }
    
    try {
        const response = await updateGig(gigPayload, endpoint, csrf_token);

        if (!response.ok) {
            // Server returned a non-2xx response
            const data = await response.json().catch(() => ({}));
            const msg = data.message || "Server rejected the request. Please check your input.";
            showToast(
                msg,
                data.status || "error",
                data.error || "Unable to Save gig/project data"
            );
            return;
        }

        const result = await response.json();

        showToast(
            result.message || "Gig successfully Updated!",
            result.staus || "success",
            "Action Successfull"
        );

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

    if (wordCount < 10) {
        errors.push("Project description must be descriptive enough for professionals to understand");
    }

    // Project timeline validation
    if (!startDate || !endDate) {
        errors.push("Project timeline(start/end dates) is required.");
    }

    const normalizedStartDate = parseDate(startDate);
    const normalizedEndDate = parseDate(endDate);
    const today = startOfToday();

    if (normalizedStartDate <= today) {
        errors.push('Start date must be greater than the current day.');
    }

    if (normalizedEndDate <= normalizedStartDate) {
        errors.push('End date must be greater than start date.');
    }

    const ONE_YEAR = 365 * 24 * 60 * 60 * 1000;
    if ((normalizedEndDate - normalizedStartDate) > ONE_YEAR) {
        errors.push('Project duration cannot exceed 1 year.');
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

                if (!role.workload) {
                    errors.push("Please select the workload");
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

async function updateGig(payload, endpoint, csrfToken) {
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

function parseDate(dateStr) {
    const date = new Date(dateStr);
    return isNaN(date.getTime()) ? null : date;
}

function startOfToday() {
    const d = new Date();
    d.setHours(0, 0, 0, 0);
    return d;
}
