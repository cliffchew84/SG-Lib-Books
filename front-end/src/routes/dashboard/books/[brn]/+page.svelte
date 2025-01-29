<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { page } from '$app/stores';

	import Button from '$lib/components/ui/button/button.svelte';
	import BookDetailsSection from '$lib/components/layout/BookDetailsSection.svelte';
	import LibraryCarousel from '$lib/components/layout/LibraryCarousel.svelte';

	import { favouriteLibrary, unfavouriteLibrary } from '$lib/api/library';
	import type { BookAvail } from '$lib/api/models';
	import type { BookProp, Library, LibraryProp } from '$lib/models';
	import { bookStore, libraryAPIStore } from '$lib/stores';
	import { bookmarkBook } from '$lib/stores/book';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
	const brn = Number($page.params.brn);

	let isLoading = $state(true);
	let isError = $state(false);
	let book: BookProp = $state({
		brn: brn,
		bookmarked: $bookStore[brn]?.bookmarked ?? false,
		bookMarkLoading: false,
		onBookMarked: async () => {
			book.bookMarkLoading = true;
			await bookmarkBook(data.client, book.brn);
			book.bookMarkLoading = false;
		}
	});

	let librariresProps: LibraryProp[] = $state([]);
	let librariesFavourite: LibraryProp[] = $derived(
		librariresProps.filter((lib) => {
			return lib.favourite;
		})
	);
	let librariesAvail: LibraryProp[] = $derived(
		librariresProps.filter((lib) => {
			return lib.availBooks.length >= 1 && !lib.favourite;
		})
	);
	let librariesOnLoan: LibraryProp[] = $derived(
		librariresProps.filter((lib) => {
			return lib.onLoanBooks.length > 0 && lib.availBooks.length == 0 && !lib.favourite;
		})
	);

	// Compute bookmarked based on bookStore update
	$effect(() => {
		book.bookmarked = $bookStore[brn]?.bookmarked ?? false;
	});

	$effect(() => {
		(async () => {
			try {
				// Await backend API response
				const bookAPI = await data.bookResponse;
				isLoading = false;
				// Update front-end states
				book = {
					title: bookAPI.TitleName,
					author: bookAPI.Author,
					publishYear: bookAPI.PublishYear,
					callNumber:
						bookAPI.avails && bookAPI.avails.length > 0 ? bookAPI.avails[0].CallNumber : undefined,
					imageLink: bookAPI.cover_url,
					summary: bookAPI.summary,
					items: bookAPI.avails,
					...book
				};
			} catch (error) {
				isError = true;
			}
		})();
	});

	$effect(() => {
		// Compute library availability state
		const libraries: { [key: string]: Library } = $libraryAPIStore;
		const branchAvail: { [key: string]: BookAvail[] } = {};
		// Reset onLoanBook and availBook state
		Object.keys(libraries).map((k) => {
			libraries[k].onLoanBooks = [];
			libraries[k].availBooks = [];
		});
		book.items?.map((avail) => {
			if (branchAvail.hasOwnProperty(avail.BranchName)) {
				branchAvail[avail.BranchName].push(avail);
			} else {
				branchAvail[avail.BranchName] = [avail];
			}
		});
		for (const [k, bookAvails] of Object.entries(branchAvail)) {
			for (let bookAvail of bookAvails) {
				if (!libraries.hasOwnProperty(k)) {
					console.warn(`Library ${k} does not exist in database`);
					continue;
				}
				if (bookAvail.StatusDesc == 'On Loan') {
					libraries[k].onLoanBooks.push({ ...book, dueDate: `Due ${bookAvail.DueDate}` });
				} else {
					libraries[k].availBooks.push(book);
				}
			}
		}
		librariresProps = Object.values(libraries).map((lib) => {
			return {
				...lib,
				onFavourite: async () => {
					try {
						if (lib.favourite) {
							console.log('unlike library');
							await unfavouriteLibrary(data.client, lib.name);
							toast.success(`${lib.name} is removed from your favourites`);
						} else {
							console.log('like library');
							await favouriteLibrary(data.client, lib.name);
							toast.success(`${lib.name} is added to your favourites`);
						}
						libraryAPIStore.update((s) => {
							s[lib.name].favourite = !s[lib.name].favourite;
							return s;
						});
					} catch (error) {
						if (error instanceof Error) {
							if (error.cause === 429) {
								toast.warning("We are hitting NLB's API too hard. Please try again later.");
							} else {
								toast.warning('Library favourite request has failed. Please try again later.');
							}
						}
						console.error('Favourite/unfavourite error:', error);
					}
				}
			};
		});
	});
</script>

<svelte:head>
	{#if isError}
		<title>Something Went Wrong | SG Lib Books</title>
	{:else}
		<title>{book.title} | SG Lib Books</title>
	{/if}
</svelte:head>

<main class="container flex flex-col gap-8 p-8 min-h-[85vh]">
	{#if !isError}
		<BookDetailsSection {book} {isLoading} />
		{#if librariesFavourite.length > 0}
			<LibraryCarousel
				title="Your Favourite"
				description="Libraries marked as favourite by you."
				libraries={librariesFavourite}
			/>
		{/if}
		<LibraryCarousel
			title="On-Shelf"
			description="Libraries with books available to be borrowed."
			libraries={librariesAvail}
		/>
		<LibraryCarousel
			title="On-Loaned"
			description="Libraries with all books on-loaned to fellow readers."
			libraries={librariesOnLoan}
		/>
	{:else}
		<div class="flex flex-col gap-3">
			<h1 class="text-4xl font-bold text-slate-700">404: Book Not Found</h1>
			<p class="text-sm text-slate-500">
				The book that you have requested does not exist on NLB's Catalogue
			</p>
			<Button
				onclick={() => {
					history.back();
				}}>Back to Search Results</Button
			>
		</div>
	{/if}
</main>
