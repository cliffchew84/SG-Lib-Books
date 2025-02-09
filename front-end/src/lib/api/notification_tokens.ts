import type BackendAPIClient from './client';
import type { NotificationToken } from './models';

export async function registerToken(client: BackendAPIClient, token: string): Promise<NotificationToken> {
	try {
		const response = await client.post({ path: `/notification_tokens/${token}` });

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}, detail: ${await response.text()}`, {
				cause: response.status
			});
		}

		const data: NotificationToken = await response.json();

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

export async function deregisterToken(client: BackendAPIClient, token: string): Promise<undefined> {
	try {
		const response = await client.delete({ path: `/notification_tokens/${token}` });

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}, detail: ${await response.text()}`, {
				cause: response.status
			});
		}

	} catch (error) {
		if (error instanceof Error) {
			console.error('Error querying api:', error.message);
		} else {
			console.error('An unknown error occurred while querying API');
		}
		throw error;
	}
}

