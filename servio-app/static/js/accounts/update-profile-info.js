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
