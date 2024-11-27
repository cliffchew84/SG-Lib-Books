<script lang="ts">
	import type { Snippet } from 'svelte';

	let {
		children,
		title = '',
		description = ''
	}: { children: Snippet; title: String; description: String } = $props();
</script>

<main class="container flex flex-col gap-8 p-8">
	<div class="flex flex-col gap-3">
		<h1 class="text-4xl font-bold text-slate-700">{title}</h1>
		<p class="text-sm text-slate-500">{description}</p>
	</div>
	{@render children()}
</main>
