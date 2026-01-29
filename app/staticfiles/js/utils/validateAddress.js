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