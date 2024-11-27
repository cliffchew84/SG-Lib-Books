<script lang="ts">
	import BookSearchBar from '$lib/components/forms/book-search-bar.svelte';
	import TitledPage from '$lib/components/layout/TitledPage.svelte';
	import PaginatedCards from '$lib/components/layout/PaginatedCards.svelte';

	let book = {
		title: 'Elon Musk',
		author: 'Walter Issacson',
		publishYear: '2023',
		callNumber: '338.092 ISA -[BIZ]',
		branches: ['Bedok Library', 'The LLibrary', 'The Chinatown Library'],
		imageLink: 'https://m.media-amazon.com/images/I/71iWxmst49L._AC_UF1000,1000_QL80_.jpg',
		bookmarked: false,
		onBookMarked: () => {}
	};
	let books = Array(100).fill(book);
</script>

<TitledPage title="Search" description="Add your favourite books from NLB's Catalogue.">
	<BookSearchBar />
	<PaginatedCards {books} perPage={25} />
</TitledPage>
