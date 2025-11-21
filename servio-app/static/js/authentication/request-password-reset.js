document.getElementById('requestPasswordReset').addEventListener('submit', async function (event) {
    event.preventDefault();

    const formData = new FormData(this);
    const isValid = validateFormData(formData);

    if (!isValid) return;

    const { email } = Object.fromEntries(formData.entries());

    formData.set("email", validator.normalizeEmail(email));

    try {
        toggleBtnState();
        const response = await fetch(this.action, {
            method: this.method,
            body: formData,
        });

        toggleBtnState();

        if (!response.ok) {
            showAuthAlert(
                "Email Failed",
                "Unable to send reset link.",
                "error");
            return;
        }
        showAuthAlert(
            "Reset Link Sent",
            "We've emailed your reset link.",
            "success"
        );
        requestCleanup();
        
    } catch (error) {
        showAuthAlert("Network Error", "Something went wrong. Please try again later.", "error");
    }
});


function validateFormData(formData) {
    let { email } = Object.fromEntries(formData.entries());
    let valid = true;
    

    if (!validator.isEmail(email)) {
        showAuthAlert(
            "Invalid Email",
            "Please enter a valid email address.",
            "error"
        );
        valid = false;
        return valid;
    }

    return valid;
}


function toggleBtnState() {
    const sendBtn = document.getElementById("sendBtn");
    const processingBtn = document.getElementById("processingBtn");

    sendBtn.classList.toggle("hidden");
    processingBtn.classList.toggle("hidden");

}

function requestCleanup() {
    const sendBtn = document.getElementById("sendBtn");
    sendBtn.textContent = "Action Successful";
    sendBtn.disabled = true;

    const logintext = document.getElementById("loginText");
    logintext.classList.toggle("hidden");

}