function intentForm() {
    return {
        intents: [{
                key: "book_services",
                label: "Book professional services"
            },
            {
                key: "create_gigs",
                label: "Create gigs/projects"
            },
            {
                key: "collaborate",
                label: "Collaborate"
            }
        ],

        selectedIntents: [],

        submitting: false,
        showProcessing: false,

        toggleIntent(key) {
            if (this.selectedIntents.includes(key)) {
                this.selectedIntents =
                    this.selectedIntents.filter(i => i !== key);
                return;
            }

            this.selectedIntents.push(key);
        },

        toggleAll() {
            if (this.selectedIntents.length === this.intents.length) {
                this.selectedIntents = [];
            } else {
                this.selectedIntents =
                    this.intents.map(i => i.key);
            }
        },

        isSelected(key) {
            return this.selectedIntents.includes(key);
        },

        buildPayload() {
            return {
                intents: this.selectedIntents
            };
        },

        async saveIntent() {
            if (this.selectedIntents.length === 0) {
                showToast(
                    "Please select at least one option to continue.",
                    "warning",
                    "Can't Proceed yet"
                );
                return;
            }
            const payload = this.buildPayload();

            this.submitting = true;
            this.showProcessing = true;

            try {
                const response = await this.sendPayload(payload);
                const data = await response.json();
                if (!response.ok) {

                    showToast(
                        data.message || "Unable to save expertise",
                        "error",
                        data.error || "Operation Error"
                    );
                    return;
                }
                console.log("DONE");

                if (data.redirect_url) {
                    window.location.assign(data.redirect_url);
                }

            } catch (err) {
                showToast("Network error, try again", "error");
            } finally {
                this.submitting = false;
                this.showProcessing = false;
            }

        },

        async skipStep() {
            const payload = { skip: true };
            const url = this.$root.dataset.completeUrl;

            this.submitting = true;
            this.showProcessing = false;

            try {
                const response = await this.sendPayload(payload);

                if (!response.ok) {
                    showToast(
                        data.message || "Unable to skip current step at this time, try in a few minutes.",
                        "error",
                        data.error || "Operation Error"
                    );
                    return;
                }

                window.location.assign(url);

            } catch (err) {
                showToast("Network error, try again", "error");
            } finally {
                this.submitting = false;
            }
        },

        async sendPayload(payload) {
            return await fetch(".", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": document.querySelector(
                        "[name=csrfmiddlewaretoken]"
                    ).value
                },
                body: JSON.stringify(payload)
            });
        },
    }
}