<script lang="ts">
	import LoaderCircle from 'lucide-svelte/icons/loader-circle';
	import { goto } from '$app/navigation';
	import { isLoading } from '$lib/stores';

	$effect(() => {
		if (!$isLoading) {
			goto('/dashboard/library');
		}
	});
</script>

<svelte:head>
	<title>Welcome | SG Lib Books</title>
</svelte:head>

<main class="flex flex-1 flex-col items-center justify-center min-h-[85vh] bg-background px-4 py-8">
	<div
		class="w-full max-w-lg rounded-2xl border border-border bg-card shadow-lg p-8 flex flex-col items-center gap-6"
	>
		<h1 class="text-3xl md:text-4xl font-bold text-slate-800 text-center">
			Welcome to SG Lib Books
		</h1>
		<p class="text-slate-600 text-center">
			<span class="font-semibold">Just a moment…</span> <br />
			Our service is starting up and you'll be redirected soon.
		</p>
		<div class="flex flex-col items-center justify-center mt-2" aria-busy="true" aria-live="polite">
			<LoaderCircle class="m-4 h-10 w-10 animate-spin" />
			<span class="sr-only">Loading…</span>
		</div>
		<button
			class="mt-2 text-slate-500 hover:underline text-xs font-medium transition-colors"
			onclick={() => location.reload()}
		>
			Not redirected yet? <span class="font-semibold">Retry</span>
		</button>
		<details class="mt-2 text-xs text-slate-600 max-w-md">
			<summary class="cursor-pointer font-semibold mb-1">Why the wait?</summary>
			<div class="pt-2">
				To keep SG Lib Books free, our server takes a short nap when not in use. When you visit
				after a while, it takes a moment to start up again. Thank you for supporting our free
				service!
			</div>
		</details>
	</div>
</main>
