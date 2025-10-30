
function toggleContentModal(modalType=null) {
    const contentModal = document.getElementById("contentModal");
    const loadingSpinner = document.getElementById("loading-spinner");

    contentModal.classList.toggle("hidden");
    loadingSpinner.classList.toggle("hidden");
}

async function verifyEmail() {
    const csrfToken = document.head.querySelector('meta[name="csrf-token"]')?.content || "";
    const url = window.location.href;

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: null,
        });

        console.log(response);
        if (response.ok) {
            console.log("Email successfully verified! Redirecting...", "success", "Account Activated");
            toggleContentModal();
        } else {
            console.log("Email verification failed. Please try again.", "error", "Verification Failed");
            toggleContentModal();
            return;
        }

    } catch (error) {
        // showToast("Something went wrong. Please try again later.", "error", "Network Error");
        alert("Network error occurred. Please try again later.");
    }

    // 

    // .then(response => response.json())
    // .then(data => {
    //     console.log("Email Verification Response:", data);
    //     const loadingSpinner = document.getElementById("loading-spinner");
    //     const contentModal = document.getElementById("contentModal");

    //     loadingSpinner.classList.add("hidden");
    //     contentModal.classList.remove("hidden");

}

document.addEventListener("DOMContentLoaded", () => {
    verifyEmail();
});
