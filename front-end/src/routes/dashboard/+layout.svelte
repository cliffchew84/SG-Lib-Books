<script lang="ts">
	import type { Snippet } from 'svelte';
	import { toast } from 'svelte-sonner';
	import type { LayoutData } from './$types';

	import Header from '$lib/components/layout/Header.svelte';
	import Footer from '$lib/components/layout/Footer.svelte';
	import { Toaster } from '$lib/components/ui/sonner';
	import { isLoading } from '$lib/stores';
	import { fetchBooks } from '$lib/stores/book';
	import { fetchLibraries } from '$lib/stores/library';

	let { children, data }: { children: Snippet; data: LayoutData } = $props();

	// Get all user's favourite books
	$effect(() => {
		(async () => {
			try {
				await fetchLibraries(data.client);
				await fetchBooks(data.client);
				isLoading.set(false);
			} catch (error) {
				toast.warning('Failed to fetch new notifications');
			}
		})();
	});
</script>

<Toaster />

<Header user={data.user} client={data.client} />

{@render children()}
<Footer />
