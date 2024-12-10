<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import LibraryDetailsSection from '$lib/components/layout/LibraryDetailsSection.svelte';
	import PaginatedCards from '$lib/components/layout/PaginatedCards.svelte';
	import { unlikeBook } from '$lib/api/book';
	import { bookStore, libraryStore } from '$lib/stores';
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
				bookMarkLoading: false,
				onBookMarked: async () => {
					try {
						console.log('Unbookmark book', book.brn);
						await unlikeBook(data.client, book.brn);
						bookStore.update((s) => {
							delete s[book.brn];
							return s;
						});
					} catch (error) {
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
				bookMarkLoading: false,
				onBookMarked: async () => {
					try {
						console.log('Unbookmark book', book.brn);
						await unlikeBook(data.client, book.brn);
						bookStore.update((s) => {
							delete s[book.brn];
							return s;
						});
					} catch (error) {
						console.error('Bookmark/Unbookmark error:', error);
					}
				}
			};
		}) ?? []
	);

	// TODO: Show loan till date in card
</script>

<main class="container flex flex-col gap-8 px-8 min-h-[85vh]">
	{#if !isError}
		<LibraryDetailsSection {...library} {onLoanBooks} {availBooks} onFavourite={() => {}} />
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
				page={1}
			/>
		</div>
	{/if}
</main>
