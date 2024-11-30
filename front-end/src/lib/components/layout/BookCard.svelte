<script lang="ts">
	import {
		ExternalLink,
		Calendar,
		User,
		AlignJustify,
		MapPin,
		BookMarked,
		Bookmark
	} from 'lucide-svelte';
	import type { BookProp } from '$lib/models';

	let {
		brn,
		title = '',
		author = '',
		publishYear = '',
		callNumber = '',
		branches = [],
		imageLink = '',
		bookmarked = false,
		onBookMarked = () => {}
	}: BookProp = $props();

	let externalLink = $derived(`https://catalogue.nlb.gov.sg/search/card?recordId=${brn}`);
	let branchesName = $derived(branches.join(', '));
</script>

<div class="rounded-lg shadow relative border-slate-400">
	<a class="bg-muted min-h-[170px]" href={`/dashboard/books/${brn}`}>
		{#if imageLink}
			<img src={imageLink} alt={title} class="rounded-t-lg" />
		{/if}
	</a>

	<button onclick={onBookMarked} class="absolute right-3 top-3 z-50 shadow">
		{#if bookmarked}
			<BookMarked class="w-5 h-5 bg-muted" />
		{:else}
			<Bookmark class="w-5 h-5 bg-muted" />
		{/if}
	</button>
	<div class="my-4 mx-3 flex flex-col gap-2 text-xs">
		<div class="flex justify-between">
			<h3
				class="text-ellipsis overflow-hidden whitespace-nowrap text-slate-700 font-semibold text-sm"
			>
				{title}
			</h3>
			<a href={externalLink} target="_blank">
				<ExternalLink class="w-4 h-4" />
			</a>
		</div>
		{#if author}
			<div class="flex gap-2 text-slate-500">
				<User class="w-4 h-4 my-auto" />
				<p class="text-ellipsis overflow-hidden whitespace-nowrap">{author}</p>
			</div>
		{/if}
		{#if publishYear}
			<div class="flex gap-2 text-slate-500">
				<Calendar class="w-4 h-4 my-auto " />
				<p class="text-ellipsis overflow-hidden whitespace-nowrap">{publishYear}</p>
			</div>
		{/if}
		{#if callNumber}
			<div class="flex gap-2 text-slate-500">
				<AlignJustify class="w-4 h-4 my-auto" />
				<p class="text-ellipsis overflow-hidden whitespace-nowrap">{callNumber}</p>
			</div>
		{/if}
		{#if branchesName}
			<div class="flex gap-2 text-slate-500">
				<MapPin class="w-6 h-4 my-auto" />
				<p class="text-ellipsis overflow-hidden whitespace-nowrap">{branchesName}</p>
			</div>
		{/if}
	</div>
</div>
