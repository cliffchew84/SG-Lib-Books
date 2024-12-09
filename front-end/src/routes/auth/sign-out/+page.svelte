<script lang="ts">
	import { goto } from '$app/navigation';
	import type { PageData } from './$types';

	import LoaderCircle from 'lucide-svelte/icons/loader-circle';

	let { data }: { data: PageData } = $props();

	// Signing-out using supabase
	data.supabase.auth
		.signOut()
		.then(() => {
			goto('/');
		})
		.catch((error) => {
			console.error(error);
			goto('/');
		});
</script>

<div class="flex flex-col space-y-2 text-center">
	<h1 class="text-2xl font-semibold tracking-tight">Signing Out</h1>
	<p class="text-muted-foreground text-sm">
		Signing-out of your account
		<LoaderCircle class="ml-2 h-4 w-4 animate-spin inline" />
	</p>
</div>
