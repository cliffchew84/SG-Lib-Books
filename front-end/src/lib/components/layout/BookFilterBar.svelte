<script lang="ts">
	import { X, Search } from 'lucide-svelte';
	import { Input } from '$lib/components/ui/input';

	let { searchValue = $bindable() }: { searchValue: string } = $props();
</script>

<div class="bg-background/95 backdrop-blur rounded relative">
	<Search class="text-muted-foreground absolute left-2 top-[50%] h-4 w-4 translate-y-[-50%]" />
	<Input
		placeholder="Filter Book from Title, Author, or Call Number"
		class="px-8"
		bind:value={searchValue}
	/>
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
