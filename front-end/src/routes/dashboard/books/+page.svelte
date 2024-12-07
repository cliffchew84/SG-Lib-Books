<script lang="ts">
	import { Search } from 'lucide-svelte';
	import { bookStore } from '$lib/stores';
	import { Button } from '$lib/components/ui/button';
	import TitledPage from '$lib/components/layout/TitledPage.svelte';
	import PaginatedCards from '$lib/components/layout/PaginatedCards.svelte';
	import BookFilterBar from '$lib/components/layout/BookFilterBar.svelte';
	import type { Book } from '$lib/models';
	import type { PageData } from './$types';
	import type { BookAvail, BookResponse } from '$lib/api/models';
	const perPage = 25;

	let { data }: { data: PageData } = $props();

	let books: Book[] = $state([]);
	let currentPage = $state(1);
	let isLoading = $state(false);
	let searchValue = $state('');
	let filteredBooks: Book[] = $state([]);
	let count = $derived(books.length);

	// Effect to load books from API
	$effect(() => {
		(async () => {
			// Await backend API response
			isLoading = true;
			let bookAPI = await data.bookResponse;
			isLoading = false;

			books = bookAPI.map((book: BookResponse) => {
				let branchAvail: { [key: string]: BookAvail[] } = {};
				book.avails.map((avail) => {
					if (branchAvail.hasOwnProperty(avail.BranchName)) {
						branchAvail[avail.BranchName].push(avail);
					} else {
						branchAvail[avail.BranchName] = [avail];
					}
				});
				return {
					brn: book.BID,
					title: book.TitleName,
					author: book.Author,
					publishYear: book.PublishYear,
					callNumber: book.avails && book.avails.length > 0 ? book.avails[0].CallNumber : undefined,
					imageLink: book.cover_url,
					summary: book.summary,
					bookmarked: $bookStore.hasOwnProperty(book.BID),
					branches: Object.keys(branchAvail)
				} as Book;
			});
		})();
	});

	// Effect to filter books
	$effect(() => {
		if (!searchValue) {
			filteredBooks = books;
		} else {
			// Normalize search value: trim and convert to lowercase
			isLoading = true;
			const normalizedSearch = searchValue.trim().toLowerCase();

			const result = books.filter((bk) => {
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

<TitledPage title="Books" description="Checkout all your favourite books.">
	<BookFilterBar bind:searchValue />
	{#if count > 0}
		<PaginatedCards
			books={filteredBooks}
			{perPage}
			{count}
			bind:isLoading
			bind:page={currentPage}
		/>
	{:else}
		<div class="w-full flex flex-col items-center gap-3">
			<p>Mark your favourite library books at</p>
			<Button href="/dashboard/search">
				<Search class="mr-2 h-4 w-4" />
				<span>Search</span>
			</Button>
		</div>
	{/if}
</TitledPage>
