<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { BellPlus, LoaderCircle } from 'lucide-svelte';

	import BookSubscriptionTabs from '$lib/components/forms/book-subscription-tabs.svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Dialog from '$lib/components/ui/dialog';
	import * as Drawer from '$lib/components/ui/drawer/index.js';
	import type BackendAPIClient from '$lib/api/client';
	import type { BookProp, LibraryProp } from '$lib/models';
	import type { BookSubscription } from '$lib/api/models';

	let {
		client,
		book,
		libraries,
		subscriptions
	}: {
		client: BackendAPIClient;
		book: BookProp;
		libraries: LibraryProp[];
		subscriptions: BookSubscription[];
	} = $props();

	let isLoading = $state(false);
	let isError = $state(false);
	let onsubmit: () => Promise<any> = $state(() => new Promise(() => {}));
	let disableNext = $state(false);
	let submitForm = $derived(async () => {
		isLoading = true;
		try {
			const results: [BookSubscription[], ...(BookSubscription | null)[]] = await onsubmit();
			const newSubscriptions = results[0];
			const removedSubscriptionIds = results.slice(1).map((sub) => {
				if (sub === null || !('id' in sub)) {
					// Skip if the subscription does not have an id
					return;
				}
				return sub.id;
			});
			// Update subscriptions state
			subscriptions = [
				...subscriptions.filter((sub) => !removedSubscriptionIds.includes(sub.id)),
				...newSubscriptions
			];
			toast.success('Subscriptions updated successfully.');
		} catch (e) {
			isError = true;
			toast.error('Failed to update subscriptions. Please try again later.');
		}
		isLoading = false;
	});
</script>

<div class="hidden md:block">
	<Dialog.Root>
		<Dialog.Trigger asChild let:builder>
			<Button class="rounded-lg w-full" builders={[builder]}>
				<BellPlus class="w-5 h-5 mr-3" />
				Subscribe Updates
			</Button>
		</Dialog.Trigger>

		<Dialog.Content class="max-w-5xl">
			<Dialog.Header>
				<Dialog.Title>Subcribe to Book Loans Updates in the following Libraries</Dialog.Title>
				<Dialog.Description
					>Get notified whenever <span class="underline">{book.title}</span> is available every morning
					in your favourite libraries.
				</Dialog.Description>
			</Dialog.Header>
			<BookSubscriptionTabs
				{book}
				{client}
				{libraries}
				{subscriptions}
				bind:disableNext
				bind:onsubmit
			/>
			<Dialog.Footer>
				<Button
					type="submit"
					disabled={isLoading || (subscriptions.length === 0 && disableNext)}
					onclick={() => {
						submitForm();
					}}
				>
					{#if isLoading}
						<LoaderCircle class="w-5 h-5 animate-spin inline mr-3" />
						Updating Changes
					{:else}
						<BellPlus class="w-5 h-5 mr-3" />
						Save Changes
					{/if}
				</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</Dialog.Root>
</div>

<div class="block md:hidden">
	<Drawer.Root>
		<Drawer.Trigger asChild let:builder>
			<Button class="rounded-lg w-full" builders={[builder]}>
				<BellPlus class="w-5 h-5 mr-3" />
				Subscribe Updates
			</Button>
		</Drawer.Trigger>
		<Drawer.Content>
			<Drawer.Header class="text-left">
				<Drawer.Title>Subcribe to Book Loans Updates in the following Libraries</Drawer.Title>
				<Drawer.Description>
					Get notified whenever your favourite book is available every morning.
				</Drawer.Description>
			</Drawer.Header>
			<BookSubscriptionTabs
				{book}
				{client}
				{libraries}
				{subscriptions}
				bind:disableNext
				bind:onsubmit
			/>
			<Drawer.Footer class="pt-2">
				<!-- <Drawer.Close asChild let:builder> -->
				<!-- 	<Button variant="outline" builders={[builder]}>Cancel</Button> -->
				<!-- </Drawer.Close> -->
				<Button
					type="submit"
					disabled={isLoading || (subscriptions.length === 0 && disableNext)}
					onclick={() => {
						submitForm();
					}}
				>
					{#if isLoading}
						<LoaderCircle class="w-5 h-5 animate-spin inline mr-3" />
						Updating Changes
					{:else}
						<BellPlus class="w-5 h-5 mr-3" />
						Save Changes
					{/if}
				</Button>
			</Drawer.Footer>
		</Drawer.Content>
	</Drawer.Root>
</div>
