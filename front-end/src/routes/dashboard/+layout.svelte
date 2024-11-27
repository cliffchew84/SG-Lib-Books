<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { LayoutData } from './$types';

	import Header from '$lib/components/layout/Header.svelte';
	import Footer from '$lib/components/layout/Footer.svelte';

	let { children, data }: { children: Snippet; data: LayoutData } = $props();
</script>

<Header user={data.user} />
{@render children()}
<Footer />
