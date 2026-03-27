importScripts('https://www.gstatic.com/firebasejs/12.11.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/12.11.0/firebase-analytics-compat.js');
importScripts('https://www.gstatic.com/firebasejs/12.11.0/firebase-messaging-compat.js');

firebase.initializeApp({
    apiKey: "xxx",
    projectId: "xxx",
    messagingSenderId: "xxx",
    appId: "xxx"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage(function (payload) {
    self.registration.showNotification(payload.notification.title, {
        body: payload.notification.body,
        icon: "/static/images/logo.png"
    });
});

