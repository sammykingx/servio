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
            console.log("RESPONSE:", res);
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

// document.getElementById("passwordChange").addEventListener("submit", async function (event) {
//     event.preventDefault();

//     const formData = new FormData(this);
//     const isValid = validatePasswordFormData(formData);

//     if (!isValid) {
//         showToast(
//             "Kindly double-check your password details and try again.",
//             "info",
//             "Password Change Failed"
//         );
//         return;
//     }

//     // Extract + sanitize
//     const { password1, password2 } = Object.fromEntries(formData.entries());
//     formData.set("password1", validator.escape(password1));
//     formData.set("password2", validator.escape(password2));

//     try {
//         updateButtonState("processing");

//         const response = await fetch(this.action, {
//             method: this.method,
//             body: formData,
//         });

//         console.log("RESPONSE:", response);
//         if (response.ok) {
//             showToast(
//                 "Your password has been updated.",
//                 "success",
//                 "Update Successful",
//             );

//             // Optional: redirect or UI action
//             updateButtonState("success");
//         } else {
//             showToast(
//                 "Your password could not be updated. Try again.",
//                 "info",
//                 "Update Failed",
//             );
//             updateButtonState("failed");
//         }

//     } catch (error) {
//         showToast(
//             "Something went wrong. Please try again later.",
//             "error",
//             "Network Error",
//         );
//         updateButtonState("failed");
//     }
// });



// function validatePasswordFormData(formData) {
//     let { password1, password2 } = Object.fromEntries(formData.entries());

//     password1 = password1.trim();
//     password2 = password2.trim();

//     // Check empty
//     if (validator.isEmpty(password1) || validator.isEmpty(password2)) {
//         showToast("Passwords cannot be empty.", "warning", "Empty Fields");
//         return false;
//     }

//     // Check match
//     if (!validator.equals(password1, password2)) {
//         showToast("Passwords do not match.", "warning", "Password Mismatch");
//         return false;
//     }

//     // Check strength
//     const strongOptions = {
//         minLength: 8,
//         minLowercase: 1,
//         minUppercase: 1,
//         minNumbers: 1,
//         minSymbols: 1
//     };

//     if (!validator.isStrongPassword(password1, strongOptions)) {
//         showToast(
//             "Password must include: uppercase, lowercase, numbers, symbols and be at least 8 characters long.",
//             "error",
//             "Weak Password",
//         );
//         return false;
//     }

//     return true;
// }


// function updateButtonState(stage="processing") {
//     const processingBtn = `
//         <svg class="animate-spin h-5 w-5 text-white"
//              xmlns="http://www.w3.org/2000/svg"
//              fill="none" viewBox="0 0 24 24">
//             <circle class="opacity-25" cx="12" cy="12" r="10"
//                 stroke="currentColor" stroke-width="4"></circle>
//             <path class="opacity-75" fill="currentColor"
//                 d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z">
//             </path>
//         </svg>
//         Processing...
//     `;

//     const successBtn = `
//             <svg class="h-5 w-5 text-white"
//                  fill="none" stroke="currentColor" stroke-width="2"
//                  viewBox="0 0 24 24">
//                 <path stroke-linecap="round" stroke-linejoin="round"
//                       d="M5 13l4 4L19 7"/>
//             </svg>
//             Update Successful
//         `;
    
//     const failedBtn = `
//             <svg class="h-5 w-5 text-white"
//                  fill="none" stroke="currentColor" stroke-width="2"
//                  viewBox="0 0 24 24">
//                 <path stroke-linecap="round" stroke-linejoin="round"
//                       d="M6 18L18 6M6 6l12 12"/>
//             </svg>
//             Update Failed, Retry
//         `;
//     const btn = document.getElementById("submit");

//     btn.disabled = true;

//     if (stage === "processing") {
//         btn.innerHTML = processingBtn;
//     } else if (stage === "success") {
//         btn.innerHTML = successBtn;
//     } else {
//         btn.disabled = false;
//         btn.innerHTML = failedBtn;
//     }

//     // btn.innerHTML = `
//     //     <svg class="animate-spin h-5 w-5 text-white"
//     //          xmlns="http://www.w3.org/2000/svg"
//     //          fill="none" viewBox="0 0 24 24">
//     //         <circle class="opacity-25" cx="12" cy="12" r="10"
//     //             stroke="currentColor" stroke-width="4"></circle>
//     //         <path class="opacity-75" fill="currentColor"
//     //             d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z">
//     //         </path>
//     //     </svg>
//     //     Processing...
//     // `;
// }
