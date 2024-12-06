<script lang="ts">
	import LoaderCircle from 'lucide-svelte/icons/loader-circle';
	import { type MouseEventHandler } from 'svelte/elements';
	import {
		ExternalLink,
		Calendar,
		User,
		AlignJustify,
		NotebookText,
		BookMarked,
		Bookmark
	} from 'lucide-svelte';

	interface BookProps {
		brn: number;
		title?: string;
		author?: string;
		publishYear?: string;
		callNumber?: string;
		summary?: string;
		imageLink?: string;
		bookmarked: boolean;
		onBookMarked: MouseEventHandler<HTMLButtonElement>;
		isLoading: boolean;
	}
	let {
		brn,
		title,
		author,
		publishYear,
		callNumber,
		summary,
		imageLink,
		bookmarked,
		onBookMarked,
		isLoading
	}: BookProps = $props();

	let externalLink = $derived(`https://catalogue.nlb.gov.sg/search/card?recordId=${brn}`);
</script>

<section class="flex md:flex-row flex-col gap-9">
	<div class="basis-1/5">
		<div class="bg-muted min-h-[340px] max-h-min rounded-lg">
			{#if imageLink}
				<img src={imageLink} alt={title} />
			{/if}
		</div>
	</div>
	<div class="flex flex-col basis-4/5 items-start gap-3">
		{#if isLoading}
			<div class="flex justify-center items-center w-full h-full">
				<LoaderCircle class="m-8 h-6 w-6 animate-spin" />
			</div>
		{:else}
			<div class="flex justify-between align-top w-full">
				<h1 class="text-slate-700 font-bold text-3xl">
					{title}
				</h1>
				<div class="flex gap-3 items-center">
					<a href={externalLink} target="_blank">
						<ExternalLink class="w-5 h-5" />
					</a>
					<button onclick={onBookMarked} class="block">
						{#if bookmarked}
							<BookMarked class="w-5 h-5" />
						{:else}
							<Bookmark class="w-5 h-5" />
						{/if}
					</button>
				</div>
			</div>
			{#if author}
				<div class="flex gap-2 text-slate-500">
					<User class="w-4 h-4 my-auto" />
					<p class="text-base">{author}</p>
				</div>
			{/if}
			{#if publishYear}
				<div class="flex gap-2 text-slate-500">
					<Calendar class="w-4 h-4 my-auto " />
					<p class="text-base">{publishYear}</p>
				</div>
			{/if}
			{#if callNumber}
				<div class="flex gap-2 text-slate-500">
					<AlignJustify class="w-4 h-4 my-auto" />
					<p class="text-base">{callNumber}</p>
				</div>
			{/if}
			{#if summary}
				<div class="flex gap-2 text-slate-500">
					<NotebookText class="w-4 h-4 my-auto shrink-0" />
					<p class="text-base whitespace-pre-line">{summary}</p>
				</div>
			{/if}
		{/if}
	</div>
</section>
