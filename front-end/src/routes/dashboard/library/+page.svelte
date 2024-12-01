<script lang="ts">
	import TitledPage from '$lib/components/layout/TitledPage.svelte';
	import LibraryCarousel from '$lib/components/layout/LibraryCarousel.svelte';
	const library = {
		id: '1',
		name: 'Bedok Regional Library',
		noOnLoan: 1,
		noAvail: 2,
		openingHoursDesc: 'Open · Closes 10pm',
		favourite: true
	};

	let librariesAvail = Array(10).fill(library);
	let librariesOnLoan = Array(3).fill(library);
</script>

<TitledPage
	title="Library"
	description="Checkout your favaourite books in every library operated by NLB."
>
	<LibraryCarousel
		title="On-Shelf"
		description="Libraries with books available to be borrowed."
		libraries={librariesAvail}
	/>
	<LibraryCarousel
		title="On-Loaned"
		description="Libraries with all books on-loaned to fellow readers."
		libraries={librariesOnLoan}
	/>
</TitledPage>
