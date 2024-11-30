<script lang="ts">
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
	}
	let {
		brn,
		title = 'Empty Title',
		author = 'Undefined Author',
		publishYear = 'Undefined Year',
		callNumber = 'Undefined Call Number',
		summary = 'Undefined Summary',
		imageLink,
		bookmarked,
		onBookMarked
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
		<div class="flex gap-2 text-slate-500">
			<User class="w-4 h-4 my-auto" />
			<p class="text-base">{author}</p>
		</div>
		<div class="flex gap-2 text-slate-500">
			<Calendar class="w-4 h-4 my-auto " />
			<p class="text-base">{publishYear}</p>
		</div>
		<div class="flex gap-2 text-slate-500">
			<AlignJustify class="w-4 h-4 my-auto" />
			<p class="text-base">{callNumber}</p>
		</div>
		<div class="flex gap-2 text-slate-500">
			<NotebookText class="w-4 h-4 my-auto basis-10" />
			<p class="text-base whitespace-pre-line basis-auto">{summary}</p>
		</div>
	</div>
</section>
