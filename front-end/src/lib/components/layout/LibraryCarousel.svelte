<script lang="ts">
	import { ScrollArea } from '$lib/components/ui/scroll-area/index.js';
	import LibraryCard from '$lib/components/layout/LibraryCard.svelte';
	import type { LibraryProp } from '$lib/models.ts';

	let {
		title = '',
		description = '',
		libraries = []
	}: {
		title: String;
		description: String;
		libraries: LibraryProp[];
	} = $props();
</script>

{#if libraries.length !== 0}
	<div class="flex flex-col gap-3">
		<h2 class="text-2xl font-bold text-slate-700">{title}</h2>
		<p class="text-sm text-slate-500">{description}</p>

		<ScrollArea class="whitespace-nowrap" orientation="horizontal">
			<div class="flex w-max space-x-4">
				{#each libraries as library}
					<div class="w-[250px]">
						<LibraryCard {...library} disableLink={false} />
					</div>
				{/each}
			</div>
		</ScrollArea>
	</div>
{/if}
