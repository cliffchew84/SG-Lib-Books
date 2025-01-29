<script lang="ts">
	import { Search } from 'lucide-svelte';
	import { bookStore } from '$lib/stores';
	import { toggleBookmarkBook } from '$lib/stores/book';
	import { Button } from '$lib/components/ui/button';
	import TitledPage from '$lib/components/layout/TitledPage.svelte';
	import PaginatedCards from '$lib/components/layout/PaginatedCards.svelte';
	import BookFilterBar from '$lib/components/layout/BookFilterBar.svelte';
	import type { Book, BookProp } from '$lib/models';
	import type { PageData } from './$types';
	const perPage = 25;

	let { data }: { data: PageData } = $props();

	let currentPage = $state(1);
	let isLoading = $state(false);
	let searchValue = $state('');
	let bookmarking: { [key: number]: boolean } = $state({});
	let books: BookProp[] = $derived(
		filterBooks(Object.values($bookStore)).map((book) => ({
			...book,
			bookMarkLoading: bookmarking[book.brn] ?? false,
			onBookMarked: async () => {
				bookmarking[book.brn] = true;
				try {
					await toggleBookmarkBook(data.client, book.brn);
				} catch (e) {}
				bookmarking[book.brn] = false;
			}
		}))
	);
	let count = $derived(Object.values($bookStore).length);

	function filterBooks(books: Book[]) {
		if (!searchValue) return books;
		// Normalize search value: trim and convert to lowercase
		const normalizedSearch = searchValue.trim().toLowerCase();

		return Object.values(books).filter((bk) => {
			// Check against multiple fields: title, author, call number
			const searchFields = [bk.title, bk.author, bk.callNumber];

			// Convert each field to lowercase and remove extra spaces
			return searchFields.some((field) =>
				field
					? field
							.toLowerCase()
							.replace(/\s+/g, ' ') // Normalize spaces
							.includes(normalizedSearch)
					: false
			);
		});
	}
</script>

<svelte:head>
	<title>Books | SG Lib Books</title>
</svelte:head>

<TitledPage title="Books" description="Checkout all your favourite books.">
	{#if count > 0}
		<BookFilterBar bind:searchValue />
		<PaginatedCards
			{books}
			{perPage}
			{count}
			hidePagination={true}
			bind:isLoading
			bind:page={currentPage}
		/>
	{:else}
		<div class="w-full flex flex-col items-center gap-3">
			<p>Search your favourite library books</p>
			<Button href="/dashboard/search">
				<Search class="mr-2 h-4 w-4" />
				<span>Search</span>
			</Button>
		</div>
	{/if}
</TitledPage>
