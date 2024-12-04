<script lang="ts">
	import LibraryDetailsSection from '$lib/components/layout/LibraryDetailsSection.svelte';
	import PaginatedCards from '$lib/components/layout/PaginatedCards.svelte';
	import { page } from '$app/stores';

	let currentPage = $state(1);
	const count = 12;
	const lid = $page.params.lid;
	const library = {
		id: lid,
		name: 'Bedok Regional Library',
		noOnLoan: 1,
		noAvail: 2,
		openingHoursDesc: 'Open · Closes 10pm',
		favourite: true
	};
	const book = {
		brn: 1,
		title: 'Elon Musk',
		author: 'Walter Issacson',
		publishYear: '2023',
		callNumber: '338.092 ISA -[BIZ]',
		imageLink: 'https://m.media-amazon.com/images/I/71iWxmst49L._AC_UF1000,1000_QL80_.jpg',
		bookmarked: false
	};
	const booksOnShelf = Array(12).fill(book);
	// TODO: Show loan till date in card
	const booksOnLoan = Array(12).fill(book);
</script>

<main class="container flex flex-col gap-8 mb-6">
	<LibraryDetailsSection {...library} onFavourite={() => {}} />

	<div class="flex flex-col gap-3">
		<h2 class="text-2xl font-bold text-slate-700">On-Shelf</h2>
		<p class="text-sm text-slate-500">Books available to be borrowed</p>
		<PaginatedCards books={booksOnShelf} perPage={4} isLoading={false} {count} page={currentPage} />
	</div>
	<div class="flex flex-col gap-3">
		<h2 class="text-2xl font-bold text-slate-700">On-Loaned</h2>
		<p class="text-sm text-slate-500">Books on-loaned to fellow readers</p>
		<PaginatedCards books={booksOnLoan} perPage={5} isLoading={false} {count} page={currentPage} />
	</div>
</main>
