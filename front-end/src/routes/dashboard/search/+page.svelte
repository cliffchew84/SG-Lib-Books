<script lang="ts">
	import BookSearchBar from '$lib/components/forms/book-search-bar.svelte';
	import TitledPage from '$lib/components/layout/TitledPage.svelte';
	import PaginatedCards from '$lib/components/layout/PaginatedCards.svelte';
	import type { Book } from '$lib/models';

	let isSearching = $state(false);
	let books: Book[] = $state([]);
</script>

<TitledPage title="Search" description="Add your favourite books from NLB's Catalogue.">
	<BookSearchBar bind:isLoading={isSearching} bind:books />
	<PaginatedCards {books} perPage={25} isLoading={isSearching} />
</TitledPage>
