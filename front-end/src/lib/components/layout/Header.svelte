<script lang="ts">
	import type { User } from '@supabase/supabase-js';

	import { Menu, Book, Settings, LibraryBig, LogOut, LogIn, Search } from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Avatar from '$lib/components/ui/avatar';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
	import { getInitials } from '$lib/utils';

	let { user }: { user: User | null } = $props();
	let isLoggedIn: boolean = $derived(user !== null);
	let username: string = $derived(getInitials(user?.user_metadata.name || 'User'));
</script>

<header class="flex flex-row justify-between p-2 border shadow items-center">
	<a href="/">SG Lib Books</a>

	{#if isLoggedIn}
		<!-- User is logged in -->
		<!-- Desktop View -->
		<nav
			class="hidden md:flex bg-background items-center space-x-6 rounded-md border px-4 py-2 shadow"
		>
			<Button variant="ghost" href="/dashboard/library">
				<LibraryBig class="mr-2 h-4 w-4" />
				<span>Library</span>
			</Button>
			<Button variant="ghost" href="/dashboard/search">
				<Search class="mr-2 h-4 w-4" />
				<span>Search</span>
			</Button>
			<Button variant="ghost" href="/dashboard/books">
				<Book class="mr-2 h-4 w-4" />
				<span>Books</span>
			</Button>
			<!-- <Button variant="ghost" href="/dashboard/settings"> -->
			<!-- 	<Settings class="mr-2 h-4 w-4" /> -->
			<!-- 	<span>Settings</span> -->
			<!-- </Button> -->
		</nav>

		<DropdownMenu.Root>
			<DropdownMenu.Trigger>
				<Avatar.Root class="hidden md:block">
					<Avatar.Fallback>{username}</Avatar.Fallback>
				</Avatar.Root>
				<Button variant="outline" class="block md:hidden">
					<Menu class="h-4 w-4" />
				</Button>
			</DropdownMenu.Trigger>
			<DropdownMenu.Content>
				<DropdownMenu.Group>
					<div class="block md:hidden">
						<DropdownMenu.Label>Navigation</DropdownMenu.Label>
						<DropdownMenu.Item href="/dashboard/library">
							<LibraryBig class="mr-2 h-4 w-4" />
							<span>Library</span>
						</DropdownMenu.Item>
						<DropdownMenu.Item href="/dasboard/search">
							<Search class="mr-2 h-4 w-4" />
							<span>Search</span>
						</DropdownMenu.Item>
						<DropdownMenu.Item href="/dashboard/books">
							<Book class="mr-2 h-4 w-4" />
							<span>Books</span>
						</DropdownMenu.Item>
						<DropdownMenu.Separator />
					</div>

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
	{:else}
		<!-- User is not logged in -->
		<Button variant="outline" href="/auth/sign-in" class="ml-auto">
			<LogIn class="mr-2 h-4 w-4" />
			<span>Sign In</span>
		</Button>
	{/if}
</header>
