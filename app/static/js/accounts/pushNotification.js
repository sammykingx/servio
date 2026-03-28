import { getToken } from "https://www.gstatic.com/firebasejs/12.11.0/firebase-messaging.js";


const pushNotificationToggle = function ({ initialState, endpoint, csrfToken }) {
    return {
        on: initialState,
        loading: false,

        async togglePush() {
            if (this.loading) return;

            this.loading = true;

            if (!this.on) {
                await this.enablePush(endpoint, csrfToken);
            } else {
                await this.disablePush(endpoint, csrfToken);
            }

            this.loading = false;
        },

        async enablePush(endpoint, csrfToken) {
            try {
                const registration = await navigator.serviceWorker.register(
                    "/firebase-messaging-sw.js"
                );
                console.log("fcm-sw successful: ", registration);

                const permission = await Notification.requestPermission();
                console.log('Notification permission result:', permission);

                if (permission !== "granted") {
                    showToast("Notifications stayed off. We'll keep things updated manually for now.", "info", "Preference Saved");
                    return;
                }

                const token = await getToken(window.servioFirebase.messaging, {
                    vapidKey: window.servioFirebase.vapidKey,
                    serviceWorkerRegistration: registration
                });

                if (!token) {
                    showToast(
                        "We couldn't generate a unique sync ID for this browser. Please check your internet connection or reload the page.",
                        "error",
                        "Connection Timeout"
                    );
                    return;
                }

                // const response = await fetch(endpoint, {
                //     method: "POST",
                //     headers: {
                //         "Content-Type": "application/json",
                //         "X-CSRFToken": csrfToken
                //     },
                //     body: JSON.stringify({
                //         channel: "web_push",
                //         value: true,
                //         token: token
                //     })
                // });

                // if (!response.ok) {
                //     throw new Error("Failed to save preference");
                // }

                this.on = true;
                showToast(
                    "You're all set! We'll push live updates to your device even when you're offline.",
                    "success",
                    "Live Sync Active"
                );

                // i need to listen to when Notification permission is revoked
                // and update the preference accordingly, but browsers don't 
                // provide an event for that. So for now, if the user revokes 
                // permission, the preference will be out of sync until they 
                // toggle it again.

            } catch (error) {
                console.error(error);
                showToast(
                    "We couldn't sync with the notification server. Please check your internet and try again.",
                    "warning",
                    "Connection Interrupted",
                );
            }
        },

        async disablePush(endpoint, csrfToken) {
            try {
                await fetch(endpoint, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken
                    },
                    body: JSON.stringify({
                        channel: "web_push",
                        value: false
                    })
                });

                this.on = false;
                showToast("Push notifications disabled", "success");

            } catch (error) {
                console.error(error);
                showToast("Failed to disable push", "error");
            }
        }
    };
};

