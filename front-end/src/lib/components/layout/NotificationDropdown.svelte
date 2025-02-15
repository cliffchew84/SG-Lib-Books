<script lang="ts">
	import { type MouseEventHandler } from 'svelte/elements';
	import { Bell, LoaderCircle } from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
	import { ScrollArea } from '$lib/components/ui/scroll-area/index.js';
	import type { Notification } from '$lib/models';

	let {
		notifications = [],
		isLoading = false,
		menuOpen = $bindable(),
		selectAll = () => {}
	}: {
		notifications: Notification[];
		isLoading: boolean;
		menuOpen: boolean;
		selectAll: MouseEventHandler<HTMLButtonElement>;
	} = $props();

	let unreadCount = $derived(notifications.filter((notification) => !notification.isRead).length);
</script>

<DropdownMenu.Root>
	<DropdownMenu.Trigger asChild let:builder>
		<Button
			variant="outline"
			builders={[builder]}
			onclick={() => {
				menuOpen = !menuOpen;
			}}
			class="rounded-full p-0 relative"
		>
			<Bell class="h-5 w-5 mx-2" />
			{#if unreadCount > 0}
				<div
					class="absolute -top-1 -right-1 w-5 h-5 z-20 rounded-full bg-red-500 text-xs text-white"
				>
					{unreadCount > 99 ? '99+' : unreadCount}
				</div>
			{/if}
		</Button>
	</DropdownMenu.Trigger>
	<DropdownMenu.Content>
		<DropdownMenu.Label class="flex justify-between items-center">
			<p>Notifications</p>
			<Button variant="ghost" onclick={selectAll} disabled={unreadCount == 0}>Read All</Button>
		</DropdownMenu.Label>
		<DropdownMenu.Separator />
		<DropdownMenu.Group>
			<ScrollArea class="h-96 w-72 rounded-md ">
				{#if isLoading}
					<div class="flex justify-center items-center">
						<LoaderCircle class="m-8 h-6 w-6 animate-spin" />
					</div>
				{:else if notifications.length === 0}
					<div class="flex items-center justify-center">
						<p class="text-center text-slate-500">No notifications</p>
					</div>
				{:else}
					{#each notifications as notification}
						<DropdownMenu.Item class="flex gap-1" onclick={notification.onClick}>
							<div
								class="w-1 h-1 rounded-full my-5 {!notification.isRead ? 'bg-slate-500' : ''}"
							></div>
							<div class="flex flex-col items-left justify-between gap-2">
								<div class="flex flex-col">
									<p class="text-sm font-semibold">{notification.title}</p>
									<p class="text-xs text-slate-500">{notification.description}</p>
								</div>
								<p class="text-xs text-slate-500">{notification.createdAt}</p>
							</div>
						</DropdownMenu.Item>
					{/each}
				{/if}
			</ScrollArea>
		</DropdownMenu.Group>
	</DropdownMenu.Content>
</DropdownMenu.Root>
