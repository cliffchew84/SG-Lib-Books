<script lang="ts">
	import type { LibraryProp } from '$lib/models.ts';
	import { BookCheck, Clock4, Star, StarOff, MapPin } from 'lucide-svelte';

	let {
		id = '',
		name = 'Undefined Library',
		noOnLoan = 0,
		noAvail = 0,
		openingHoursDesc = 'Unknown Opening Hours',
		location = 'This is a long long long address\nThis is a long long long address\n',
		favourite = false,
		onFavourite = () => {},
		imageLink
	}: LibraryProp = $props();

	let availabilityStatus = $derived(
		[noAvail ? `${noAvail} Available` : '', noOnLoan ? `${noOnLoan} On-Loan` : ''].join(' · ')
	);
</script>

<section class="">
	<div class="bg-muted min-h-[140px] block">
		{#if imageLink}
			<img src={imageLink} alt={name} class="rounded-t-lg" />
		{/if}
	</div>

	<div class="py-6 flex flex-col gap-6">
		<div class="flex justify-start gap-3">
			<h1 class="text-slate-700 font-bold text-3xl">{name}</h1>
			<button onclick={onFavourite} class="">
				{#if favourite}
					<Star class="w-5 h-5 " />
				{:else}
					<StarOff class="w-5 h-5 " />
				{/if}
			</button>
		</div>
		<div class="grid md:grid-cols-2 grid-cols-1">
			<div class="flex gap-2 text-slate-600 items-center">
				<p class="flex text-slate-700 font-semibold">
					<MapPin class="w-4 h-4 mr-2 my-auto " />
					Location:
				</p>
				<p class=" whitespace-pre-line">{location}</p>
			</div>
			<div class="flex flex-col gap-3">
				<div class="flex gap-2 text-slate-600 items-center">
					<p class="flex text-slate-700 font-semibold">
						<Clock4 class="w-4 h-4 mr-2 my-auto " />
						Opening Hours:
					</p>
					<p class="">{openingHoursDesc}</p>
				</div>
				<div class="flex gap-2 text-slate-600 items-center">
					<p class="flex text-slate-700 font-semibold">
						<BookCheck class="w-4 h-4 mr-2 my-auto" />
						Book Availability:
					</p>
					<p class="">{availabilityStatus}</p>
				</div>
			</div>
		</div>
	</div>
</section>
