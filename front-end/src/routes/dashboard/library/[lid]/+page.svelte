<script lang="ts">
	import { toast } from 'svelte-sonner';

	import { Button } from '$lib/components/ui/button';
	import LibraryDetailsSection from '$lib/components/layout/LibraryDetailsSection.svelte';
	import PaginatedCards from '$lib/components/layout/PaginatedCards.svelte';

	import { favouriteLibrary, unfavouriteLibrary } from '$lib/api/library';
	import { libraryStore, libraryAPIStore } from '$lib/stores';
	import { bookmarkBook } from '$lib/stores/book';
	import type { Book, BookProp, Library } from '$lib/models';
	import type { PageData } from './$types';

	import { page } from '$app/stores';

	let { data }: { data: PageData } = $props();

	const lid = $page.params.lid;
	const toBookProp = (book: Book) =>
		({
			...book,
			branches: undefined, // Remove branches from book
			bookMarkLoading: bookmarking[book.brn] ?? false,
			onBookMarked: async () => {
				bookmarking[book.brn] = true;
				await bookmarkBook(data.client, book.brn);
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
			if (library.favourite) {
				await unfavouriteLibrary(data.client, library.name);
				toast.success(`${library.name} is removed from your favourites`);
			} else {
				await favouriteLibrary(data.client, library.name);
				toast.success(`${library.name} is added to your favourites`);
			}
			libraryAPIStore.update((s) => {
				s[library!.name].favourite = !s[library!.name].favourite;
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

	// Update library dynamically as libraryStore changes
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
