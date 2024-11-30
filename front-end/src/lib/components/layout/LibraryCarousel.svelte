<script lang="ts">
	import * as Carousel from '$lib/components/ui/carousel/index.js';
	import LibraryCard from '$lib/components/layout/LibraryCard.svelte';
	import type { Library } from '$lib/models.ts';

	let {
		title = '',
		description = '',
		libraries = []
	}: {
		title: String;
		description: String;
		libraries: Library[];
	} = $props();
</script>

{#if libraries.length !== 0}
	<div class="flex flex-col gap-3">
		<h1 class="text-4xl font-bold text-slate-700">{title}</h1>
		<p class="text-sm text-slate-500">{description}</p>

		<Carousel.Root>
			<Carousel.Content>
				{#each libraries as library}
					<Carousel.Item class="md:basis-1/2 lg:basis-1/4 my-3">
						<LibraryCard {...library} onFavourite={() => {}} />
					</Carousel.Item>
				{/each}
			</Carousel.Content>
			<Carousel.Previous />
			<Carousel.Next />
		</Carousel.Root>
	</div>
{/if}
