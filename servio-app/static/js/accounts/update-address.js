let COUNTRIES = [];

document.addEventListener("DOMContentLoaded", async () => {
	const selections = document.querySelectorAll(".countrySelect");
	const countries = await fetch("/static/js/country-list.json").then(res => res.json());

    COUNTRIES = countries;

	if (!selections.length) return;
	
	selections.forEach(selection => {
		countries.forEach(country => {
			const option = document.createElement("option");
			option.value = country.name;
			option.textContent = country.name;
			option.className = "text-gray-700 dark:bg-gray-900 dark:text-gray-400";
		
		    selection.appendChild(option);
	    });
	})	
});

document.addEventListener("DOMContentLoaded", () => {
    const forms = document.querySelectorAll(".updateAddressForm");

    forms.forEach((form) => {
        const submitBtn = form.querySelector("button[type='submit']");

        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            const formData = new FormData(form);
            const isValid = validateFormData(formData);
            

            if (!isValid) return;

            startLoading(submitBtn);

            try {
                const response = await fetch(form.action, {
                    method: "POST",
                    body: formData,
                });

                const data = await response.json();

                if (!response.ok) {
                    stopLoading(submitBtn);
                    return showToast(
                        data.message || "Something went wrong",
                        "info",
                        "Update Failed"
                    );
                }

                updateAddressUI(data.address);
                showToast(
                    data.message || "Updated successfully!",
                    "success",
                    "Updated Successfully"
                );
                showSuccessState(submitBtn);

            } catch (err) {
                stopLoading(submitBtn);
                return showToast(
                    "Network error. Please try again.",
                    "error",
                    "Network Error"
                );
            }
        });
    });
});

// Spinner & button functions
const SPINNER = `
<svg class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
  <path class="opacity-75" fill="currentColor"
        d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 100 16v-4l-3 3 3 3v-4a8 8 0 01-8-8z">
  </path>
</svg>
`;

function validateFormData(formData) {
    const street = formData.get("street")?.trim();
    const street_line_2 = formData.get("street_line_2")?.trim();
    const city = formData.get("city")?.trim();
    const province = formData.get("province")?.trim();
    const postal_code = formData.get("postal_code")?.trim();
    const country = formData.get("country")?.trim();
    const countryObj = COUNTRIES.find(c => c.name === country);
    const countryCode = countryObj ? countryObj.code : "any";

    // Required fields
    const requiredFields = { street, city, province, postal_code, country };
    for (const [fieldName, value] of Object.entries(requiredFields)) {
        if (!value) {
            showToast(
                `${capitalize(fieldName.replace("_", " "))} is required.`,
                "warning",
                "Validation Error"
            );
            return false;
        }
    }

    // STREET: minimum length
    if (!validator.isLength(street, { min: 3 })) {
        showToast(
            "Street address must be at least 3 characters long.",
            "warning",
            "Validation Error"
        );
        return false;
    }

    if (street_line_2 && !validator.isLength(street_line_2, { min: 3 })) {
        showToast(
            "Street Line 2 must be at least 3 characters long if provided.",
            "warning",
            "Validation Error"
        );
        return false;
    }

    // City, Province, Country: only letters & spaces
    const alphaFields = { city, province, country };
    for (const [fieldName, value] of Object.entries(alphaFields)) {
        if (!validator.matches(value, /^[a-zA-Z\s()*]+$/)) {
            showToast(
                `${capitalize(fieldName)} must contain only letters and spaces.`,
                "warning",
                "Validation Error"
            );
            return false;
        }
    }

    // Postal code
    try {
        if (!validator.isPostalCode(postal_code, countryCode)) {
            showToast(
                "Postal code does not match the selected country format.",
                "warning",
                "Validation Error"
            );
            return false;
        }
    } catch (err) {
        showToast(
            `Invalid postal/zip code for selected country region (${country}, ${countryCode})`,
            "error",
            "Postal/Zip code Error"
        );
        return false;
    }

    return true;
}

/**
 * Converts a string to title case like Python's str.title()
 * @param {string} str
 * @returns {string}
 */
function updateAddressUI(addressData) {
    const label = addressData.label;
    Object.entries(addressData).forEach(([field, value]) => {
        const el = document.querySelector(
            `[data-address="${label}"][data-field="${field}"]`
        );

        if (!el) return;

        if (field === "postal_code") {
            el.textContent = value ? value.toUpperCase() : "N/A";
            return;
        }

        el.textContent = value ? title(value) : "N/A";
    });
}

function title(str) {
    return str
        .toLowerCase()
        .replace(/\b\w/g, char => char.toUpperCase());
}


function capitalize(str) {
    return str.replace(/\b\w/g, (c) => c.toUpperCase());
}

function startLoading(button) {
    button.disabled = true;
    button.dataset.originalText = button.innerHTML;
    button.innerHTML = `<span class="flex items-center gap-2">${SPINNER} Updating...</span>`;
}

function stopLoading(button) {
    button.disabled = false;
    button.innerHTML = button.dataset.originalText;
}

function showSuccessState(button) {
    button.innerHTML = `
        <span class="flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-white" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 00-1.414 0L8 12.586 4.707 9.293A1 1 
                0 003.293 10.707l4 4a1 1 0 001.414 0l8-8a1 1 0 000-1.414z" clip-rule="evenodd" />
            </svg>
            Updated!
        </span>
    `;
}

