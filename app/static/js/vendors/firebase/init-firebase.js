const firebaseConfig = {
    apiKey: "xxx",
    authDomain: "xxx",
    projectId: "xxx",
    messagingSenderId: "xxx",
    appId: "xxx"
};

firebase.initializeApp(firebaseConfig);
const messaging = firebase.messaging();