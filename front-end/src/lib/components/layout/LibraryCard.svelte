<script lang="ts">
	import type { LibraryProp } from '$lib/models.ts';
	import { BookCheck, Clock4, Star, StarOff } from 'lucide-svelte';

	let {
		name = 'Undefined Library',
		onLoanBooks = [],
		availBooks = [],
		openingHoursDesc = 'Unknown Opening Hours',
		favourite = false,
		onFavourite = () => {},
		imageLink,
		disableLink = false
	}: LibraryProp & { disableLink: boolean } = $props();

	let noAvail = $derived(availBooks.length);
	let noOnLoan = $derived(onLoanBooks.length);

	let availabilityStatus = $derived(
		noAvail > 0 || noOnLoan > 0
			? [noAvail ? `${noAvail} Available` : undefined, noOnLoan ? `${noOnLoan} On-Loan` : undefined]
					.filter((v) => v)
					.join(' · ')
			: 'No related books'
	);
</script>

<div class="relative rounded-lg shadow border-slate-400 w-full">
	<a
		class="bg-muted md:min-h-[140px] max-h-[200px] w-full block overflow-hidden rounded-t-lg"
		href={!disableLink ? `/dashboard/library/${name}` : ''}
	>
		{#if imageLink}
			<img src={imageLink} alt={name} class="rounded-t-lg aspect-[3/2] h-fit w-fit object-cover" />
		{/if}
	</a>
	<button
		onclick={!disableLink ? onFavourite : () => {}}
		class="absolute right-3 top-3 z-10 shadow"
	>
		{#if favourite}
			<Star class="w-5 h-5 bg-muted" />
		{:else}
			<StarOff class="w-5 h-5 bg-muted" />
		{/if}
	</button>

	<div class="py-4 px-3 flex flex-col gap-2 text-xs">
		<h3
			class="text-ellipsis overflow-hidden whitespace-nowrap text-slate-700 font-semibold text-sm text-left"
		>
			{name}
		</h3>
		<div class="flex gap-2 text-slate-500">
			<BookCheck class="w-4 h-4 my-auto" />
			<p class="">{availabilityStatus}</p>
		</div>
		{#if openingHoursDesc}
			<div class="flex gap-2 text-slate-500">
				<Clock4 class="w-4 h-4 my-auto " />
				<p class="">{openingHoursDesc}</p>
			</div>
		{/if}
	</div>
</div>
