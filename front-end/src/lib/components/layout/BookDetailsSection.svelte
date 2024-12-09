<script lang="ts">
	import {
		ExternalLink,
		Calendar,
		User,
		AlignJustify,
		NotebookText,
		BookMarked,
		Bookmark,
		LoaderCircle
	} from 'lucide-svelte';

	import { Skeleton } from '$lib/components/ui/skeleton';
	import type { BookProp } from '$lib/models';

	let { book, isLoading }: { book: BookProp; isLoading: boolean } = $props();

	let externalLink = $derived(`https://catalogue.nlb.gov.sg/search/card?recordId=${book.brn}`);
</script>

<section class="flex md:flex-row flex-col gap-9">
	<div class="basis-1/5">
		<div class="bg-muted min-h-[340px] max-h-min rounded-lg">
			{#if book.imageLink}
				<img src={book.imageLink} alt={book.title} />
			{/if}
		</div>
	</div>
	<div class="flex flex-col basis-4/5 items-start gap-3">
		{#if isLoading}
			<Skeleton class="h-10 w-full rounded-full" />
		{:else}
			<div class="flex justify-between align-top w-full">
				<h1 class="text-slate-700 font-bold text-3xl">
					{book.title}
				</h1>
				<div class="flex gap-3 items-center">
					<a href={externalLink} target="_blank">
						<ExternalLink class="w-5 h-5" />
					</a>
					<button onclick={book.onBookMarked} class="block">
						{#if book.bookMarkLoading}
							<LoaderCircle class="w-5 h-5 animate-spin" />
						{:else if book.bookmarked}
							<BookMarked class="w-5 h-5" />
						{:else}
							<Bookmark class="w-5 h-5" />
						{/if}
					</button>
				</div>
			</div>
		{/if}

		{#if isLoading}
			<div class="flex gap-2 text-slate-500">
				<Skeleton class="w-8 h-8 rounded-full" />
				<Skeleton class="h-8 w-72 rounded-full" />
			</div>
			<div class="flex gap-2 text-slate-500">
				<Skeleton class="w-8 h-8 rounded-full" />
				<Skeleton class="h-8 w-72 rounded-full" />
			</div>
			<div class="flex gap-2 text-slate-500">
				<Skeleton class="w-8 h-8 rounded-full" />
				<Skeleton class="h-8 w-72 rounded-full" />
			</div>
			<div class="flex gap-2 text-slate-500">
				<Skeleton class="w-8 h-8 rounded-full" />
				<Skeleton class="h-8 w-72 rounded-full" />
			</div>
		{:else}
			{#if book.author}
				<div class="flex gap-2 text-slate-500">
					<User class="w-4 h-4 my-auto" />
					<p class="text-base">{book.author}</p>
				</div>
			{/if}
			{#if book.publishYear}
				<div class="flex gap-2 text-slate-500">
					<Calendar class="w-4 h-4 my-auto " />
					<p class="text-base">{book.publishYear}</p>
				</div>
			{/if}
			{#if book.callNumber}
				<div class="flex gap-2 text-slate-500">
					<AlignJustify class="w-4 h-4 my-auto" />
					<p class="text-base">{book.callNumber}</p>
				</div>
			{/if}
			{#if book.summary}
				<div class="flex gap-2 text-slate-500">
					<NotebookText class="w-4 h-4 my-auto shrink-0" />
					<p class="text-base whitespace-pre-line">{book.summary}</p>
				</div>
			{/if}
		{/if}
	</div>
</section>
