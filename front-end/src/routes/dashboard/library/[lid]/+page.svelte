<script lang="ts">
	import { toast } from 'svelte-sonner';

	import { Button } from '$lib/components/ui/button';
	import LibraryDetailsSection from '$lib/components/layout/LibraryDetailsSection.svelte';
	import PaginatedCards from '$lib/components/layout/PaginatedCards.svelte';

	import { unlikeBook } from '$lib/api/book';
	import { favouriteLibrary, unfavouriteLibrary } from '$lib/api/library';
	import { bookStore, libraryStore, libraryAPIStore } from '$lib/stores';
	import type { BookProp, Library } from '$lib/models';
	import type { PageData } from './$types';

	import { page } from '$app/stores';

	let { data }: { data: PageData } = $props();

	const lid = $page.params.lid;

	let library: Library | undefined = $derived($libraryStore[lid]);
	let isError: boolean = $derived(library === undefined);
	let availBooks: BookProp[] = $derived(
		library?.availBooks.map((book) => {
			return {
				...book,
				branches: undefined,
				bookMarkLoading: false,
				onBookMarked: async () => {
					try {
						console.log('Unbookmark book', book.brn);
						await unlikeBook(data.client, book.brn);
						bookStore.update((s) => {
							delete s[book.brn];
							return s;
						});
						toast.success(`Book ${book.title} is removed`);
					} catch (error) {
						if (error instanceof Error) {
							if (error.cause === 429) {
								toast.warning("We are hitting NLB's API too hard. Please try again later.");
							} else {
								toast.warning('Bookmark request has failed. Please try again later.');
							}
						}
						console.error('Bookmark/Unbookmark error:', error);
					}
				}
			};
		}) ?? []
	);
	let onLoanBooks: BookProp[] = $derived(
		library?.onLoanBooks.map((book) => {
			return {
				...book,
				callNumber: undefined,
				branches: undefined,
				bookMarkLoading: false,
				onBookMarked: async () => {
					try {
						console.log('Unbookmark book', book.brn);
						await unlikeBook(data.client, book.brn);
						bookStore.update((s) => {
							delete s[book.brn];
							return s;
						});
						toast.success(`Book ${book.title} is removed`);
					} catch (error) {
						if (error instanceof Error) {
							if (error.cause === 429) {
								toast.warning("We are hitting NLB's API too hard. Please try again later.");
							} else {
								toast.warning('Bookmark request has failed. Please try again later.');
							}
						}
						console.error('Bookmark/Unbookmark error:', error);
					}
				}
			};
		}) ?? []
	);
	let onFavourite = $derived(async () => {
		try {
			if (library.favourite) {
				await unfavouriteLibrary(data.client, library.name);
				toast.success(`${library.name} is removed from your favourites`);
			} else {
				await favouriteLibrary(data.client, library.name);
				toast.success(`${library.name} is added to your favourites`);
			}
			libraryAPIStore.update((s) => {
				s[library.name].favourite = !s[library.name].favourite;
				return s;
			});
		} catch (error) {
			if (error instanceof Error) {
				if (error.cause === 429) {
					toast.warning("We are hitting NLB's API too hard. Please try again later.");
				} else {
					toast.warning('Library favourite request has failed. Please try again later.');
				}
			}
			console.error('Favourite/unfavourite error:', error);
		}
	});

	// TODO: Show loan till date in card
</script>

<svelte:head>
	{#if isError}
		<title>Something Went Wrong | SG Lib Books</title>
	{:else}
		<title>{library.name} | SG Lib Books</title>
	{/if}
</svelte:head>

<main class="container flex flex-col gap-8 px-8 min-h-[85vh]">
	{#if !isError}
		<LibraryDetailsSection {...library} {onLoanBooks} {availBooks} {onFavourite} />
	{:else}
		<div class="my-5 flex flex-col gap-3">
			<h1 class="text-4xl font-bold text-slate-700">{lid} Library Not Found</h1>
			<p class="text-sm text-slate-500">
				The library that you have requested does not exist in our records.
			</p>
			<div class="w-full">
				<Button
					class="mx-auto"
					onclick={() => {
						history.back();
					}}>Back to Previous Page</Button
				>
			</div>
		</div>
	{/if}
	{#if availBooks.length > 0}
		<div class="flex flex-col gap-3">
			<h2 class="text-2xl font-bold text-slate-700">On-Shelf</h2>
			<p class="text-sm text-slate-500">Books available to be borrowed</p>
			<PaginatedCards
				books={availBooks}
				perPage={4}
				isLoading={false}
				count={availBooks.length}
				hidePagination={true}
				page={1}
			/>
		</div>
	{/if}
	{#if onLoanBooks.length > 0}
		<div class="flex flex-col gap-3">
			<h2 class="text-2xl font-bold text-slate-700">On-Loaned</h2>
			<p class="text-sm text-slate-500">Books on-loaned to fellow readers</p>
			<PaginatedCards
				books={onLoanBooks}
				perPage={5}
				isLoading={false}
				count={onLoanBooks.length}
				hidePagination={true}
				page={1}
			/>
		</div>
	{/if}
</main>
