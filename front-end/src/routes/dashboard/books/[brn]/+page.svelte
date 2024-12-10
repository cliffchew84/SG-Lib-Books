<script lang="ts">
	import { page } from '$app/stores';

	import Button from '$lib/components/ui/button/button.svelte';
	import BookDetailsSection from '$lib/components/layout/BookDetailsSection.svelte';
	import LibraryCarousel from '$lib/components/layout/LibraryCarousel.svelte';

	import { likeBook, unlikeBook } from '$lib/api/book';
	import { favouriteLibrary, unfavouriteLibrary } from '$lib/api/library';
	import type { BookAvail } from '$lib/api/models';
	import type { BookProp, Library, LibraryProp } from '$lib/models';
	import { bookStore, libraryAPIStore } from '$lib/stores';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
	const brn = Number($page.params.brn);

	let isLoading = $state(true);
	let isError = $state(false);
	let book: BookProp = $state({
		brn: brn,
		bookmarked: $bookStore.hasOwnProperty($page.params.brn),
		bookMarkLoading: false,
		onBookMarked: async () => {
			book.bookMarkLoading = true;
			try {
				if ($bookStore.hasOwnProperty(brn)) {
					console.log('Unbookmark book', brn);
					await unlikeBook(data.client, brn);
					bookStore.update((s) => {
						delete s[brn];
						return s;
					});
				} else {
					console.log('bookmark book', brn);
					await likeBook(data.client, brn);
					bookStore.update((s) => {
						s[brn] = { ...book, bookmarked: true };
						return s;
					});
				}
				book.bookMarkLoading = false;
				book.bookmarked = !book.bookmarked;
			} catch (error) {
				console.error('Bookmark/Unbookmark error:', error);
				book.bookMarkLoading = false;
			}
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
			return lib.availBooks.length >= 1;
		})
	);
	let librariesOnLoan: LibraryProp[] = $derived(
		librariresProps.filter((lib) => {
			return lib.availBooks.length == 0;
		})
	);

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
		const libraries: { [key: string]: Library } = {};
		const branchAvail: { [key: string]: BookAvail[] } = {};
		(book.items ?? []).map((avail) => {
			if (branchAvail.hasOwnProperty(avail.BranchName)) {
				branchAvail[avail.BranchName].push(avail);
			} else {
				branchAvail[avail.BranchName] = [avail];
			}
		});
		for (const [k, bookAvails] of Object.entries(branchAvail)) {
			const onLoanBooks = [];
			const availBooks = [];
			for (let bookAvail of bookAvails) {
				if (bookAvail.StatusDesc == 'On Loan') {
					onLoanBooks.push(book);
				} else {
					availBooks.push(book);
				}
			}
			if (libraries.hasOwnProperty(k)) {
				libraries[k].onLoanBooks.concat(onLoanBooks);
				libraries[k].availBooks.concat(availBooks);
			} else {
				if ($libraryAPIStore.hasOwnProperty(k)) {
					libraries[k] = {
						name: k,
						favourite: $libraryAPIStore[k].favourite,
						location: $libraryAPIStore[k].location,
						openingHoursDesc: $libraryAPIStore[k].openingHoursDesc,
						imageLink: $libraryAPIStore[k].imageLink,
						onLoanBooks,
						availBooks
					};
				}
			}
			librariresProps = Object.values(libraries).map((lib) => {
				return {
					...lib,
					onFavourite: async () => {
						if (lib.favourite) {
							console.log('unlike library');
							await unfavouriteLibrary(data.client, lib.name);
						} else {
							console.log('like library');
							await favouriteLibrary(data.client, lib.name);
						}
						libraryAPIStore.update((s) => {
							s[lib.name].favourite = !s[lib.name].favourite;
							return s;
						});
					}
				};
			});
		}
	});
</script>

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
