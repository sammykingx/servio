document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("requestPasswordReset");
    if (!form) return;

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const password1 = document.querySelector("input[name='new_password1']").value.trim();
        const password2 = document.querySelector("input[name='new_password2']").value.trim();
        const autoLogin = document.querySelector("input[name='auto_login']");
        const autoLoginValue = autoLogin ? autoLogin.checked : false;

        if (validator.isEmpty(password1) || validator.isEmpty(password2)) {
            showAuthAlert(
                "Missing Fields",
                "Both password fields are required.",
                "info"
            );
            return;
        }

        if (!validator.equals(password1, password2)) {
            showAuthAlert(
                "Field Mismatch",
                "Both password field values doesn't match",
                "error"
            );
            return;
        }

        if (!validator.isLength(password1, { min: 8 })) {
            showAuthAlert(
                "Weak Password",
                "Password must be at least 8 characters long.",
                "warning"
            );
            return;
        }

        const formData = new FormData();
        formData.append("password1", validator.escape(password1));
        formData.append("auto_login", autoLoginValue);

        const csrfToken = document.querySelector("input[name='csrfmiddlewaretoken']").value;
        const submitBtn = document.getElementById("submitBtn");

        toggleBtnState();

        try {
            const response = await fetch(form.action, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken
                },
                body: formData
            });

            toggleBtnState()

            if (!response.ok) {
                showAuthAlert(
                    "Password reset failed",
                    "we couldn't reset your password at this time, kindly check back later cheers.",
                    "info"
                );
            }
            
            showAuthAlert(
                "Password reset complete",
                "Your password has been updated, you're account is waiting for you",
                "success"
            );

            submitBtn.textContent = "Reset Completed";
            submitBtn.disabled = true;

            const processingText = document.getElementById("processingText");
            processingText.textContent = "redirecting";

            toggleBtnState();

            setTimeout(() => {
                toggleBtnState();
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    const loginUrl = document.getElementById("login-url").dataset.loginUrl;
                    window.location.href = loginUrl;
                }
            }, 3000);
            

        } catch (error) {
            showAuthAlert("Network Error", "Something went wrong. Please try again later.", "error");
        }
    });
});

function toggleBtnState() {
    const submitBtn = document.getElementById("submitBtn");
    const processingBtn = document.getElementById("processingBtn");

    submitBtn.classList.toggle("hidden");
    processingBtn.classList.toggle("hidden");

}