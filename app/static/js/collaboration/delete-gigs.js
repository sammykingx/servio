/**
 * Handles the soft-delete/archive via AJAX
 * @param {HTMLElement} btn - The button element clicked
 */
async function archiveProject(btn) {
    const card = btn.closest('article');
    const url = btn.getAttribute('data-url');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
        getCookie('csrftoken');

    if (!confirm('Are you sure you want to delete the service request?')) return;

    card.classList.add('opacity-50', 'blur-[2px]', 'pointer-events-none', 'cursor-not-allowed');

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 'action': 'archive' })
        });

        if (response.ok) {
            card.style.transform = 'scale(0.95)';
            card.style.opacity = '0';
            card.style.transition = 'all 0.4s ease';

            setTimeout(() => {
                card.remove();
                showToast('Your project was deleted successfully.', 'success', 'Project deleted');
            }, 400);
        } else {
            const data = await response.json();
            const errorMessage = data.message || 'Failed to delete the project. Please try again.';
            card.classList.remove('opacity-50', 'blur-[2px]', 'pointer-events-none', 'cursor-not-allowed');
            showToast(errorMessage, data.status || 'warning', data.error || 'Project Deletion Failed');
        }
    } catch (error) {
        card.classList.remove('opacity-50', 'blur-[2px]', 'pointer-events-none', 'cursor-not-allowed');
        showToast('Failed to delete the project. Please try again.', 'error', 'Project Deletion Error');
    }
}

// Helper to get CSRF from cookies if the hidden input isn't found
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}