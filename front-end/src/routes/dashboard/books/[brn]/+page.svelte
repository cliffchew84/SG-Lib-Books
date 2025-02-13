<script lang="ts">
	import { page } from '$app/stores';

	import Button from '$lib/components/ui/button/button.svelte';
	import BookDetailsSection from '$lib/components/layout/BookDetailsSection.svelte';
	import LibraryCarousel from '$lib/components/layout/LibraryCarousel.svelte';

	import type { BookAvail } from '$lib/api/models';
	import type { BookProp, Library, LibraryProp } from '$lib/models';
	import type { BookSubscription } from '$lib/api/models';
	import { bookStore, libraryAPIStore } from '$lib/stores';
	import { toggleBookmarkBook } from '$lib/stores/book';
	import { toggleFavouriteLibrary } from '$lib/stores/library';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
	const brn = Number($page.params.brn);

	let isLoading = $state(true);
	let isError = $state(false);
	let book: BookProp = $state({
		brn: brn,
		bookmarked: $bookStore[brn]?.bookmarked ?? false,
		bookMarkLoading: false,
		onBookMarked: async () => {
			book.bookMarkLoading = true;
			try {
				await toggleBookmarkBook(data.client, book.brn);
			} catch (e) {}
			book.bookMarkLoading = false;
		}
	});
	let subscriptions: BookSubscription[] = $state([]);
	let librariresProps: LibraryProp[] = $state([]);
	let librariesFavourite: LibraryProp[] = $derived(librariresProps.filter((lib) => lib.favourite));
	let librariesAvail: LibraryProp[] = $derived(
		librariresProps.filter((lib) => lib.availBooks.length > 0 && !lib.favourite)
	);
	let librariesOnLoan: LibraryProp[] = $derived(
		librariresProps.filter(
			(lib) => lib.onLoanBooks.length > 0 && lib.availBooks.length == 0 && !lib.favourite
		)
	);

	// Compute bookmarked based on bookStore update
	$effect(() => {
		book.bookmarked = $bookStore[brn]?.bookmarked ?? false;
	});

	// Receives API response for book details and update frontend states
	$effect(() => {
		(async () => {
			try {
				// Await backend API response
				const bookAPI = await data.bookResponse;
				isLoading = false;
				// Update front-end states
				book = {
					title: bookAPI.TitleName,
					author: bookAPI.Author,
					publishYear: bookAPI.PublishYear,
					callNumber:
						bookAPI.avails && bookAPI.avails.length > 0 ? bookAPI.avails[0].CallNumber : undefined,
					imageLink: bookAPI.cover_url,
					summary: bookAPI.summary,
					items: bookAPI.avails,
					...book
				};
			} catch (error) {
				isError = true;
			}
		})();
	});

	// Receives API response for subscription details and update frontend states
	$effect(() => {
		(async () => {
			try {
				subscriptions = await data.subscriptionResponse;
			} catch (error) {
				isError = true;
			}
		})();
	});

	// Compute library availability state
	$effect(() => {
		// Compute library availability state
		const libraries: { [key: string]: Library } = $libraryAPIStore;
		const branchAvail: { [key: string]: BookAvail[] } = {};
		// Reset onLoanBook and availBook state
		Object.keys(libraries).map((k) => {
			libraries[k].onLoanBooks = [];
			libraries[k].availBooks = [];
		});
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
		librariresProps = Object.values(libraries).map((lib) => {
			return {
				...lib,
				onFavourite: async () => {
					try {
						await toggleFavouriteLibrary(data.client, lib.name);
					} catch (e) {}
				}
			};
		});
	});
</script>

<svelte:head>
	{#if isError}
		<title>Something Went Wrong | SG Lib Books</title>
	{:else}
		<title>{book.title} | SG Lib Books</title>
	{/if}
</svelte:head>

<main class="container flex flex-col gap-8 p-8 min-h-[85vh]">
	{#if !isError}
		<BookDetailsSection
			{book}
			libraries={librariresProps}
			{isLoading}
			{subscriptions}
			client={data.client}
		/>
		{#if librariesFavourite.length > 0}
			<LibraryCarousel
				title="Your Favourite"
				description="Libraries marked as favourite by you."
				libraries={librariesFavourite}
			/>
		{/if}
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
	{:else}
		<div class="flex flex-col gap-3">
			<h1 class="text-4xl font-bold text-slate-700">404: Book Not Found</h1>
			<p class="text-sm text-slate-500">
				The book that you have requested does not exist on NLB's Catalogue
			</p>
			<Button
				onclick={() => {
					history.back();
				}}>Back to Search Results</Button
			>
		</div>
	{/if}
</main>
