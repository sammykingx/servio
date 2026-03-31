importScripts('https://www.gstatic.com/firebasejs/12.11.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/12.11.0/firebase-messaging-compat.js');

firebase.initializeApp({
    apiKey: "{{ FIREBASE_API_KEY }}",
    authDomain: "{{ FIREBASE_AUTH_DOMAIN }}",
    projectId: "{{ FIREBASE_PROJECT_ID }}",
    storageBucket: "{{ FIREBASE_STORAGE_BUCKET }}",
    messagingSenderId: "{{ FIREBASE_MESSAGING_SENDER_ID }}",
    appId: "{{ FIREBASE_APP_ID }}",
    measurementId: "{{ FIREBASE_MEASUREMENT_ID }}"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
    self.registration.showNotification(
        payload.notification.title || "Servio Notification", {
        body: payload.notification.body,
        icon: "/static/images/logo.png",
        // badge: "/static/images/logo.png",
            data: {
                url: payload.data?.url || "/"
            }
    });
});

self.addEventListener("notificationclick", function (event) {
    event.notification.close();

    const url = event.notification.data?.url || "/";

    event.waitUntil(
        clients.matchAll({ type: "window", includeUncontrolled: true })
            .then((clientList) => {

                // check if already open
                for (const client of clientList) {
                    if (client.url.includes(url) && "focus" in client) {
                        return client.focus();
                    }
                }

                // open new tab if not open
                if (clients.openWindow) {
                    return clients.openWindow(url);
                }
            })
    );
});

