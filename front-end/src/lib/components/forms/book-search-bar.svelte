<script lang="ts">
	import { X, Search } from 'lucide-svelte';
	import { Input } from '$lib/components/ui/input';
	import type { Book } from '$lib/models';

	let { isLoading = $bindable(), books = $bindable() }: { isLoading: boolean; books: Book[] } =
		$props();
	let searchValue = $state('');

	const book = {
		brn: 1,
		title: 'Elon Musk',
		author: 'Walter Issacson',
		publishYear: '2023',
		callNumber: '338.092 ISA -[BIZ]',
		branches: ['Bedok Library', 'The LLibrary', 'The Chinatown Library'],
		imageLink: 'https://m.media-amazon.com/images/I/71iWxmst49L._AC_UF1000,1000_QL80_.jpg',
		bookmarked: false
	};

	function onSubmit(e: SubmitEvent) {
		e.preventDefault();
		isLoading = true;
		setTimeout(() => {
			isLoading = false;
			books = Array(100).fill(book);
		}, 1000);
	}
</script>

<div class="bg-background/95 backdrop-blur rounded">
	<form onsubmit={onSubmit}>
		<div class="relative">
			<Search class="text-muted-foreground absolute left-2 top-[50%] h-4 w-4 translate-y-[-50%]" />
			<Input placeholder="Book Title" class="px-8" bind:value={searchValue} />
			<input type="submit" hidden />
			<button
				class="absolute right-2 top-[50%] translate-y-[-50%]"
				onclick={() => {
					searchValue = '';
				}}
			>
				<X class="text-muted-foreground h-4 w-4" />
			</button>
		</div>
	</form>
</div>
