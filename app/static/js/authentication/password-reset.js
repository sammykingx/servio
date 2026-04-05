/**
 * Modern Busy State Handler
 * Blurs the button, reduces opacity, and prevents clicks
 */
function setBusyState(isBusy) {
    const btn = document.getElementById("submitBtn");
    if (!btn) return;

    if (isBusy) {
        btn.disabled = true;
        btn.classList.add("opacity-50", "blur-[1.5px]", "pointer-events-none", "cursor-not-allowed");
        btn.dataset.originalText = btn.textContent;
        btn.textContent = "Updating...";
    } else {
        btn.disabled = false;
        btn.classList.remove("opacity-50", "blur-[1.5px]", "pointer-events-none", "cursor-not-allowed");
        btn.textContent = btn.dataset.originalText || "Update Password";
    }
}

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

        if (!validator.isLength(password2, { min: 8 })) {
            showAuthAlert(
                "Weak Password",
                "Password must be at least 8 characters long.",
                "warning"
            );
            return;
        }

        const formData = new FormData();
        formData.append("password1", validator.escape(password1));
        formData.append("password2", validator.escape(password2));
        formData.append("auto_login", autoLoginValue);

        const csrfToken = document.querySelector("input[name='csrfmiddlewaretoken']").value;

        setBusyState(true);
        try {
            const response = await fetch(form.action, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken
                },
                body: formData
            });
            const data = await response.json();

            if (!response.ok) {
                showAuthAlert(
                    data.error || "Password reset failed",
                    data.message || "we couldn't reset your password at this time, kindly check back later cheers.",
                    data.status || "info"
                );
                return;
            }

            showAuthAlert(
                data.title || "Password reset complete",
                data.message || "Your password has been updated, you're account is waiting for you",
                data.status || "success"
            );


            if (data?.redirect && data?.url) {
                setTimeout(() => {
                    window.location.assign(data.url);
                }, 1700);
            }
            

        } catch (error) {
            showAuthAlert("Network Error", "Something went wrong. Please try again later.", "error");
        } finally {
            setBusyState(false);
        }
    });
});
