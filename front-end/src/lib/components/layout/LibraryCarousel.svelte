<script lang="ts">
	import * as Carousel from '$lib/components/ui/carousel/index.js';
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

		<Carousel.Root>
			<Carousel.Content>
				{#each libraries as library}
					<Carousel.Item class="basis-1/2 lg:basis-1/4 my-3">
						<LibraryCard {...library} />
					</Carousel.Item>
				{/each}
			</Carousel.Content>
			<div class="hidden md:block">
				<!-- Hide navigation button in mobile interface -->
				<Carousel.Previous />
				<Carousel.Next />
			</div>
		</Carousel.Root>
	</div>
{/if}
