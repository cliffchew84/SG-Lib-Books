<script lang="ts">
	import { goto } from '$app/navigation';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
	if (data.session) {
		// Redirect to dashboard if user is already logged in
		goto('/dashboard');
	}
</script>

<div class="flex flex-col space-y-2 text-center">
	<h1 class="text-2xl font-semibold tracking-tight">Email Confirmation</h1>
	<p class="text-muted-foreground text-sm">
		An email is sent to your inbox. Follow the link to login.
	</p>
</div>
