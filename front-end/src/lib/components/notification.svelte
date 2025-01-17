<script lang="ts">
	import { getToken, onMessage } from 'firebase/messaging';
	import { toast } from 'svelte-sonner';

	import { PUBLIC_FIREBASE_VAPIDKEY } from '$env/static/public';
	import { messaging } from '$lib/firebase';
	import { goto } from '$app/navigation';

	// Get registration token. Initially this makes a network call, once retrieved
	// subsequent calls to getToken will return from cache
	Notification.requestPermission().then((permission) => {
		if (permission === 'granted') {
			getToken(messaging, {
				vapidKey: PUBLIC_FIREBASE_VAPIDKEY
			})
				.then((currentToken) => {
					if (currentToken) {
						// TODO: Add token to database
						console.log(currentToken);
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
		// TODO: add notification to svelte store
	});
</script>
