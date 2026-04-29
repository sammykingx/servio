/**
 * Servio Proposal Action Handler
 * Handles Acceptance/Rejection with visual feedback
 */
const ProposalManager = (() => {

    const selectors = ['[data-proposal-actions]', '[data-action]'];
    const attrs = ['endpoint', 'proposalId', 'roleId'];

    const checkStructure = () => {
        const container = document.querySelector(selectors[0]);
        const hasButtons = !!document.querySelector(selectors[1]);
        const hasData = container && attrs.every(a => container.dataset[a]);
        console.log(container, hasButtons, hasData);
        if (!container || !hasButtons || !hasData) {
            setTimeout(() => {
                showToast(
                    "Proposal settings failed to load. Refresh to try again or contact support.",
                    "warning",
                    "Configuration Error"
                );
            }, 1200);
            return false;
        }
        return true;
    };

    /**
     * Finds ALL action containers on the page and toggles their state
     */
    const toggleBusyState = (isBusy) => {
        const allContainers = document.querySelectorAll(selectors[0]);

        allContainers.forEach(container => {
            const buttons = container.querySelectorAll('button');

            if (isBusy) {
                container.classList.add('pointer-events-none', 'select-none');
                buttons.forEach(btn => {
                    btn.disabled = true;
                    btn.classList.add('opacity-50', 'blur-[1px]', 'cursor-not-allowed');
                });
            } else {
                container.classList.remove('pointer-events-none', 'select-none');
                buttons.forEach(btn => {
                    btn.disabled = false;
                    btn.classList.remove('opacity-50', 'blur-[1px]', 'cursor-not-allowed');
                });
            }
        });
    };

    const handleAction = async (event) => {
        const btn = event.target.closest('[data-action]');
        if (!btn) return;

        const container = btn.closest('[data-proposal-actions]');
        const { endpoint, proposalId, roleId, csrfToken } = container.dataset;
        const action = btn.dataset.action;

        toggleBusyState(true);

        try {
            const response = await fetch(endpoint, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({
                    proposal_id: proposalId,
                    role_id: roleId,
                    state: action
                })
            });

            const data = await response.json();

            if (!response.ok) {
                showToast(
                    data.message || "We couldn't update the proposal state.",
                    data.status || "error",
                    data.title || "Update didn't go through"
                );

                if (data.redirect && data.url) {
                    setTimeout(() => {
                        window.location.assign(data.url)
                    }, 2200);
                }
                return;
                
            }

            showToast(
                data.message || "We’ve updated the proposal state for you",
                data.status || "success",
                data.title || "Proposal Updated"
            );

            if (data.redirect && data.url && action==='accepted') {
                setTimeout(() => {
                    window.location.assign(data.url)
                }, 2200);
            } else {
                setTimeout(() => {
                    window.location.reload()
                }, 2200);
            }

        } catch (error) {
            showToast(
                "We couldn't reach the server. Please check your internet connection and try again.",
                "error",
                "Client Side Error",
            );
        } finally {
            toggleBusyState(false);
        }
    };

    const init = () => {
        if (!checkStructure()) return;
        document.addEventListener('click', handleAction);
    };

    return { init };
})();

