import type { PageLoad } from './$types';
import { getBook } from '$lib/api/book';
import { getBookSubscription } from '$lib/api/bookSubscription';

export const load: PageLoad = async ({ parent, params }) => {
	/**
	 * Query book data from backend
	 */
	const { client } = await parent();

	const brn = parseInt(params.brn);
	const bookResponse = getBook(client, brn);
	const subscriptionResponse = getBookSubscription(client, brn);

	return { bookResponse, subscriptionResponse };
};
