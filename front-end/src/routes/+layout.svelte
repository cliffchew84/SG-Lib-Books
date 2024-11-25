<script lang="ts">
	import { onMount, type Snippet } from 'svelte';
	import { invalidate } from '$app/navigation';
	import type { LayoutData } from './$types';
	import '../app.css';

	let { children, data: loadData }: { children: Snippet; data: LayoutData } = $props();

	onMount(() => {
		const { data } = loadData.supabase.auth.onAuthStateChange((_, newSession) => {
			if (newSession?.expires_at !== loadData.session?.expires_at) {
				invalidate('supabase:auth');
			}
		});

		return () => data.subscription.unsubscribe();
	});
</script>

{@render children()}
