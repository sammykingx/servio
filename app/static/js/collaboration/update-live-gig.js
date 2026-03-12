async function updateLiveGig() {
    const saveBtn = document.getElementById('saveChanges');
    if (!saveBtn) return;

    const payload = window.projectCollector.getPayload();
    const endpoint = saveBtn.dataset.endpoint || window.location.href;
    const csrfToken = saveBtn.dataset.csrfToken;

    const originalContent = saveBtn.innerHTML;
    saveBtn.disabled = true;
    saveBtn.classList.add('opacity-70', 'cursor-not-allowed');
    saveBtn.innerHTML = `
        <span class="animate-spin material-symbols-outlined text-lg">progress_activity</span>
        Processing...
    `;

    try {
        const response = await sendPayload(payload, endpoint, csrfToken);
        const result = await response.json();

        if (response.ok) {
            const msg = "We've updated your project details. Everything looks good!";
            showToast(
                result.message || msg,
                "success",
                result.title || "All set, Changes Saved"
            );
            setTimeout(() => window.location.reload(), 1500);
        } else {
            // console.log(JSON.stringify(result, null, 2));
            showToast(
                result.message || "Please check your inputs.",
                result.status || "error",
                result.error || "Update Failed"
            );
        }
    } catch (error) {
        console.error("Fetch Error:", error);
        showToast("System Error", "Could not reach the server.", "error");
    } finally {
        saveBtn.disabled = false;
        saveBtn.classList.remove('opacity-70', 'cursor-not-allowed');
        saveBtn.innerHTML = originalContent;
    }
}