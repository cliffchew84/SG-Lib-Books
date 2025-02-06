<script lang="ts">
	import LoaderCircle from 'lucide-svelte/icons/loader-circle';

	import { goto } from '$app/navigation';
	import { deregisterToken } from '$lib/api/notification_tokens';
	import { notificationToken } from '$lib/stores/notification';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();

	// Deregistering notification token
	$effect(() => {
		if ($notificationToken !== null && data.client !== undefined) {
			deregisterToken(data.client, $notificationToken).catch((error) => {
				console.error(error);
			});
		}
	});

	// Signing-out using supabase

	$effect(() => {
		data.supabase.auth
			.signOut()
			.then(() => {
				goto('/');
			})
			.catch((error) => {
				console.error(error);
				goto('/');
			});
	});
</script>

<svelte:head>
	<title>Sign Out | SG Lib Books</title>
</svelte:head>

<div class="flex flex-col space-y-2 text-center">
	<h1 class="text-2xl font-semibold tracking-tight">Signing Out</h1>
	<p class="text-muted-foreground text-sm">
		Signing-out of your account
		<LoaderCircle class="ml-2 h-4 w-4 animate-spin inline" />
	</p>
</div>
