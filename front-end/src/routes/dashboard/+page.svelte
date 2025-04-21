<script lang="ts">
	import LoaderCircle from 'lucide-svelte/icons/loader-circle';
	import { goto } from '$app/navigation';
	import { isLoading } from '$lib/stores';

	$effect(() => {
		if (!$isLoading) {
			// goto('/dashboard/library');
		}
	});
</script>

<svelte:head>
	<title>Welcome | SG Lib Books</title>
</svelte:head>

<main class="flex flex-col items-center justify-center min-h-[85vh] bg-slate-50 p-4">
	<div class="bg-white rounded-lg shadow-lg p-8 max-w-md w-full flex flex-col items-center gap-4">
		<h1 class="text-3xl md:text-4xl font-bold text-slate-700 text-center">
			Welcome to SG Lib Books
		</h1>
		<p class="text-base text-slate-600 text-center">
			<span class="font-semibold">Just a moment…</span> <br />
			Our service is starting up and you'll be redirected soon.
		</p>
		<div class="flex flex-col items-center justify-center mt-4" aria-busy="true" aria-live="polite">
			<LoaderCircle class="m-4 h-10 w-10 animate-spin text-blue-500" />
			<span class="sr-only">Loading…</span>
		</div>
		<button class="mt-2 text-blue-500 hover:underline text-xs" on:click={() => location.reload()}>
			Not redirected yet? <span class="font-semibold">Retry</span>
		</button>
		<details class="mt-2 text-xs text-slate-400 max-w-md">
			<summary class="cursor-pointer font-semibold mb-1">Why the wait?</summary>
			<div class="pt-2">
				To keep SG Lib Books free, our server takes a short nap when not in use. When you visit
				after a while, it takes a moment to start up again. Thank you for supporting our free
				service!
			</div>
		</details>
	</div>
</main>
