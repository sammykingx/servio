document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("passwordChange");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const data = Object.fromEntries(new FormData(form).entries());
        const error = validatePasswords(data);
        if (error) return showToast(error, "error", "Password Error");

        Object.keys(data).forEach(k => data[k] = validator.escape(data[k]));

        updateButton("processing");

        try {
            const res = await fetch(form.action, { method: form.method, body: new FormData(form) });
            if (res.ok) {
                showToast("Your password has been updated.", "success", "Update Successful");
                updateButton("success");
            } else {
                showToast("Password could not be updated. Try again.", "info", "Update Failed");
                updateButton("failed");
            }
        } catch {
            showToast("Something went wrong. Please try again later.", "error", "Network Error");
            updateButton("failed");
        }
    });


});

function validatePasswords({ password1, password2 }) {
    if (!password1 || !password2) return "Passwords cannot be empty.";
    if (password1 !== password2) return "Passwords do not match.";
    const strongOptions = { minLength: 8, minLowercase:1, minUppercase:1, minNumbers:1, minSymbols:1 };
    if (!validator.isStrongPassword(password1, strongOptions)) 
        return "Password must include uppercase, lowercase, numbers, symbols, min 8 chars.";
    return null;
};

function updateButton(stage) {
    const submitBtn = document.getElementById("submitBtn");
    submitBtn.innerHTML = btnStates[stage];
    submitBtn.disabled = stage === "processing" || stage === "success";
}

const btnStates = {
    processing: `
        <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
        </svg>
        Processing...
    `,
    success: `
        <svg class="h-5 w-5 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
        </svg>
        Update Successful
    `,
    failed: `
        <svg class="h-5 w-5 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
        </svg>
        Update Failed, Retry
    `
};
