<script lang="ts">
	import TitledPage from '$lib/components/layout/TitledPage.svelte';
	import PaginatedCards from '$lib/components/layout/PaginatedCards.svelte';
	import BookFilterBar from '$lib/components/layout/BookFilterBar.svelte';
	import type { Book } from '$lib/models';

	const book: Book = {
		brn: 1,
		title: 'Elon Musk',
		author: 'Walter Issacson',
		publishYear: '2023',
		callNumber: '338.092 ISA -[BIZ]',
		branches: ['Bedok Library', 'The LLibrary', 'The Chinatown Library'],
		imageLink: 'https://m.media-amazon.com/images/I/71iWxmst49L._AC_UF1000,1000_QL80_.jpg',
		bookmarked: false
	};
	const count = 100;
	const books = Array(25).fill(book);

	let currentPage = $state(1);
	let isFiltering = $state(false);
	let searchValue = $state('');
	let filteredBooks = $state(books);

	$effect(() => {
		if (!searchValue) {
			filteredBooks = books;
		} else {
			// Normalize search value: trim and convert to lowercase
			isFiltering = true;
			const normalizedSearch = searchValue.trim().toLowerCase();

			const result = books.filter((bk) => {
				// Check against multiple fields: title, author, call number
				const searchFields = [bk.title, bk.author, bk.callNumber];

				// Convert each field to lowercase and remove extra spaces
				return searchFields.some((field) =>
					field
						.toLowerCase()
						.replace(/\s+/g, ' ') // Normalize spaces
						.includes(normalizedSearch)
				);
			});

			isFiltering = false;
			filteredBooks = result;
		}
	});
</script>

<TitledPage title="Books" description="Checkout all your favourite books.">
	<!-- TODO: add book search and filter -->
	<BookFilterBar bind:searchValue />
	<PaginatedCards
		books={filteredBooks}
		perPage={25}
		bind:isLoading={isFiltering}
		{count}
		page={currentPage}
	/>
</TitledPage>
