<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { LayoutData } from './$types';

	import Header from '$lib/components/layout/Header.svelte';
	import Footer from '$lib/components/layout/Footer.svelte';
	import { isLoading, bookStore } from '$lib/stores';
	import { getBooks } from '$lib/api/book';
	import { getLibraries } from '$lib/api/library';
	import type { BookResponse, BookAvail } from '$lib/api/models';

	let { children, data }: { children: Snippet; data: LayoutData } = $props();

	// Get all user's favourite books
	$effect(() => {
		(async () => {
			const apiResponseBook = await getBooks(data.client);
			const apiResponseLibrary = await getLibraries(data.client);
			isLoading.set(false);
			console.log(apiResponseLibrary);
			bookStore.set(
				Object.fromEntries(
					apiResponseBook.map((book: BookResponse) => {
						let branchAvail: { [key: string]: BookAvail[] } = {};
						book.avails.map((avail) => {
							if (branchAvail.hasOwnProperty(avail.BranchName)) {
								branchAvail[avail.BranchName].push(avail);
							} else {
								branchAvail[avail.BranchName] = [avail];
							}
						});
						return [
							book.BID,
							{
								brn: book.BID,
								title: book.TitleName,
								author: book.Author,
								publishYear: book.PublishYear,
								callNumber:
									book.avails && book.avails.length > 0 ? book.avails[0].CallNumber : undefined,
								imageLink: book.cover_url,
								summary: book.summary,
								bookmarked: true,
								branches: Object.keys(branchAvail),
								items: book.avails
							}
						];
					})
				)
			);
		})();
	});
</script>

<Header user={data.user} />
{@render children()}
<Footer />
