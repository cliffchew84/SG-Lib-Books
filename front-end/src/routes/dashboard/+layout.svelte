<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { LayoutData } from './$types';

	import Header from '$lib/components/layout/Header.svelte';
	import Footer from '$lib/components/layout/Footer.svelte';
	import Notification from '$lib/components/notification.svelte';
	import { Toaster } from '$lib/components/ui/sonner';
	import { isLoading, libraryAPIStore, bookStore } from '$lib/stores';
	import { getBooks } from '$lib/api/book';
	import { getLibraries } from '$lib/api/library';
	import type { Library } from '$lib/models';
	import type { BookResponse, BookAvail, LibraryResponse } from '$lib/api/models';
	import { getDateFromTimeString, formatAMPM } from '$lib/utils';

	let { children, data }: { children: Snippet; data: LayoutData } = $props();

	// Get all user's favourite books
	$effect(() => {
		(async () => {
			const apiResponseBook = await getBooks(data.client);
			const apiResponseLibrary: LibraryResponse[] = await getLibraries(data.client);
			isLoading.set(false);
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
			bookStore.set(
				Object.fromEntries(
					apiResponseBook.map((book: BookResponse) => {
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
		})();
	});
</script>

<Toaster />

<!-- Initialise FCM to receives and show notification -->
<!-- TODO: Merge this to notification component -->
<Notification />
<Header user={data.user} client={data.client} />

{@render children()}
<Footer />
