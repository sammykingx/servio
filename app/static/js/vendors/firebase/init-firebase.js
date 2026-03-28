// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/12.11.0/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/12.11.0/firebase-analytics.js";
import { getMessaging } from "https://www.gstatic.com/firebasejs/12.11.0/firebase-messaging.js";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional

const configElement = document.getElementById('firebase-config');
const vapidKeyElement = document.getElementById('firebase-vapid-key');

function initializeFirebase() {
    if (!configElement || !vapidKeyElement) {
        showToast("push notification configuration is missing. Please contact support.", "error", "Issue Detected");
        return {};
    }

    const firebaseConfig = JSON.parse(configElement.textContent);
    const vapidKey = JSON.parse(vapidKeyElement.textContent);

    // Initialize Firebase
    const app = initializeApp(firebaseConfig);
    const analytics = getAnalytics(app);
    const messaging = getMessaging(app);

    return { app, analytics, messaging, vapidKey };

}

const { app, analytics, messaging, vapidKey } = initializeFirebase();

window.servioFirebase = {
    firebaseApp: app,
    messaging: messaging,
    vapidKey: vapidKey,
}

// fore ground messages
// messaging.onMessage((payload) => {
//     const title = payload.notification.title || "New Notification";
//     const body = payload.notification.body || "You have a new notification.";

//     showToast(body, "info", title);
// })

// function requestPermission() {
//     console.log('Requesting permission...');
//     Notification.requestPermission().then((permission) => {
//         if (permission === 'granted') {
//             console.log('Notification permission granted.');
//             getToken(messaging, { vapidKey: vapidKey }).then((currentToken) => {
//                 if (currentToken) {
//                     console.log('Token retrieved:', currentToken);
//                     // Send the token to your server and update the UI if necessary
//                 } else {
//                     console.log('No registration token available. Request permission to generate one.');
//                 }
//             }).catch((err) => {
//                 console.log('An error occurred while retrieving token. ', err);
//             });
//         } else {
//             console.log('Unable to get permission to notify.');
//         }
//     });
// }