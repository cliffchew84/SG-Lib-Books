<script lang="ts">
	import { page } from '$app/stores';
	import BookDetailsSection from '$lib/components/layout/BookDetailsSection.svelte';
	import LibraryCarousel from '$lib/components/layout/LibraryCarousel.svelte';
	import type { PageData } from './$types';
	import type { Book, Library } from '$lib/models';
	import type { BookAvail } from '$lib/api/models';

	let { data }: { data: PageData } = $props();

	let isLoading = $state(true);
	let book: Book = $state({
		brn: Number($page.params.brn),
		bookmarked: false
	});
	let librariesAvail: Library[] = $state([]);
	let librariesOnLoan: Library[] = $state([]);

	$effect(() => {
		(async () => {
			// Await backend API response
			let bookAPI = await data.bookResponse;
			isLoading = false;

			// Compute library availability state
			let branchAvail: { [key: string]: BookAvail[] } = {};
			let libraries: { [key: string]: Library } = {};
			bookAPI.avails.map((avail) => {
				if (branchAvail.hasOwnProperty(avail.BranchName)) {
					branchAvail[avail.BranchName].push(avail);
				} else {
					branchAvail[avail.BranchName] = [avail];
				}
			});
			for (const [k, bookAvails] of Object.entries(branchAvail)) {
				let name = k;
				let favourite = true;
				let noOnLoan = 0;
				let noAvail = 0;
				let openingHoursDesc = 'Open · Closes 10pm';
				for (let bookAvail of bookAvails) {
					if (bookAvail.StatusDesc == 'On Loan') {
						noOnLoan += 1;
					} else {
						noAvail += 1;
					}
				}
				libraries[k] = { id: name, name, noAvail, noOnLoan, favourite, openingHoursDesc };
			}

			// Update front-end states
			book = {
				brn: Number($page.params.brn),
				title: bookAPI.TitleName,
				author: bookAPI.Author,
				publishYear: bookAPI.PublishYear,
				callNumber:
					bookAPI.avails && bookAPI.avails.length > 0 ? bookAPI.avails[0].CallNumber : undefined,
				imageLink: bookAPI.cover_url,
				summary: bookAPI.summary,
				bookmarked: false,
				branches: Object.keys(branchAvail)
			};
			librariesAvail = Object.values(libraries).filter((lib) => {
				return lib.noAvail >= 1;
			});
			librariesOnLoan = Object.values(libraries).filter((lib) => {
				return lib.noAvail == 0;
			});
		})();
	});
</script>

<main class="container flex flex-col gap-8 p-8 min-h-[85vh]">
	<BookDetailsSection {...book} {isLoading} onBookMarked={() => {}} />
	<LibraryCarousel
		title="On-Shelf"
		description="Libraries with books available to be borrowed."
		libraries={librariesAvail}
	/>
	<LibraryCarousel
		title="On-Loaned"
		description="Libraries with all books on-loaned to fellow readers."
		libraries={librariesOnLoan}
	/>
</main>
