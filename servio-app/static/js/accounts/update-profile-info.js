document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("updateProfile");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        const saveBtn = document.getElementById("saveBtn");
        const numberFields = ["mobile_num", "alt_mobile_num"];
        const FIELD_LABELS = {
            mobile_num: "Mobile Number",
            alt_mobile_num: "Alternate Mobile Number",
        };

        const mobile = formData.get("mobile_num")?.trim();
        const altMobile = formData.get("alt_mobile_num")?.trim();

        if (!mobile && !altMobile) {
            showToast(
                "Please provide at least one phone number.",
                "warning",
                "No Number Provided",
            );
            return;
        }

        for (let field of numberFields) {
            let value = formData.get(field)?.trim();

            if (value && !isValidNumber(value)) {
                const label = FIELD_LABELS[field] || field;
                showToast(
                    `Your ${label} has an invalid format`,
                    "warning",
                    `Invalid ${label}`,
                );
                return;
            }

            formData.set(field, value || "");
        }

        startLoading(saveBtn);
        try {
            const response = await fetch(form.action, {
                method: "POST",
                body: formData,
            });

            const data = await response.json();
            
            startLoading(saveBtn);

            if (!response.ok) {
                return showToast(
                    data.message || "Something went wrong",
                    "info",
                    "Update Failed",
                );
            }

            updateProfileUI(data.profile);
            showToast(
                data.message || "Updated successfully!",
                "success",
                "Updated Successfully",
            );
            showSuccessState(saveBtn);

        } catch (err) {
            return showToast(
                "Network error. Please try again.",
                "error",
                "Network Error",
            );
        }
    });
   
});

function isValidNumber(number) {
    if (!validator.isMobilePhone(number, "any")) {
        return false;
    }
    return true;
};

function updateProfileUI(profileData) {
    Object.entries(profileData).forEach(([field, value]) => {
        const el = document.querySelector(`[data-profile-field="${field}"]`);
        if (el) {
            const formatted = value ? formatPhone(value) : "N/A";
            el.textContent = formatted;
        }
    });
}

function formatPhone(number) {
    if (!number) return "N/A";

    // Keep only digits
    const digits = number.replace(/\D/g, "");

    if (digits.length === 10) {
        // US / Canada / Local Nigeria (assuming local 10-digit)
        return `(${digits.slice(0,3)}) ${digits.slice(3,6)}-${digits.slice(6)}`;
    }

    if (digits.length === 11 && digits.startsWith("1")) {
        // US / Canada with country code
        return `+1 (${digits.slice(1,4)}) ${digits.slice(4,7)}-${digits.slice(7)}`;
    }

    if (digits.length === 11 && digits.startsWith("7")) {
        // Russia
        return `+7 (${digits.slice(1,4)}) ${digits.slice(4,7)}-${digits.slice(7,9)}-${digits.slice(9)}`;
    }

    if (digits.length === 13 && digits.startsWith("234")) {
        // Nigeria with country code
        return `+234 (${digits.slice(3,6)}) ${digits.slice(6,9)}-${digits.slice(9)}`;
    }

    if (digits.length === 12 && digits.startsWith("44")) {
        // UK
        return `+44 ${digits.slice(2,5)} ${digits.slice(5,8)} ${digits.slice(8)}`;
    }

    if (digits.length >= 11 && digits.startsWith("3")) {
        // General Europe (France, Germany, etc.) fallback
        return `+${digits.slice(0, digits.length - 9)} ${digits.slice(-9,-6)} ${digits.slice(-6,-3)} ${digits.slice(-3)}`;
    }

    // fallback: just show digits
    return "+" + digits;
}
