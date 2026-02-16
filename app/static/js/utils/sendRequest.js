/**
 * Sends a POST request with a JSON payload and CSRF protection.
 * * Note: This function only throws/catches on network-level failures. 
 * HTTP error statuses (e.g., 400, 500) are returned as resolved responses 
 * and must be handled by the caller.
 *
 * @param {Object} payload - The data to be stringified and sent in the request body.
 * @param {string} endpoint - The destination URL.
 * @param {string} csrfToken - The Django/Server-side CSRF token for the 'X-CSRFToken' header.
 * @returns {Promise<Response>} The Fetch API Response object.
 * @throws {Error} If the network is unreachable or the fetch request is aborted.
 */
async function sendPayload(payload, endpoint, csrfToken) {
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify(payload),
        });

        return response;
    } catch (err) {
        showToast(
            "We couldn't reach the server. Please check your internet connection and try again.",
            "error",
            "Client Side Error"
        );
        throw err;
    }
}
