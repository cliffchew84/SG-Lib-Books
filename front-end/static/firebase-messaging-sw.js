// Give the service worker access to Firebase Messaging.
// Note that you can only use Firebase Messaging here. Other Firebase libraries
// are not available in the service worker.
// Replace 10.13.2 with latest version of the Firebase JS SDK.
importScripts('https://www.gstatic.com/firebasejs/10.13.2/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.13.2/firebase-messaging-compat.js');

// Initialize the Firebase app in the service worker by passing in
// your app's Firebase config object.
// https://firebase.google.com/docs/web/setup#config-object
firebase.initializeApp({
	messagingSenderId: "955327746756",
});

// Retrieve an instance of Firebase Messaging so that it can handle background
// messages.
const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
	console.log(
		'[firebase-messaging-sw.js] Received background message ',
		payload
	);
	const notificationTitle = payload.notification.title;  // Or `payload.notification` depending on what the payload is
	var notificationOptions = {
		body: payload.notification.body,
		icon: payload.data.icon,
		data: { url: payload.data.click_action },  // The URL which we are going to use later
		actions: [{ action: "open_url", title: "Check Out" }],
	};

	return self.registration.showNotification(
		notificationTitle,
		notificationOptions,
	);
});
