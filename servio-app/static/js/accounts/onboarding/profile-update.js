function onboardingProfile() {
    return {
        payload: {
            profile: {
                phoneCountryCode: "",
                phoneNumber: "",
                altNumber: "",
            },
            address: {
                street: "",
                street_line_two: "",
                city: "",
                state: "",
                postal_code: "",
                country: "",
            }
        },

        submitting: false,

        async submit() {
            if (this.submitting) return;

            const normalizedData = normalizeProfileData(this.payload);
            const errors = validateProfileData(normalizedData);

            if (errors.length) {
                errors.forEach(msg =>
                    showToast(msg, "error", "Validation Error")
                );
                return;
            }

            try {
                this.submitting = true;
                const response = await sendProfileData(normalizedData);
                console.log(response);
                if (!response.ok) {
                    // Server returned a non-2xx response
                    const data = await response.json().catch(() => ({}));
                    const msg = data.message || "Server rejected the request. Please check your input.";
                    showToast(
                        msg,
                        data.status || "error",
                        data.error || "Profile Update Error"
                    );
                    return;
                }
                const data = await response.json();
                console.log(data);
                if (data.redirect_url) {
                    window.location.assign(data.redirect_url);
                }
    
            } catch (err) {
                showToast(
                    "Network error. Please try again.",
                    "error",
                    "Submission Failed"
                );
            } finally {
                this.submitting = false;
            }
        },
    }
}

const sanitizeString = (value) =>
    typeof value === "string"
        ? value.trim().replace(/\s+/g, " ")
        : "";

const sanitizePhone = (value) =>
    typeof value === "string"
        ? value.replace(/\D/g, "")
        : "";

function normalizeProfileData(data) {
    return {
        profile: {
            phoneCountryCode: sanitizeString(data.profile.phoneCountryCode),
            phoneNumber: sanitizePhone(data.profile.phoneNumber),
            altNumber: sanitizePhone(data.profile.altNumber),
        },
        address: {
            street: sanitizeString(data.address.street),
            street_line_two: sanitizeString(data.address.street_line_two),
            city: sanitizeString(data.address.city),
            state: sanitizeString(data.address.state),
            postal_code: sanitizeString(data.address.postal_code),
            country: sanitizeString(data.address.country),
        },
    };
}


function validateProfileData(data) {
    const errors = [];

    if (!data.profile.phoneCountryCode) {
        errors.push("Country code is required");
    }

    if (!data.profile.phoneNumber) {
        errors.push("Phone number is required");
    } else if (data.profile.phoneNumber.length < 10) {
        errors.push("Invalid phone number");
    }

    if (data.profile.altNumber) {
        if (data.profile.altNumber.length < 10) {
            errors.push("Alternate Phone number is invalid");
        }
    }

    if (!data.address.street) {
        errors.push("Street address is required");
    }
    if (!data.address.city) {
        errors.push("city is required");
    }
    if (!data.address.state) {
        errors.push("state is required");
    }
    if (!data.address.country) {
        errors.push("country is required");
    }

    return errors;
}

async function sendProfileData(payload) {
    try {
        const response = await fetch(".", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector("[name=csrfmiddlewaretoken]").value,
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
