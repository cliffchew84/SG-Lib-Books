<script lang="ts">
	import { Book, LibraryBig, Search } from 'lucide-svelte';
	import { toast } from 'svelte-sonner';

	import { Button } from '$lib/components/ui/button';
	import TitledPage from '$lib/components/layout/TitledPage.svelte';
	import LibraryCarousel from '$lib/components/layout/LibraryCarousel.svelte';

	import { favouriteLibrary, unfavouriteLibrary } from '$lib/api/library';
	import type { LibraryProp } from '$lib/models';
	import { libraryStore, libraryAPIStore } from '$lib/stores';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	let librariresProps: LibraryProp[] = $derived(
		Object.values($libraryStore).map((lib) => {
			return {
				...lib,
				onFavourite: async () => {
					try {
						if (lib.favourite) {
							await unfavouriteLibrary(data.client, lib.name);
							toast.success(`${lib.name} is removed from your favourites`);
						} else {
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
		})
	);
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
			return lib.availBooks.length == 0 && !lib.favourite;
		})
	);
</script>

<TitledPage
	title="Library"
	description="Checkout your favourite books in every library operated by NLB."
>
	{#if librariesAvail.length === 0 && librariesOnLoan.length === 0}
		<div>
			<h3 class="font-semibold text-slate-800">You have your account now. What's next?</h3>
			<ul class="list-disc list-inside text-slate-800">
				<li class="">
					<p class="inline">
						Search your favourite library books at
						<Button variant="ghost" href="/dashboard/search">
							<Search class="mr-2 h-4 w-4" />
							<span>Search</span>
						</Button>
					</p>
				</li>
				<li class="">
					<p class="inline">
						View your saved books in
						<Button variant="ghost" href="/dashboard/books">
							<Book class="mr-2 h-4 w-4" />
							<span>Books</span>
						</Button>
					</p>
				</li>
				<li class="">
					<p class="inline">
						View your book availabilities in
						<Button variant="ghost" href="/dashboard/library">
							<LibraryBig class="mr-2 h-4 w-4" />
							<span>Library</span>
						</Button>
					</p>
				</li>
				<li class="mt-3">
					<p class="inline">More features will be added so do keep a lookout</p>
				</li>
				<li class="mt-3">
					<p class="inline">
						To provide any feedback, email me at <a
							class="underline"
							href="mailto:sglibreads@gmail.com">sglibreads@gmail.com</a
						>
					</p>
				</li>
			</ul>
		</div>
	{:else}
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
	{/if}
</TitledPage>
