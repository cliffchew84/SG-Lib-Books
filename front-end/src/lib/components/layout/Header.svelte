<script lang="ts">
	import { toast } from 'svelte-sonner';
	import type { User } from '@supabase/supabase-js';
	import { Book, LibraryBig, LogOut, LogIn, Search } from 'lucide-svelte';

	import { goto } from '$app/navigation';
	import type BackendAPIClient from '$lib/api/client';
	import { getNotifications, readNotification } from '$lib/api/notification';
	import { Button } from '$lib/components/ui/button';
	import * as Avatar from '$lib/components/ui/avatar';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
	import NotificationDropdown from '$lib/components/layout/NotificationDropdown.svelte';
	import { getInitials } from '$lib/utils';
	import type { Notification } from '$lib/models';
	import { notificationStore } from '$lib/stores';

	let { user, client }: { user?: User | null; client?: BackendAPIClient } = $props();
	let isNotificationOpen: boolean = $state(false);
	let isLoggedIn: boolean = $derived(user != null);
	let isNotificationLoading: boolean = $state(false);
	let username: string = $derived(getInitials(user?.user_metadata.name || 'User'));
	let notifications: Notification[] = $derived(Object.values($notificationStore) as Notification[]);

	$effect(() => {
		(async () => {
			// Fetch notifications from API when menu is opened
			if (isNotificationOpen && client && notifications.length === 0) {
				isNotificationLoading = true;
				try {
					notificationStore.set(
						(await getNotifications(client)).reduce((acc, notif) => {
							acc[String(notif.id)] = {
								...notif,
								onClick: async () => {
									try {
										await readNotification(client, notif.id);
										notificationStore.update((s) => {
											s[String(notif.id)].isRead = true;
											return s;
										});
									} catch (error) {
										toast.warning('Failed to mark notification as read');
										console.error('Failed to mark notification as read', error);
									}
									goto(notif.action);
								}
							};
							return acc;
						}, {} as any)
					);
					isNotificationLoading = false;
				} catch (error) {
					isNotificationLoading = false;
					toast.warning('Failed to fetch notifications');
					console.error('Failed to fetch notifications', error);
				}
			}
		})();
	});
</script>

<header class="flex flex-row justify-between p-2 border shadow items-center min-h-14">
	<a href="/"
		>SG Lib Books
		<span class="text-[0.5em]">BETA</span>
	</a>

	{#if isLoggedIn}
		<!-- User is logged in -->
		<!-- Desktop View -->
		<nav
			class="flex bg-background items-center justify-around space-x-6 rounded-md border px-4 py-2 shadow fixed md:relative bottom-0 left-0 right-0 z-50"
		>
			<Button variant="ghost" href="/dashboard/library" class="flex items-center justify-center">
				<LibraryBig class="md:mr-2 h-4 w-4" />
				<span class="md:block hidden">Library</span>
			</Button>
			<Button variant="ghost" href="/dashboard/search" class="flex items-center justify-center">
				<Search class="md:mr-2 h-4 w-4" />
				<span class="md:block hidden">Search</span>
			</Button>
			<Button variant="ghost" href="/dashboard/books" class="flex items-center justify-center">
				<Book class="md:mr-2 h-4 w-4" />
				<span class="md:block hidden">Books</span>
			</Button>
		</nav>

		<div class="flex gap-3">
			<NotificationDropdown
				bind:menuOpen={isNotificationOpen}
				{notifications}
				isLoading={isNotificationLoading}
			/>
			<DropdownMenu.Root>
				<DropdownMenu.Trigger>
					<Avatar.Root class="block">
						<Avatar.Fallback>{username}</Avatar.Fallback>
					</Avatar.Root>
				</DropdownMenu.Trigger>
				<DropdownMenu.Content>
					<DropdownMenu.Group>
						<DropdownMenu.Label>My Account</DropdownMenu.Label>
						<DropdownMenu.Separator />
						<!-- <DropdownMenu.Item href="/dashboard/settings"> -->
						<!-- 	<Settings class="mr-2 h-4 w-4" /> -->
						<!-- 	<span>Settings</span> -->
						<!-- </DropdownMenu.Item> -->
						<DropdownMenu.Item href="/auth/sign-out">
							<LogOut class="mr-2 h-4 w-4" />
							<span>Log out</span>
						</DropdownMenu.Item>
					</DropdownMenu.Group>
				</DropdownMenu.Content>
			</DropdownMenu.Root>
		</div>
	{:else}
		<!-- User is not logged in -->
		<!-- <Button href="/auth/sign-in" class="ml-auto"> -->
		<!-- 	<LogIn class="mr-2 h-4 w-4" /> -->
		<!-- 	<span>Sign In</span> -->
		<!-- </Button> -->
	{/if}
</header>
