import type BackendAPIClient from './client';
import type { Notification } from './models';

export async function getNotifications(client: BackendAPIClient): Promise<Notification[]> {
	try {
		const response = await client.get({ path: '/notifications' });

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}, detail: ${await response.text()}`, {
				cause: response.status
			});
		}

		const data: Notification[] = await response.json();

		return data;
	} catch (error) {
		if (error instanceof Error) {
			console.error('Error querying api:', error.message);
		} else {
			console.error('An unknown error occurred while querying API');
		}
		throw error;
	}
}

export async function readNotification(client: BackendAPIClient, id: number): Promise<Notification> {
	try {
		const response = await client.post({ path: `/notifications/${id}/read` });

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}, detail: ${await response.text()}`, {
				cause: response.status
			});
		}

		const data: Notification = await response.json();

		return data;
	} catch (error) {
		if (error instanceof Error) {
			console.error('Error querying api:', error.message);
		} else {
			console.error('An unknown error occurred while querying API');
		}
		throw error;
	}
}

