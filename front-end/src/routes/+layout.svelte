<script lang="ts">
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
