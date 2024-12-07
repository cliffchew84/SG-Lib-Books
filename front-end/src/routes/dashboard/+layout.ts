import { redirect } from '@sveltejs/kit'
import { bookStore } from '$lib/stores'
import { getBooks } from '$lib/api/book'
import type { BookResponse, BookAvail } from '$lib/api/models'
import type { LayoutLoad } from './$types'

export const load: LayoutLoad = async ({ parent }) => {
	/**
	 * Check if user session is available, else redirect to login
	 */
	const { session, client } = await parent();
	if (!session) {
		redirect(307, '/auth/sign-in')
	}
	// Get all user's favourite books
	const apiReponse = await getBooks(client)
	console.log("I run")
	bookStore.set(
		Object.fromEntries(apiReponse.map((book: BookResponse) => {
			let branchAvail: { [key: string]: BookAvail[] } = {};
			book.avails.map((avail) => {
				if (branchAvail.hasOwnProperty(avail.BranchName)) {
					branchAvail[avail.BranchName].push(avail);
				} else {
					branchAvail[avail.BranchName] = [avail];
				}
			});
			return [book.BID, {
				brn: book.BID,
				title: book.TitleName,
				author: book.Author,
				publishYear: book.PublishYear,
				callNumber: book.avails && book.avails.length > 0 ? book.avails[0].CallNumber : undefined,
				imageLink: book.cover_url,
				summary: book.summary,
				bookmarked: true,
				branches: Object.keys(branchAvail)
			}];
		}))
	)
}
