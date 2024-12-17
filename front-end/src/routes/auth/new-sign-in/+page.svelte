<script lang="ts">
	import { goto } from '$app/navigation';
	import type { PageData } from './$types';
	import UserAddUsername from '$lib/components/forms/user-add-username.svelte';

	let { data }: { data: PageData } = $props();

	if (!data.user || !data.session || data.user?.user_metadata.name !== undefined) {
		// Redirect to dashboard if user is already logged in
		goto('/auth/sign-in');
	}
</script>

<svelte:head>
	<title>New User | SG Lib Books</title>
</svelte:head>

<div class="flex flex-col space-y-2 text-center">
	<h1 class="text-2xl font-semibold tracking-tight">Welcome to SG Lib Books</h1>
	<p class="text-muted-foreground text-sm">Welcome to SG Lib Reads {data.user?.email ?? ''}</p>
	<p class="text-muted-foreground text-sm">Please enter your username</p>
</div>
<UserAddUsername supabase={data.supabase} />
