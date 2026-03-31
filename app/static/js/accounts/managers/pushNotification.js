import { getToken } from "https://www.gstatic.com/firebasejs/12.11.0/firebase-messaging.js";

class WebPushManager {
    /**
     * * Retrieves the FCM token for the current user/device.
     * @returns {Promise<string>} The FCM token.
     */
    static async getUserPermissionAndToken() {
        const registration = await navigator.serviceWorker.register(
            "/firebase-messaging-sw.js"
        );

        const token = await getToken(window.servioFirebase.messaging, {
            vapidKey: window.servioFirebase.vapidKey,
            serviceWorkerRegistration: registration
        });
        return token;
    }

    /**
     * Handles browser permissions and Firebase token generation.
     * @returns {Promise<{token: string}>}
     */
    static async enable() {
        if (Notification.permission === "denied") {
            throw new Error("PERMISSION_BLOCKED_BY_BROWSER");
        }

        const permission = await Notification.requestPermission();

        if (permission !== "granted") {
            throw new Error("PERMISSION_DENIED");
        }
        // const token = "ram janane"
        const token = await this.getUserPermissionAndToken();

        if (!token) {
            throw new Error("TOKEN_GENERATION_FAILED");
        }

        return { token };
    }

    /**
     * Handles any cleanup needed when disabling push.
     * @returns {Promise<{token: null}>}
     */
    static async disable() {
        // unregister the SW or set the token to in_active from the backend.
        const token = await this.getUserPermissionAndToken();
        return { token };
    }
    
    static async syncToken() {
        try {
            const token = await this.getUserPermissionAndToken();

            if (token) {
                await fetch("/notifications/fcm/sync-token/", {
                    method: "POST",
                    body: JSON.stringify({ token: token })
                });
            }
        } catch (err) {
            console.error("Token sync failed", err);
        }
    }
}

export default WebPushManager;
