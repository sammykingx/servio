document.getElementById('signupForm').addEventListener('submit', async function (event) {
    event.preventDefault();

    const checkbox = document.getElementById("checkboxLabelOne");
    if (!checkbox.checked) {
        showAuthAlert(
            "Terms Agreement Required",
            "Please agree to the Terms and Conditions before continuing.",
            "info"
        );
        return;
    }

    const formData = new FormData(this);
    const isValid = validateFormData(formData);

    if (!isValid) return;

    const { email, first_name, last_name, password1 } = Object.fromEntries(formData.entries());

    formData.set("first_name", validator.escape(first_name));
    formData.set("last_name", validator.escape(last_name));
    formData.set("email", validator.normalizeEmail(email));
    formData.set("password1", validator.escape(password1));

    try {
        const response = await fetch(this.action, {
            method: this.method,
            body: formData,
        });

        console.log("Backend Response: ", response);

        if (response.redirected) {
            showAuthAlert(
                "Signup Successful",
                "Your account has been created. Redirecting...",
                "success"
            );
            setTimeout(() => {
                window.location.href = response.url;
            }, 1500);
            return;
        } else {
            showAuthAlert(
                "Signup Failed",
                "Kindly double-check your details and retry again, cheers.",
                "info"
            );
        }

    } catch (error) {
        showAuthAlert("Network Error", "Something went wrong. Please try again later.", "error");
    }
});


function validateFormData(formData) {
    let { email, first_name, last_name, password1 } = Object.fromEntries(formData.entries());
    first_name = first_name.trim();
    last_name = last_name.trim();
    let valid = true;

    if (
        !validator.isLength(first_name, { min: 3 }) ||
        !validator.isAlpha(first_name, 'en-US', { ignore: "-'" })
    ) {
        showAuthAlert(
            "Name Error - First Name",
            "First name must be at least 3 letters and may include hyphens or apostrophes.",
            "warning"
        );
        valid = false;
        return valid;
    }

    if (
        !validator.isLength(last_name, { min: 3 }) ||
        !validator.isAlpha(last_name, 'en-US', { ignore: "-'" })
    ) {
        showAuthAlert(
            "Name Error - Last Name",
            "Last name must be at least 3 letters and may include hyphens or apostrophes.",
            "warning"
        );
        valid = false;
        return valid;
    }

    if (!validator.isEmail(email)) {
        showAuthAlert(
            "Invalid Email",
            "Please enter a valid email address.",
            "error"
        );
        valid = false;
        return valid;
    }

    if (!validator.isStrongPassword(password1, {
        minLength: 8,
        minLowercase: 1,
        minUppercase: 1,
        minNumbers: 1,
        minSymbols: 1
    })) {
        showAuthAlert(
            "Password not strong enough",
            "Password should be at least 8 characters long including uppercase letters, lowercase, numbers and symbols.",
            "error");
        valid = false;
        return valid;
    }

    return valid;
}

// Response Object
// Response {
//     type: "basic",
//     url: "http://localhost:8000/accounts/email/sent/",
//     redirected: true,
//     status: 200,
//     ok: true,
//     statusText: "OK", 
//     headers: Headers(7), 
//     body: ReadableStream, 
//     bodyUsed: false
// }