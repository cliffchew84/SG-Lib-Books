import { derived, writable } from "svelte/store";
import type { BookAvail } from "$lib/api/models";
import type { Book, Library } from "$lib/models";

export const isLoading = writable<boolean>(true);
export const libraryAPIStore = writable<{ [key: string]: Library }>({})
export const bookStore = writable<{ [key: number]: Book }>({})
export const libraryStore = derived([bookStore, libraryAPIStore], ([$bookStore, $libraryAPIStore]) => {
	const libraries: { [key: string]: Library } = {};
	const branchAvail: { [key: string]: BookAvail[] } = {};
	Object.values($bookStore).map((book) => {
		// Split book items into dictionary of branch
		book.items?.map((avail) => {
			if (branchAvail.hasOwnProperty(avail.BranchName)) {
				branchAvail[avail.BranchName].push(avail);
			} else {
				branchAvail[avail.BranchName] = [avail];
			}
		});
		for (const [k, bookAvails] of Object.entries(branchAvail)) {
			let onLoanBooks = [];
			let availBooks = [];
			for (let bookAvail of bookAvails) {
				if (bookAvail.StatusDesc == 'On Loan') {
					onLoanBooks.push(book)
				} else {
					availBooks.push(book)
				}
			}

			if (libraries.hasOwnProperty(k)) {
				libraries[k].onLoanBooks.concat(onLoanBooks);
				libraries[k].availBooks.concat(availBooks);
			} else {
				if ($libraryAPIStore.hasOwnProperty(k)) {
					libraries[k] = {
						name: k,
						favourite: $libraryAPIStore[k].favourite,
						location: $libraryAPIStore[k].location,
						openingHoursDesc: $libraryAPIStore[k].openingHoursDesc,
						imageLink: $libraryAPIStore[k].imageLink,
						onLoanBooks,
						availBooks,
					}
				}
			}
		}
	}
	)
	const sortedResult: { [key: string]: Library } = {}
	Object.keys(libraries).sort().forEach(function(k) {
		sortedResult[k] = libraries[k]
	});
	return sortedResult;
})
