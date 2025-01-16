<script lang="ts">
	import { goto } from '$app/navigation';
	import { Bell } from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
	import { ScrollArea } from '$lib/components/ui/scroll-area/index.js';
	import type { MouseEventHandler } from 'svelte/elements';

	interface Notification {
		id: number;
		title: string;
		description: string;
		date: string;
		read: boolean;
		action: MouseEventHandler<HTMLDivElement>;
	}

	let notifications: Notification[] = Array.from({ length: 50 }, (_, i) => ({
		id: i,
		title: `Notification ${i + 1}`,
		description: `Description ${i + 1}`,
		date: '2 hours ago',
		read: false,
		action: () => {
			goto('/dashboard/books');
		}
	}));

	// let { notifications }: { notifications: Notification[] } = $props();
</script>

<DropdownMenu.Root>
	<DropdownMenu.Trigger>
		<Button variant="outline" class="rounded-full p-0">
			<Bell class="h-5 w-5 mx-2" />
		</Button>
	</DropdownMenu.Trigger>
	<DropdownMenu.Content>
		<DropdownMenu.Label>Notifications</DropdownMenu.Label>
		<DropdownMenu.Separator />
		<DropdownMenu.Group>
			<ScrollArea class="h-72 w-64 rounded-md ">
				{#each notifications as notification}
					<!-- TODO: UI to show if notification is read or not -->
					<DropdownMenu.Item class="block" onclick={notification.action}>
						<div class="flex flex-col items-left justify-between gap-2">
							<div class="flex flex-col">
								<p class="text-sm font-semibold">{notification.title}</p>
								<p class="text-xs text-slate-500">{notification.description}</p>
							</div>
							<p class="text-xs text-slate-500">{notification.date}</p>
						</div>
					</DropdownMenu.Item>
				{/each}
				<!-- TODO: lazy load notifications -->
			</ScrollArea>
		</DropdownMenu.Group>
	</DropdownMenu.Content>
</DropdownMenu.Root>
