import { getToken, onMessage } from 'firebase/messaging';
import { toast } from 'svelte-sonner';

import { PUBLIC_FIREBASE_VAPIDKEY } from '$env/static/public';
import { messaging } from '$lib/firebase';
import { goto } from '$app/navigation';
import { refreshNotification } from '$lib/stores/notification';

// Get registration token. Initially this makes a network call, once retrieved
// subsequent calls to getToken will return from cache
export default async function requestToken() {
	return Notification.requestPermission().then((permission) => {
		if (permission === 'granted') {
			return getToken(messaging, {
				vapidKey: PUBLIC_FIREBASE_VAPIDKEY
			})
				.then((currentToken) => {
					if (currentToken) {
						return currentToken;
					} else {
						// Show permission request UI
						console.log('No registration token available. Request permission to generate one.');
					}
				})
				.catch((err) => {
					console.log('An error occurred while retrieving token. ', err);
				});
		}
	});
}

// Show notification as toast and update UI store
onMessage(messaging, ({ notification, data }) => {
	if (notification === undefined || notification.title === undefined) {
		return;
	}
	// Show notification as toast
	toast.info(notification.title, {
		description: notification?.body,
		action: data?.click_action
			? {
				label: 'Visit',
				onClick: () => goto(data?.click_action)
			}
			: undefined
	});
	console.log('Message received. ', notification, data);
	// Update notification on next refresh
	refreshNotification.set(true);
});
