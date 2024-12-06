import type { PageLoad } from './$types'
import { getBooks } from '$lib/api/book'

export const load: PageLoad = async ({ parent }) => {
	/**
	 * Query books data from backend
	 */
	const { client } = await parent()

	const bookResponse = getBooks(client)

	return { bookResponse }
}
