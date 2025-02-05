<script lang="ts">
	import type { Snippet } from 'svelte';
	import { Check } from 'lucide-svelte';
	let {
		children,
		selected = $bindable(),
		onclick
	}: { children: Snippet; selected: boolean; onclick: Function } = $props();
</script>

<button
	class={`w-full relative rounded-lg box-content ${selected ? 'border-2 border-blue-500' : ''}`}
	onclick={() => {
		selected = !selected;
		onclick();
	}}
>
	{@render children()}
	{#if selected}
		<div class="absolute top-2 left-2 m-1 bg-white bg-opacity-75 rounded-full p-1">
			<Check class="w-5 h-5 text-blue-500" />
		</div>
	{/if}
</button>
