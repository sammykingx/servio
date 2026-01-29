function expertiseForm() {
    return {
        maxNiches: 3,
        maxBioWords: 30,
        bioWordCount: 0,

        taxonomy: [],
        industryId: null,
        experience: "",
        bio: "",

        selectedNiches: [],

        submitting: false,

        init() {
            this.taxonomy = JSON.parse(
                document.getElementById("taxonomy").textContent
            );

            // defaults for industry
            if (this.taxonomy.length) {
                this.industryId = this.taxonomy[0].id;
            }
            this.experience = "0-2";
            this.bioWordCount = this.countWords(this.bio || "")

            this.$watch("industryId", () => {
            this.selectedNiches = [];
    });
        },

        get industry() {
            return this.taxonomy.find(i => i.id === this.industryId) || null;
        },

        get niches() {
            return this.industry ? this.industry.subcategories : [];
        },

        toggleNiche(niche) {
            const exists = this.selectedNiches.find(n => n.id === niche.id);

            if (exists) {
                this.selectedNiches = this.selectedNiches.filter(
                    n => n.id !== niche.id
                );
                return;
            }

            if (this.selectedNiches.length >= this.maxNiches) {
                showToast(
                    `You can select up to ${this.maxNiches} niches`,
                    "warning"
                );
                return;
            }

            this.selectedNiches.push({
                id: niche.id,
                name: niche.name
            });
        },

        isSelected(nicheId) {
            return this.selectedNiches.some(n => n.id === nicheId);
        },

        buildPayload() {
            return {
                industry: {
                    id: this.industry?.id || null,
                    name: this.industry?.name || null,
                },
                niches: this.selectedNiches,
                experience_level: this.experience,
                bio: this.bio.trim(),
            };
        },

        async submit() {
            const payload = this.buildPayload();

            if (!payload.industry.id) {
                showToast("Please select an industry from the dropdown", "warning", "Industry Required");
                return;
            }

            if (!payload.niches.length) {
                showToast("Select at least one niche to proceed", "warning", "Niche Required");
                return;
            }

            if (!payload.bio) {
                showToast("Professional bio is required to procee", "warning", "Bio required");
                return;
            }

            this.submitting = true;

            try {
                const response = await fetch(".", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": document.querySelector(
                            "[name=csrfmiddlewaretoken]"
                        ).value
                    },
                    body: JSON.stringify(payload)
                });

                const data = await response.json();

                if (!response.ok) {
                    showToast(
                        data.message || "Unable to save expertise",
                        "error",
                        data.error || "Operation Error"
                    );
                    return;
                }

                if (data.redirect_url) {
                    window.location.assign(data.redirect_url);
                }
            } catch (err) {
                console.log(err);
                showToast("Network error, try again", "error");
            } finally {
                this.submitting = false;
            }
        },

        countWords(text) {
            return text
                .trim()
                .split(/\s+/)
                .filter(Boolean)
                .length;
        },

        enforceBioLimit() {
            this.bioWordCount = this.countWords(this.bio);

            if (this.bioWordCount > this.maxBioWords) {
                this.bio = this.bio
                    .trim()
                    .split(/\s+/)
                    .slice(0, this.maxBioWords)
                    .join(" ");

                this.bioWordCount = this.maxBioWords;
            }
        },
    }
}

function validatePayload(payload) {

}
