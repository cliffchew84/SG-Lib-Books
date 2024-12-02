<script lang="ts">
	import BookSearchBar from '$lib/components/forms/book-search-bar.svelte';
	import TitledPage from '$lib/components/layout/TitledPage.svelte';
	import PaginatedCards from '$lib/components/layout/PaginatedCards.svelte';
	import type { Book } from '$lib/models';
	import type { PageData } from '../$types';
	import { searchBook } from '$lib/api/search';

	let { data }: { data: PageData } = $props();

	let searchInput = $state(''); // Input search box
	let searchValue: string = $state(''); // search text when onSubmit is trigger
	let books: Book[] = $state([]);

	let isSearching = $state(false);
	let isError = $state(false);

	let total_records: number | null = $state(null);
	let has_more_records: boolean | null = $state(null);
	let next_offset = $state(0);

	async function onSubmit(e: SubmitEvent) {
		e.preventDefault(); // Prevent page reload

		// Reset initial state
		isSearching = true;
		isError = false;
		books = [];
		total_records = null;
		has_more_records = null;
		searchValue = searchInput;

		try {
			const response = await searchBook(data.client, searchValue, next_offset);
			isSearching = false;
			let searchBooks: Book[] = [];
			for (let title of response.titles) {
				searchBooks.push({
					brn: title.BID,
					title: title.TitleName,
					author: title.Author,
					imageLink: title.cover_url,
					bookmarked: false
				});
			}
			books = searchBooks;
			total_records = response.total_records;
			has_more_records = response.has_more_records;
			next_offset = response.next_offset;
		} catch (error) {
			isSearching = false;
			isError = true;
			console.error(error);
		}
	}
</script>

<TitledPage title="Search" description="Add your favourite books from NLB's Catalogue.">
	<BookSearchBar {onSubmit} bind:searchInput />
	{#if !isError}
		{#if total_records === 0}
			<div>
				<p>
					Your search - <span class="font-semibold">{searchValue}</span> - did not match any books.
				</p>
				<ul class="list-disc list-inside">
					<span>What you can do:</span>
					<li>Check for any spelling error.</li>
					<li>Avoid using acronyms.</li>
					<li>Reduce the number of keywords, or use more general terms.</li>
				</ul>
			</div>
		{:else}
			<PaginatedCards {books} perPage={25} isLoading={isSearching} />
		{/if}
	{:else}
		<p>An unknown error has occurred.</p>
		<p>If this behaviour persist, please contact us to make this app better, together.</p>
	{/if}
</TitledPage>
