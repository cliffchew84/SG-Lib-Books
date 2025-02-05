import type BackendAPIClient from './client';
import type { BookSubscriptionCreate, BookSubscription } from './models';

export async function getBookSubscription(client: BackendAPIClient, brn: number): Promise<BookSubscription[]> {
	try {
		const response = await client.get({ path: `/subscription/${brn}` });

		if (!response.ok) {
			if (response.status === 404) {
				return [];
			}
			throw new Error(`HTTP error! status: ${response.status}, detail: ${await response.text()}`, {
				cause: response.status
			});
		}

		const data: BookSubscription[] = await response.json();

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


export async function createSubscriptions(client: BackendAPIClient, subscriptions: BookSubscriptionCreate[]): Promise<BookSubscription[]> {
	try {
		const response = await client.post({ path: `/subscription`, body: subscriptions });

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}, detail: ${await response.text()}`, {
				cause: response.status
			});
		}

		const data: BookSubscription[] = await response.json();

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

export async function updateSubscription(client: BackendAPIClient, id: number, subscription: BookSubscription): Promise<BookSubscription> {
	try {
		const response = await client.put({ path: `/subscription/${id}`, body: subscription });

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}, detail: ${await response.text()}`, {
				cause: response.status
			});
		}

		const data: BookSubscription = await response.json();

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

export async function deleteSubscription(client: BackendAPIClient, id: number): Promise<BookSubscription | null> {
	try {
		const response = await client.delete({ path: `/subscription/${id}` });

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}, detail: ${await response.text()}`, {
				cause: response.status
			});
		}

		const data: BookSubscription | null = await response.json();

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
