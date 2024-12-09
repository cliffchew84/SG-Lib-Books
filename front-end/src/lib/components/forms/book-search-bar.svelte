<script lang="ts">
	import { X, Search } from 'lucide-svelte';
	import { Input } from '$lib/components/ui/input';

	let {
		onSubmit,
		searchInput = $bindable()
	}: {
		onSubmit: (e: SubmitEvent) => any;
		searchInput: string;
	} = $props();
</script>

<div class="bg-background/95 backdrop-blur rounded">
	<form onsubmit={onSubmit}>
		<div class="relative">
			<Search class="text-muted-foreground absolute left-2 top-[50%] h-4 w-4 translate-y-[-50%]" />
			<Input placeholder="Book Title" class="px-8" bind:value={searchInput} />
			<input type="submit" hidden />
			<button
				class="absolute right-2 top-[50%] translate-y-[-50%]"
				onclick={() => {
					searchInput = '';
				}}
			>
				<X class="text-muted-foreground h-4 w-4" />
			</button>
		</div>
	</form>
</div>
