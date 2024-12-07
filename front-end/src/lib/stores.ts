import { derived, writable } from "svelte/store";
import type { BookAvail } from "$lib/api/models";
import type { Book, Library } from "$lib/models";

export const bookStore = writable<{ [key: number]: Book }>({})
export const libraryStore = derived(bookStore, ($bookStore) => {
	const libraries: { [key: string]: Library } = {}
	const branchAvail: { [key: string]: BookAvail[] } = {};
	Object.values($bookStore).map((book) => {
		book.items?.map((avail) => {
			if (branchAvail.hasOwnProperty(avail.BranchName)) {
				branchAvail[avail.BranchName].push(avail);
			} else {
				branchAvail[avail.BranchName] = [avail];
			}
		});
		for (const [k, bookAvails] of Object.entries(branchAvail)) {
			let noOnLoan = 0;
			let noAvail = 0;
			for (let bookAvail of bookAvails) {
				if (bookAvail.StatusDesc == 'On Loan') {
					noOnLoan += 1;
				} else {
					noAvail += 1;
				}
			}

			if (libraries.hasOwnProperty(k)) {
				libraries[k].noOnLoan += noOnLoan;
				libraries[k].noAvail += noAvail;
			} else {
				libraries[k] = {
					id: k,
					name: k,
					favourite: false,
					openingHoursDesc: 'Open · Closes 10pm',
					noAvail,
					noOnLoan,
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
