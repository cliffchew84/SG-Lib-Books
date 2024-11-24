<script lang="ts">
	import '../app.css';
	import Header from '$lib/components/layout/Header.svelte';
	let { children } = $props();
</script>

<Header />
{@render children()}
