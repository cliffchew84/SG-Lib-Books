<script lang="ts">
	import LoaderCircle from 'lucide-svelte/icons/loader-circle';
	import { goto } from '$app/navigation';
	import { isLoading } from '$lib/stores';

	// Redirect to library page after page load is completed
	$effect(() => {
		if (!$isLoading) {
			goto('/dashboard/library');
		}
	});
</script>

<svelte:head>
	<title>Welcome | SG Lib Books</title>
</svelte:head>

<main class="container flex flex-col gap-8 p-8 min-h-[85vh]">
	<div class="flex flex-col gap-3">
		<h1 class="text-4xl font-bold text-slate-700">Welcome to SG Lib Books</h1>
		<p class="text-sm text-slate-500">We are working hard to retrieve your favourite books.</p>
		<p class="text-sm text-slate-500">This might take a while at the start.</p>
		<div class="flex justify-center items-center">
			<LoaderCircle class="m-8 h-6 w-6 animate-spin" />
		</div>
	</div>
</main>
