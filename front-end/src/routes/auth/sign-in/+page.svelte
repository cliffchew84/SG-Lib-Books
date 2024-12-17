<script lang="ts">
	import { goto } from '$app/navigation';
	import type { PageData } from './$types';
	import UserAuthForm from '$lib/components/forms/user-auth-form.svelte';

	let { data }: { data: PageData } = $props();
	if (data.session) {
		// Redirect to dashboard if user is already logged in
		goto('/dashboard');
	}
</script>

<svelte:head>
	<title>Sign In | SG Lib Books</title>
</svelte:head>

<div class="flex flex-col space-y-2 text-center">
	<h1 class="text-2xl font-semibold tracking-tight">Sign In</h1>
	<p class="text-muted-foreground text-sm">Sign-in to your account</p>
</div>
<UserAuthForm class={undefined} supabase={data.supabase} />
