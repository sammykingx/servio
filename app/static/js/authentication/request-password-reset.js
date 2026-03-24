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

        const data = await response.json();
        if (!response.ok) {
            showAuthAlert(
                data.error || "Email Failed",
                data.message || "Unable to send reset link.",
                data.status || "error"
            );

        } else {
            showAuthAlert(
                data.title || "Reset Link Sent",
                data.message || "We've emailed your reset link.",
                data.status || "success"
            );
        }
        
    } catch (error) {
        showAuthAlert("Network Error", "Something went wrong. Please try again later.", "error");
    } finally {
        toggleBtnState();
        requestCleanup();
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

}