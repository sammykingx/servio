document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("socialLinks");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        const saveBtn = document.getElementById("saveChangesBtn");

        const urlFields = ["facebook", "twitter", "linkedin", "instagram"];

        for (let field of urlFields) {
            let value = formData.get(field)?.trim();

            if (value && !isValidURL(value)) {
                showToast(
                    `${field.toUpperCase()} URL is invalid`,
                    "warning",
                    "Invalid URL",
                );
                return;
            }

            formData.set(field, value || "");
        }

        startLoading(saveBtn);
        try {
            const response = await fetch(form.action, {
                method: "POST",
                body: formData,
            });

            const data = await response.json();
            
            startLoading(saveBtn);

            if (!response.ok) {
                return showToast(
                    data.message || "Something went wrong",
                    "info",
                    "Update Failed",
                );
            }

            showToast(
                data.message || "Updated successfully!",
                "success",
                "Updated Successfully",
            );
            showSuccessState(saveBtn);

        } catch (err) {
            return showToast(
                "Network error. Please try again.",
                "error",
                "Network Error",
            );
        }
    });
   
});

function isValidURL(url) {
    if (!validator.isURL(url)) {
        return false;
    }
    return true;
};

const SPINNER = `
<svg class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
  <path class="opacity-75" fill="currentColor"
        d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 100 16v-4l-3 3 3 3v-4a8 8 0 01-8-8z">
  </path>
</svg>
`;

function startLoading(button) {
    button.disabled = true;
    button.innerHTML = `
        <span class="flex items-center gap-2">
            ${SPINNER}
            Processing...
        </span>
    `;
    button.dataset.originalText = button.innerHTML;
}

function stopLoading(button) {
    button.disabled = false;
    button.innerHTML = button.dataset.originalText;
}

function showSuccessState(button) {
    button.innerHTML = `
        <span class="flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-white" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 00-1.414 0L8 12.586 4.707 9.293A1 1 
                0 003.293 10.707l4 4a1 1 0 001.414 0l8-8a1 1 0 000-1.414z" clip-rule="evenodd" />
            </svg>
            Successful!
        </span>
    `;
}
