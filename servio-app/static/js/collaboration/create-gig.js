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
        },

        buildBase() {
            return {
                title: this.payload.title.trim(),
                description: this.payload.description.trim(),
                projectBudget: Number(this.payload.projectBudget),
                visibility: this.payload.visibility,
            };
        },

        setRoles(roles) {
            this.payload.roles = roles;
        },
    };
}

function submitBtn() {
    // Get the gigData Alpine component from the DOM
    const gigEl = document.querySelector('[data-gig-data]');
    if (!gigEl) {
        showToast("Gig data not found", "error", "Error");
        return;
    }

    const gig = Alpine.$data(gigEl);
    const payload = gig.payload;

    // For now, just show it in console or for validation
    console.log('Gig payload:', JSON.stringify(payload, null, 2));


    showToast("Payload collected! Check console", "success", "Success");
}

