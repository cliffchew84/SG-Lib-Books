<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';

	import { bookStore } from '$lib/stores';
	import { toggleBookmarkBook } from '$lib/stores/book';
	import { searchBook } from '$lib/api/search';
	import BookSearchBar from '$lib/components/forms/book-search-bar.svelte';
	import TitledPage from '$lib/components/layout/TitledPage.svelte';
	import PaginatedCards from '$lib/components/layout/PaginatedCards.svelte';
	import type { BookProp } from '$lib/models';
	import type { PageData } from '../$types';

	let { data }: { data: PageData } = $props();

	const perPage = 25;
	let searchInput = $state($page.url.searchParams.get('q') ?? ''); // Input search box
	let books: { [key: number]: BookProp } = $state({});

	let isSearching = $state(false);
	let isError = $state(false);

	let currentPage = $state(parseInt($page.url.searchParams.get('page') ?? '1'));
	let prevPage = $state(parseInt($page.url.searchParams.get('page') ?? '1'));
	let totalRecords: number | null = $state(null);
	let offset = $derived((currentPage - 1) * perPage);

	async function onSubmit(e?: SubmitEvent) {
		if (e) e.preventDefault(); // Prevent page reload
		if (searchInput === '') return;

		// Reset initial state
		isSearching = true;
		isError = false;
		books = {};
		totalRecords = null;
		goto(`?q=${searchInput}&page=${currentPage}`); // Add query data to url

		try {
			const response = await searchBook(data.client, searchInput, offset);
			isSearching = false;
			books = Object.fromEntries(
				response.titles.map((book) => [
					book.BID,
					{
						brn: book.BID,
						title: book.TitleName,
						author: book.Author,
						imageLink: book.cover_url,
						publishYear: book.PublishYear,
						bookmarked: $bookStore[book.BID]?.bookmarked ?? false,
						bookMarkLoading: false,
						onBookMarked: async () => {
							books[book.BID].bookMarkLoading = true;
							try {
								await toggleBookmarkBook(data.client, book.BID);
								books[book.BID].bookmarked = !books[book.BID].bookmarked;
							} catch (e) {}
							books[book.BID].bookMarkLoading = false;
						}
					}
				])
			);
			totalRecords = response.total_records;
		} catch (error) {
			isSearching = false;
			isError = true;
			console.error(error);
		}
	}

	onMount(() => {
		// Start searching after mount if `q` is present in query
		if (searchInput) {
			onSubmit();
		}
	});

	$effect(() => {
		// Re-trigger query on page changed
		if (prevPage !== currentPage) {
			prevPage = currentPage;
			onSubmit();
		}
	});
</script>

<svelte:head>
	<title>Search | SG Lib Books</title>
</svelte:head>

<TitledPage title="Search" description="Add your favourite books from NLB's Catalogue.">
	<BookSearchBar {onSubmit} bind:searchInput />
	{#if !isError}
		{#if totalRecords === 0}
			<div>
				<p>
					Your search - <span class="font-semibold">{$page.url.searchParams.get('q')}</span> - did not
					match any books.
				</p>
				<ul class="list-disc list-inside">
					<span>What you can do:</span>
					<li>Check for any spelling error.</li>
					<li>Avoid using acronyms.</li>
					<li>Reduce the number of keywords, or use more general terms.</li>
				</ul>
			</div>
		{:else}
			<PaginatedCards
				books={Object.values(books)}
				{perPage}
				isLoading={isSearching}
				count={totalRecords ?? 0}
				bind:page={currentPage}
				hidePagination={false}
			/>
		{/if}
	{:else}
		<p>Something went wrong...</p>
		<p>If this behaviour persist, please contact us to make this app better, together.</p>
	{/if}
</TitledPage>
