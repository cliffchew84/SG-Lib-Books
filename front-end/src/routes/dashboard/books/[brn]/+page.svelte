<script lang="ts">
	import { page } from '$app/stores';
	import BookDetailsSection from '$lib/components/layout/BookDetailsSection.svelte';
	import LibraryCarousel from '$lib/components/layout/LibraryCarousel.svelte';

	const brn = $page.params.brn;

	let book = {
		title: 'Elon Musk',
		author: 'Walter Issacson',
		publishYear: '2023',
		callNumber: '338.092 ISA -[BIZ]',
		branches: ['Bedok Library', 'The LLibrary', 'The Chinatown Library'],
		imageLink: 'https://m.media-amazon.com/images/I/71iWxmst49L._AC_UF1000,1000_QL80_.jpg',
		summary: `#1 New York Times bestseller\nFrom the author of Steve Jobs and other bestselling biographies, this is the astonishingly intimate  story of the most fascinating and controversial innovator of our era—a rule-breaking visionary who helped to lead the world into the era of electric vehicles, private space exploration, and artificial  intelligence. Oh, and took over Twitter.\nWhen Elon Musk was a kid in South Africa, he was regularly beaten by bullies. One day a  group pushed him down some concrete steps and kicked him until his face  was a swollen ball of flesh. He was in the hospital for a week. But the  physical scars were minor compared to the emotional ones inflicted by  his father, an engineer, rogue, and charismatic fantasist.\nHis  father's impact on his psyche would linger. He developed into a tough  yet vulnerable man-child, prone to abrupt Jekyll-and-Hyde mood swings,  with an exceedingly high tolerance for risk, a craving for drama, an  epic sense of mission, and a maniacal intensity that was callous and at  times destructive.\nAt the beginning of 2022—after a year marked  by SpaceX launching thirty-one rockets into orbit, Tesla selling a  million cars, and him becoming the richest man on earth—Musk spoke  ruefully about his compulsion to stir up dramas. "I need to shift my  mindset away from being in crisis mode, which it has been for about  fourteen years now, or arguably most of my life," he said.\nIt  was a wistful comment, not a New Year's resolution. Even as he said it,  he was secretly buying up shares of Twitter, the world's ultimate  playground. Over the years, whenever he was in a dark place, his mind  went back to being bullied on the playground. Now he had the chance to  own the playground.`,
		bookmarked: false
	};
	let library = {
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

<main class="container flex flex-col gap-8 p-8">
	<BookDetailsSection brn={Number(brn)} {...book} onBookMarked={() => {}} />
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
</main>
