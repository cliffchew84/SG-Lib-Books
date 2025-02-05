<script lang="ts">
	import { Badge } from '$lib/components/ui/badge';
	import * as Tabs from '$lib/components/ui/tabs';
	import { ScrollArea } from '$lib/components/ui/scroll-area/index.js';
	import Selectable from '$lib/components/ui/selectable.svelte';
	import LibraryCard from '$lib/components/layout/LibraryCard.svelte';
	import { createSubscriptions, deleteSubscription } from '$lib/api/bookSubscription';
	import type BackendAPIClient from '$lib/api/client';
	import type { BookProp, LibraryProp } from '$lib/models.ts';
	import type { BookSubscription, BookSubscriptionCreate } from '$lib/api/models.ts';

	let {
		client,
		book,
		libraries,
		subscriptions,
		disableNext = $bindable(),
		onsubmit = $bindable()
	}: {
		client: BackendAPIClient;
		book: BookProp;
		libraries: LibraryProp[];
		disableNext: boolean;
		subscriptions: BookSubscription[];
		onsubmit: () => Promise<[BookSubscription[], ...(BookSubscription | null)[]]>;
	} = $props();

	const defaultSelectedLibraries = Array.from(
		subscriptions.reduce((set, sub) => {
			const item = book.items?.find((item) => item.ItemNo === sub.ItemNo);
			if (item !== undefined) {
				set.add(item.BranchName);
			}
			return set;
		}, new Set<string>())
	);
	let selectedLibraries: string[] = $state(defaultSelectedLibraries);
	let relatedLibraries = $state(
		libraries
			.filter((library) => library.availBooks.length > 0 || library.onLoanBooks.length > 0)
			.map((library) => ({
				...library,
				openingHoursDesc: '',
				selected: selectedLibraries.includes(library.name)
			}))
	);

	// Disable next button if no libraries are selected
	$effect(() => {
		disableNext = selectedLibraries.length === 0;
	});

	// Compute subscription changes and update onsubmit
	$effect(() => {
		onsubmit = () => {
			const newSubscriptions: BookSubscriptionCreate[] = [];
			const removedSubscriptions: BookSubscription[] = [];
			for (const item of book.items ?? []) {
				const selected = selectedLibraries.includes(item.BranchName);
				const inDefault = defaultSelectedLibraries.includes(item.BranchName);
				if (selected && !inDefault) {
					// Add new subscription
					newSubscriptions.push({
						ItemNo: item.ItemNo,
						status: 'pending',
						condition: 'book_updates_only',
						email: ''
					});
				} else if (!selected && inDefault) {
					// Remove subscription
					const sub = subscriptions.find((sub) => sub.ItemNo === item.ItemNo);
					if (sub !== undefined) {
						removedSubscriptions.push(sub);
					}
				}
			}
			return Promise.all([
				createSubscriptions(client, newSubscriptions),
				...removedSubscriptions.map((sub) => deleteSubscription(client, sub.id))
			]);
		};
	});

	const onLibrarySelect = (library: LibraryProp & { selected: boolean }) => {
		return () => {
			if (library.selected) {
				selectedLibraries = [...selectedLibraries, library.name];
			} else {
				selectedLibraries = selectedLibraries.filter((name) => name !== library.name);
			}
		};
	};
</script>

<Tabs.Root value="library" class="">
	<div class="px-4 mb-3">
		<ScrollArea class="h-24 md:h-full w-full">
			{#if selectedLibraries.length === 0}
				<span class="text-slate-500">Click on the library icon to select at least one library.</span
				>
			{/if}
			{#each selectedLibraries as libraryName}
				<Badge variant="outline" class="mx-1">{libraryName}</Badge>
			{/each}
		</ScrollArea>
	</div>
	<Tabs.Content value="library">
		<ScrollArea class="h-[500px] w-full p-4">
			<div class="grid grid-cols-2 md:grid-cols-3 md:mx-6 gap-1 md:gap-3">
				{#each relatedLibraries as library}
					<div class="w-[150px] md:w-[250px] mx-auto">
						<Selectable bind:selected={library.selected} onclick={onLibrarySelect(library)}>
							<LibraryCard {...library} disableLink={true} />
						</Selectable>
					</div>
				{/each}
			</div>
		</ScrollArea>
	</Tabs.Content>
	<!-- <Tabs.Content value="changes"> -->
	<!-- 	<div class="px-4"> -->
	<!-- 		<h3 class="my-3">Notify me when...</h3> -->
	<!-- 		<RadioGroup.Root bind:value={notificationType}> -->
	<!-- 			<div class="flex items-center space-x-3"> -->
	<!-- 				<RadioGroup.Item value="book_updates_only" /> -->
	<!-- 				<p>Book has become available.</p> -->
	<!-- 			</div> -->
	<!-- 			<div class="flex items-center space-x-3"> -->
	<!-- 				<RadioGroup.Item value="all_notif" /> -->
	<!-- 				<p>Any book status changes.</p> -->
	<!-- 			</div> -->
	<!-- 			<div class="flex items-center space-x-3"> -->
	<!-- 				<RadioGroup.Item value="no_notif" /> -->
	<!-- 				<p>Nothing</p> -->
	<!-- 			</div> -->
	<!-- 			<RadioGroup.Input name="" /> -->
	<!-- 		</RadioGroup.Root> -->
	<!-- 	</div> -->
	<!-- </Tabs.Content> -->
</Tabs.Root>
