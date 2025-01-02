<script lang="ts">
	import { LogIn, Library, Radar, Sprout } from 'lucide-svelte';

	import { Button } from '$lib/components/ui/button';
	import Footer from '$lib/components/layout/Footer.svelte';

	import { goto } from '$app/navigation';
	import type { PageData } from './$types';

	let data: PageData = $props();
	if (data.session !== undefined) {
		goto('/dashboard');
	}
</script>

<svelte:head>
	<title>SG Lib Books</title>
</svelte:head>

<main class="">
	<!-- Hero header -->
	<section
		id="hero"
		class="min-h-[85vh] bg-slate-100 container-sm md:container-lg md:mx-auto px-5 text-xl font-primary"
	>
		<header class="flex items-center min-h-screen max-w-6xl">
			<div class="mx-auto">
				<h1 class="mb-1 text-4xl font-bold text-slate-700">
					SG Lib Books <span class="text-sm">BETA</span>
				</h1>
				<p class="mb-3 text-slate-500">
					Redefining book borrowing experience at your neighbourhood libraries.
				</p>
				<Button href="/auth/sign-in" class="ml-auto">
					<LogIn class="mr-2 h-4 w-4" />
					<span>Be Our Beta Tester!</span>
				</Button>
			</div>
		</header>
	</section>
	<section class="container mb-6">
		<div>
			<h2 class="mb-3 text-3xl font-bold text-slate-700">Calling all Singapore library users!</h2>
			<p>
				We are a group of Singapore tech and book enthusiasts who wanted to improve our physical
				library book borrowing experience.
			</p>
		</div>
	</section>
	<section class="container mb-6">
		<div>
			<h2 class="mb-12 text-3xl font-bold text-slate-700">Why consider us?</h2>
			<div class="w-full flex md:flex-row flex-col justify-center md:gap-8 gap-3">
				<div class="w-72 flex flex-col gap-3 mb-9 text-center">
					<Library class="my-1 mx-auto" />
					<div>
						<h3 class="text-xl font-bold mb-2">Library View</h3>
						<p class="">
							Overview of books availibility on each library. You wont missed out your favourite
							book on-shelve again!
						</p>
					</div>
				</div>
				<div class="w-72 flex flex-col gap-3 mb-9 text-center">
					<Radar class="my-1 mx-auto" />
					<div>
						<h3 class="text-xl font-bold mb-2">Plan your Trip Ahead</h3>
						<p class="">
							Know which library has your favourite book so you can plan your journey ahead.
						</p>
					</div>
				</div>
				<div class="w-72 flex flex-col gap-3 mb-9 text-center">
					<Sprout class="my-1 mx-auto" />
					<div>
						<h3 class="text-xl font-bold mb-2">Community Driven</h3>
						<p class="">
							From the fellow readers to the community. We are here to resolve your pain points that
							bugs us too.
						</p>
					</div>
				</div>
			</div>
		</div>
	</section>
	<section class="container">
		<div>
			<h2 class="mb-3 text-3xl font-bold text-slate-700">Join our waitlist!</h2>
			<p class="mb-3">
				Join our waitlist to receive an email as soon as our web application is ready.
			</p>
			<Button href="https://forms.gle/C4MyKxAyUhhgds4U9">Join our waitlist!</Button>
		</div>
	</section>
</main>
<Footer />
