<script lang="ts">
	import { Search } from 'lucide-svelte';
	import { toast } from 'svelte-sonner';
	import { likeBook, unlikeBook } from '$lib/api/book';
	import { bookStore } from '$lib/stores';
	import { Button } from '$lib/components/ui/button';
	import TitledPage from '$lib/components/layout/TitledPage.svelte';
	import PaginatedCards from '$lib/components/layout/PaginatedCards.svelte';
	import BookFilterBar from '$lib/components/layout/BookFilterBar.svelte';
	import type { BookProp } from '$lib/models';
	import type { PageData } from './$types';
	const perPage = 25;

	let { data }: { data: PageData } = $props();

	let books: { [key: number]: BookProp } = $derived(
		Object.fromEntries(
			Object.entries($bookStore).map(([k, v]) => {
				const brn = Number(k);
				return [
					brn,
					{
						...v,
						bookMarkLoading: false,
						onBookMarked: async () => {
							books[brn].bookMarkLoading = true;
							try {
								if ($bookStore.hasOwnProperty(brn)) {
									console.log('Unbookmark book', brn);
									await unlikeBook(data.client, brn);
									toast.success(`Book ${books[brn].title} is removed`);
									bookStore.update((s) => {
										delete s[brn];
										return s;
									});
								} else {
									console.log('bookmark book', k);
									await likeBook(data.client, brn);
									bookStore.update((s) => {
										s[brn] = { ...v, bookmarked: true };
										return s;
									});
									toast.success(`Book ${books[brn].title} is added`);
									books[brn].bookMarkLoading = false;
									books[brn].bookmarked = !books[brn].bookmarked;
								}
							} catch (error) {
								if (error instanceof Error) {
									if (error.cause === 429) {
										toast.warning("We are hitting NLB's API too hard. Please try again later.");
									} else {
										toast.warning('Bookmark request has failed. Please try again later.');
									}
								}
								console.error('Bookmark/Unbookmark error:', error);
								books[brn].bookMarkLoading = false;
							}
						}
					} as BookProp
				];
			})
		)
	);
	let currentPage = $state(1);
	let isLoading = $state(false);
	let searchValue = $state('');
	let filteredBooks: BookProp[] = $state([]);
	let count = $derived(Object.values(books).length);

	// Effect to filter books
	$effect(() => {
		if (!searchValue) {
			filteredBooks = Object.values(books);
		} else {
			// Normalize search value: trim and convert to lowercase
			isLoading = true;
			const normalizedSearch = searchValue.trim().toLowerCase();

			const result = Object.values(books).filter((bk) => {
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

			isLoading = false;
			filteredBooks = result;
		}
	});
</script>

<svelte:head>
	<title>Books | SG Lib Books</title>
</svelte:head>

<TitledPage title="Books" description="Checkout all your favourite books.">
	{#if count > 0}
		<BookFilterBar bind:searchValue />
		<PaginatedCards
			books={filteredBooks}
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
