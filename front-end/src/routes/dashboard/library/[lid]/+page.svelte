<script lang="ts">
	import type { PageData } from './$types';
	import { page } from '$app/stores';

	import { Button } from '$lib/components/ui/button';
	import LibraryDetailsSection from '$lib/components/layout/LibraryDetailsSection.svelte';
	import PaginatedCards from '$lib/components/layout/PaginatedCards.svelte';

	import type { Book, BookProp, Library } from '$lib/models';
	import { libraryStore } from '$lib/stores';
	import { toggleBookmarkBook } from '$lib/stores/book';
	import { toggleFavouriteLibrary } from '$lib/stores/library';

	let { data }: { data: PageData } = $props();

	const lid = $page.params.lid;
	const toBookProp = (book: Book) =>
		({
			...book,
			branches: undefined, // Remove branches from book
			bookMarkLoading: bookmarking[book.brn] ?? false,
			onBookMarked: async () => {
				bookmarking[book.brn] = true;
				try {
					await toggleBookmarkBook(data.client, book.brn);
				} catch (e) {}
				bookmarking[book.brn] = false;
			}
		}) as BookProp;

	let bookmarking: { [key: number]: boolean } = $state({});
	let library: Library | undefined = $state($libraryStore[lid]);
	let availBooks: BookProp[] = $derived(library?.availBooks.map(toBookProp) ?? []);
	let onLoanBooks: BookProp[] = $derived(library?.onLoanBooks.map(toBookProp) ?? []);
	let onFavourite = $derived(async () => {
		if (library === undefined) {
			// Do nothing if library is undefined
			return;
		}
		try {
			await toggleFavouriteLibrary(data.client, library.name);
		} catch (e) {}
	});
	$effect(() => {
		library = $libraryStore[lid];
	});
</script>

<svelte:head>
	{#if library !== undefined}
		<title>{library!.name} | SG Lib Books</title>
	{:else}
		<title>Unknown Library | SG Lib Books</title>
	{/if}
</svelte:head>

<main class="container flex flex-col gap-8 px-8 min-h-[85vh]">
	{#if library !== undefined}
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
