function businessState() {
    return {
        endpoint: '',
        businessData: {
            name: '',
            tagline: '',
            email: '',
            phone: '',
            industry: '',
            niche: '',
            bio: '',

            socials: {
            facebook: '',
            instagram: '',
            twitter: '',
            linkedin: '',
            },

            address: {
                street: '',
                streetTwo: '',
                city: '',
                state: '',
                postalCode: '',
                country: '',
            }
        }
    }
};

// function industrySelector(businessData) {
//     return {
//         industries: [],
//         subCategories: [],

//         init() {
//             this.industries = window.INDUSTRIES_DATA || [];

//             if (businessData.industry) {
//                 this.updateSubCategories();
//             }

//             this.$watch('businessData.industry', () => {
//                 this.updateSubCategories();
//             });
//         },

//         updateSubCategories() {
//             const selected = this.industries.find(
//                 i => i.name === businessData.industry
//             );
//             this.subCategories = selected ? selected.subcategories : [];
//         }
//     };
// }


function industrySelector(businessData) {
    return {
        industries: JSON.parse(
            document.getElementById('industries-data').textContent
        ),

        get subCategories() {
            const i = this.industries.find(
            i => i.name === businessData.industry
            )
            return i ? i.sub_categories : []
        },

        init() {
            this.$watch(
            () => businessData.industry,
            () => (businessData.niche = '')
            )
        }
    }
};

async function saveBusiness(businessState) {
    if (!validateFormData(businessState.businessData)) return;

    const csrfToken = document.querySelector(
        '[name=csrfmiddlewaretoken]'
    ).value;
    
    const response = await fetch(businessState.endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify(businessState.businessData),
    });

    if (!response.ok) {
        showToast(
            "Unable to register business account at this time, check back later",
            "error",
            "Failed Registration"
        );
        return
    }
    data = await response.json();
    if (data.error) {
        showToast(data.error, "error", "Registration Error");
        return
    }

    showToast(data.message, "success", "Created Business Account");
};

function validateFormData(businessData) {
    const requiredFields = [
        businessData.name,
        businessData.email,
        businessData.phone,
        businessData.bio,

        businessData.address.street,
        businessData.address.city,
        businessData.address.state,
        businessData.address.postalCode,
        businessData.address.country,
    ];

    // Required fields
    const allPresent = requiredFields.every(
        v => typeof v === 'string' && v.trim().length > 0
    );

    if (!allPresent) {
        showToast(
            "Missing required fields, check and try again",
            "info",
            "Missing Fields"
        );
        return false;
    }

    // STREET: minimum length
    if (!validator.isLength(businessData.address.street, { min: 3 })) {
        showToast(
            "Street address must be at least 3 characters long.",
            "warning",
            "Validation Error"
        );
        return false;
    };

    if (businessData.address.streetTwo && !validator.isLength(businessData.address.streetTwo, { min: 3 })) {
        showToast(
            "Street Line 2 must be at least 3 characters long if provided.",
            "warning",
            "Validation Error"
        );
        return false;
    };

    const countryObj = COUNTRIES.find(c => c.name === businessData.address.country);
    const countryCode = countryObj ? countryObj.code : "any";

    // City, Province, Country: only letters & spaces
    const alphaFields = {
        city: businessData.address.city,
        state: businessData.address.state,
        country: businessData.address.country,
    };

    for (const [fieldName, value] of Object.entries(alphaFields)) {
        if (!validator.matches(value, /^[a-zA-Z\s()*]+$/)) {
            showToast(
                `${capitalize(fieldName)} must contain only letters and spaces.`,
                "warning",
                "Validation Error"
            );
            return false;
        }
    };

    // Postal code
    try {
        if (!validator.isPostalCode(businessData.address.postalCode, countryCode)) {
            showToast(
                "Postal code does not match the selected country format.",
                "warning",
                "Validation Error"
            );
            return false;
        }
    } catch (err) {
        showToast(
            `Invalid postal/zip code for selected country region (${businessData.address.country}, ${countryCode})`,
            "error",
            "Postal/Zip code Error"
        );
        return false;
    }

    return true;
}