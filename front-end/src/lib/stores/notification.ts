import { toast } from 'svelte-sonner';
import { writable } from 'svelte/store';

import { goto } from '$app/navigation';
import type { Notification } from '$lib/models';
import type BackendAPIClient from '$lib/api/client';
import { getNotifications, readNotification } from '$lib/api/notification';

export const notificationToken = writable<string | null>(null);
export const refreshNotification = writable<boolean>(true);
export const notificationStore = writable<Notification[]>([]);

export async function fetchNotifications(client: BackendAPIClient) {
	try {
		const notifications = await getNotifications(client);
		notificationStore.set(
			notifications.map((notif) => ({
				...notif,
				onClick: async () => {
					try {
						await readNotification(client, notif.id);
						notificationStore.update((s) => {
							const index = s.findIndex(n => n.id === notif.id);
							if (index !== -1) {
								s[index].isRead = true;
							}
							return s;
						});
						goto(notif.action);
					} catch (error) {
						toast.warning('Failed to mark notification as read');
						console.error('Failed to mark notification as read', error);
					}
				}
			}))
		);
	} catch (error) {
		console.error('Failed to fetch notifications', error);
		throw error;
	}
}
