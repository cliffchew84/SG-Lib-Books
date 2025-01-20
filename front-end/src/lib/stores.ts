import { derived, writable } from 'svelte/store';
import type { BookAvail } from '$lib/api/models';
import type { Book, Library, Notification } from '$lib/models';

export const isLoading = writable<boolean>(true);
export const libraryAPIStore = writable<{ [key: string]: Library }>({});
export const bookStore = writable<{ [key: number]: Book }>({});
export const libraryStore = derived(
	[bookStore, libraryAPIStore],
	([$bookStore, $libraryAPIStore]) => {
		const libraries: { [key: string]: Library } = $libraryAPIStore;
		// Reset onLoanBook and availBook state
		Object.keys(libraries).map((k) => {
			libraries[k].onLoanBooks = [];
			libraries[k].availBooks = [];
		})
		Object.values($bookStore).map((book) => {
			const branchAvail: { [key: string]: BookAvail[] } = {};
			// Split book items into dictionary of branch
			book.items?.map((avail) => {
				if (branchAvail.hasOwnProperty(avail.BranchName)) {
					branchAvail[avail.BranchName].push(avail);
				} else {
					branchAvail[avail.BranchName] = [avail];
				}
			});
			for (const [k, bookAvails] of Object.entries(branchAvail)) {
				for (let bookAvail of bookAvails) {
					if (!libraries.hasOwnProperty(k)) {
						console.warn(`Library ${k} does not exist in database`);
						continue;
					}
					if (bookAvail.StatusDesc == 'On Loan') {
						libraries[k].onLoanBooks.push({ ...book, dueDate: `Due ${bookAvail.DueDate}` });
					} else {
						libraries[k].availBooks.push(book);
					}
				}
			}
		});
		// Sort libraries result by alphabetical order
		const sortedResult: { [key: string]: Library } = {};
		Object.keys(libraries)
			.sort()
			.forEach((k) => {
				sortedResult[k] = libraries[k];
			});
		return sortedResult;
	}
);
export const notificationStore = writable<{ [key: string]: Notification }>({});
