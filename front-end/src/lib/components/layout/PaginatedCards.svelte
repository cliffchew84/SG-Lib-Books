<script lang="ts">
	import * as Pagination from '$lib/components/ui/pagination';
	import BookCard from '$lib/components/layout/BookCard.svelte';
	import type { Book } from '$lib/models';

	let { books = [], perPage = 25 }: { books: Book[]; perPage: number } = $props();
	let page = $state(0); // Current page number
	let count = $derived(books.length); // Total items
	let filteredBooks = $derived(books.slice(page * perPage, Math.min((page + 1) * perPage, count))); // Slice of books based on page changes
</script>

<section class="flex flex-col gap-3">
	<div class="grid md:grid-cols-5 sm:grid-cols-3 grid-cols-1 gap-3">
		{#each filteredBooks as book}
			<BookCard {...book} onBookMarked={() => {}} />
		{/each}
	</div>
	<Pagination.Root {count} {perPage} bind:page let:pages let:currentPage>
		<Pagination.Content>
			<Pagination.Item>
				<Pagination.PrevButton />
			</Pagination.Item>
			{#each pages as page (page.key)}
				{#if page.type === 'ellipsis'}
					<Pagination.Item>
						<Pagination.Ellipsis />
					</Pagination.Item>
				{:else}
					<Pagination.Item isVisible={currentPage == page.value}>
						<Pagination.Link {page} isActive={currentPage == page.value}>
							{page.value}
						</Pagination.Link>
					</Pagination.Item>
				{/if}
			{/each}
			<Pagination.Item>
				<Pagination.NextButton />
			</Pagination.Item>
		</Pagination.Content>
	</Pagination.Root>
</section>
