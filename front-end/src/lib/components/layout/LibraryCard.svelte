<script lang="ts">
	import type { LibraryCardProp } from '$lib/models.ts';
	import { BookCheck, Clock4, Star, StarOff } from 'lucide-svelte';

	let {
		id = '',
		name = 'Undefined Library',
		noOnLoan = 0,
		noAvail = 0,
		openingHoursDesc = 'Unknown Opening Hours',
		favourite = false,
		onFavourite = () => {},
		imageLink
	}: LibraryCardProp = $props();

	let availabilityStatus = $derived(
		[noAvail ? `${noAvail} Available` : '', noOnLoan ? `${noOnLoan} On-Loan` : ''].join(' · ')
	);
</script>

<div class="relative rounded-lg shadow border-slate-400">
	<a class="bg-muted min-h-[140px] block" href={`/dashboard/library/${id}`}>
		{#if imageLink}
			<img src={imageLink} alt={name} class="rounded-t-lg" />
		{/if}
	</a>
	<button onclick={onFavourite} class="absolute right-3 top-3 z-50 shadow">
		{#if favourite}
			<Star class="w-5 h-5 bg-muted" />
		{:else}
			<StarOff class="w-5 h-5 bg-muted" />
		{/if}
	</button>

	<div class="py-4 px-3 flex flex-col gap-2 text-xs">
		<h3
			class="text-ellipsis overflow-hidden whitespace-nowrap text-slate-700 font-semibold text-sm"
		>
			{name}
		</h3>
		<div class="flex gap-2 text-slate-500">
			<BookCheck class="w-4 h-4 my-auto" />
			<p class="">{availabilityStatus}</p>
		</div>
		<div class="flex gap-2 text-slate-500">
			<Clock4 class="w-4 h-4 my-auto " />
			<p class="">{openingHoursDesc}</p>
		</div>
	</div>
</div>
