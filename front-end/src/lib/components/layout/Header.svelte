<script lang="ts">
	import { Menu, Book, Settings, LibraryBig, LogOut, LogIn, Search } from 'lucide-svelte';

	import { Button } from '$lib/components/ui/button';
	import * as Avatar from '$lib/components/ui/avatar';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';

	let { isLoggedIn = true } = $props();
</script>

<header class="flex flex-row justify-between p-2 border shadow items-center">
	<a href="/">SG Lib Books</a>

	{#if isLoggedIn}
		<!-- User is logged in -->
		<!-- Desktop View -->
		<nav
			class="hidden md:flex bg-background items-center space-x-6 rounded-md border px-4 py-2 shadow"
		>
			<Button variant="ghost" href="/library">
				<LibraryBig class="mr-2 h-4 w-4" />
				<span>Library</span>
			</Button>
			<Button variant="ghost" href="/search">
				<Search class="mr-2 h-4 w-4" />
				<span>Search</span>
			</Button>
			<Button variant="ghost" href="/books">
				<Book class="mr-2 h-4 w-4" />
				<span>Books</span>
			</Button>
			<Button variant="ghost" href="/settings">
				<Settings class="mr-2 h-4 w-4" />
				<span>Settings</span>
			</Button>
		</nav>

		<DropdownMenu.Root>
			<DropdownMenu.Trigger>
				<Avatar.Root class="hidden md:block">
					<Avatar.Fallback>CN</Avatar.Fallback>
				</Avatar.Root>
				<Button variant="outline" class="block md:hidden">
					<Menu class="h-4 w-4" />
				</Button>
			</DropdownMenu.Trigger>
			<DropdownMenu.Content>
				<DropdownMenu.Group>
					<div class="block md:hidden">
						<DropdownMenu.Label>Navigation</DropdownMenu.Label>
						<DropdownMenu.Item href="/library">
							<LibraryBig class="mr-2 h-4 w-4" />
							<span>Library</span>
						</DropdownMenu.Item>
						<DropdownMenu.Item href="/search">
							<Search class="mr-2 h-4 w-4" />
							<span>Search</span>
						</DropdownMenu.Item>
						<DropdownMenu.Item href="/books">
							<Book class="mr-2 h-4 w-4" />
							<span>Books</span>
						</DropdownMenu.Item>
						<DropdownMenu.Separator />
					</div>

					<DropdownMenu.Label>My Account</DropdownMenu.Label>
					<DropdownMenu.Separator />
					<DropdownMenu.Item href="/settings">
						<Settings class="mr-2 h-4 w-4" />
						<span>Settings</span>
					</DropdownMenu.Item>
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
