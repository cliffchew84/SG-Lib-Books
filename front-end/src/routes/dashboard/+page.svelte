<script lang="ts">
	import LoaderCircle from 'lucide-svelte/icons/loader-circle';
	import { goto } from '$app/navigation';
	import { isLoading } from '$lib/stores';

	let loadingDots = $state('');
	let interval: ReturnType<typeof setInterval>;

	$effect(() => {
		if (!$isLoading) {
			// goto('/dashboard/library');
		}
	});
</script>

<svelte:head>
	<title>Welcome | SG Lib Books</title>
</svelte:head>

<main class="container flex flex-col gap-8 p-8 min-h-[85vh]">
	<div class="flex flex-col gap-3 items-center">
		<h1 class="text-4xl font-bold text-slate-700 text-center">Welcome to SG Lib Books</h1>
		<p class="text-base text-slate-600 text-center max-w-xl">
			Thank you for your patience!<br />
			<span class="font-semibold">Our server is starting up</span> due to inactivity.<br />
			This may take a few seconds as our backend "wakes up" from sleep.<br />
			Once ready, you'll be redirected to your library dashboard.
		</p>
		<div class="flex flex-col items-center justify-center mt-6">
			<LoaderCircle class="m-4 h-10 w-10 animate-spin text-blue-500" />
		</div>
		<div class="mt-4 text-xs text-slate-400 text-center max-w-md">
			<p>
				Why the wait? <br />
				To keep SG Lib Books free, we use a cloud server that "sleeps" when not in use.<br />
				When you visit after a while, it takes a moment to start up again.<br />
				Thank you for supporting our free service!
			</p>
		</div>
	</div>
</main>
