import { toast } from 'svelte-sonner';
import { get, derived, writable } from 'svelte/store';

import type { Book } from '$lib/models';
import { getBooks, likeBook, unlikeBook } from '$lib/api/book';
import type BackendAPIClient from '$lib/api/client';
import type { BookResponse, BookAvail } from '$lib/api/models';

export const bookStore = writable<{ [key: number]: Book }>({});

export async function fetchBooks(client: BackendAPIClient) {
	// Fetch favorite books from API
	try {
		const bookResponse = await getBooks(client);
		bookStore.set(
			Object.fromEntries(
				bookResponse.map((book: BookResponse) => {
					let branchAvail: { [key: string]: BookAvail[] } = {};
					book.avails.map((avail) => {
						if (branchAvail.hasOwnProperty(avail.BranchName)) {
							branchAvail[avail.BranchName].push(avail);
						} else {
							branchAvail[avail.BranchName] = [avail];
						}
					});
					return [
						book.BID,
						{
							brn: book.BID,
							title: book.TitleName,
							author: book.Author,
							publishYear: book.PublishYear,
							callNumber:
								book.avails && book.avails.length > 0 ? book.avails[0].CallNumber : undefined,
							imageLink: book.cover_url,
							summary: book.summary,
							bookmarked: true,
							branches: Object.keys(branchAvail),
							items: book.avails
						}
					];
				})
			)
		);
	} catch (error) {
		console.error('Failed to fetch books', error);
		throw error;
	}
}

export async function bookmarkBook(client: BackendAPIClient, brn: number) {
	try {
		if (get(bookStore)[brn]?.bookmarked ?? false) {
			await unlikeBook(client, brn);
			bookStore.update((s) => {
				s[brn].bookmarked = !s[brn].bookmarked;
				toast.success(`Book ${s[brn].title} is removed`);
				return s;
			});
		}
		else {
			const book = await likeBook(client, brn);
			bookStore.update((s) => {
				s[book.BID] = {
					brn: book.BID,
					title: book.TitleName,
					author: book.Author,
					imageLink: book.cover_url,
					bookmarked: true,
					items: book.avails ?? []
				};
				toast.success(`Book ${book.TitleName} is added`);
				return s;
			});
		}
	} catch (error) {
		if (error instanceof Error) {
			if (error.cause === 429) {
				toast.warning("We are hitting NLB's API too hard. Please try again later.");
			} else {
				toast.warning('Bookmark request has failed. Please try again later.');
			}
		}
		console.error('Bookmark/Unbookmark error:', error);
		throw error;
	}
}

