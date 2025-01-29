import { derived, writable } from 'svelte/store';

import BackendAPIClient from '$lib/api/client';
import { getLibraries } from '$lib/api/library';
import type { BookAvail, LibraryResponse } from '$lib/api/models';
import type { Library } from '$lib/models';
import { bookStore } from '$lib/stores/book';
import { getDateFromTimeString, formatAMPM } from '$lib/utils';

export const libraryAPIStore = writable<{ [key: string]: Library }>({});
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
			if (!book.bookmarked || book.items?.length == 0) { return }
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
						console.warn(`${k} does not exist in database`);
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

export async function fetchLibraries(client: BackendAPIClient) {
	try {
		const apiResponseLibrary: LibraryResponse[] = await getLibraries(client);
		libraryAPIStore.set(
			apiResponseLibrary.reduce(
				(a, v) => {
					let openingStatusDesc = v.opening_status;
					let currentTime = new Date();
					if (v.opening_status === 'closed') {
						openingStatusDesc = 'Closed';
					} else {
						if (v.start_hour && v.end_hour) {
							let h = currentTime.getHours();
							let start_hour = getDateFromTimeString(v.start_hour);
							let end_hour = getDateFromTimeString(v.end_hour);
							if (
								// Closes on Sunday
								(v.opening_status === 'close sunday' && currentTime.getDay() == 0) ||
								h < start_hour.getHours()
							) {
								openingStatusDesc = `Closed · Opens at ${formatAMPM(start_hour)}`;
							} else if (h < end_hour.getHours()) {
								openingStatusDesc = `Opens Now · Closing at ${formatAMPM(end_hour)}`;
							} else if (v.opening_status === 'close sunday' && currentTime.getDay() == 6) {
								// If saturday, show library only opens on Monday
								openingStatusDesc = `Closed · Opens Monday at ${formatAMPM(start_hour)}`;
							} else {
								openingStatusDesc = `Closed · Opens at ${formatAMPM(start_hour)}`;
							}
						} else {
							openingStatusDesc = 'Opens Daily';
						}
					}

					a[v.name] = {
						name: v.name,
						onLoanBooks: [],
						availBooks: [],
						openingHoursDesc: openingStatusDesc,
						favourite: v.isFavourite,
						imageLink: v.cover_url,
						location: v.address?.replace('<br>', '\n')
					};
					return a;
				},
				{} as { [key: string]: Library }
			)
		);
	} catch (error) {
		console.error('Failed to fetch libraries', error);
		throw error;
	}
}

