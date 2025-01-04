<script lang="ts">
	import { LogIn, Library, Radar, Sprout } from 'lucide-svelte';

	import { Button } from '$lib/components/ui/button';
	import Footer from '$lib/components/layout/Footer.svelte';
	import highlightPic from '$lib/images/library-overview.png';

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

<header class="flex flex-row justify-between p-2 border shadow items-center min-h-16">
	<a href="/">SG Lib Books <span class="text-[0.5em]">BETA</span></a>
	<Button href="/auth/sign-in" class="ml-auto">
		<LogIn class="mr-2 h-4 w-4" />
		<span class="text-xs">Sign In</span>
	</Button>
</header>

<main class="">
	<!-- Hero header -->
	<section
		id="hero"
		class="min-h-[85vh] bg-gradient-to-b from-slate-100 to-white container-sm md:container-lg md:mx-auto px-5 text-xl font-primary"
	>
		<div class="mx-auto text-center py-16 max-w-3xl">
			<h1 class="mb-6 text-6xl font-semibold text-slate-700">
				Redefining your book borrowing experience
			</h1>
			<p class="text-slate-500 mb-8">
				Borrowing your favourite books easier at your neighbourhood libraries
			</p>
			<Button href="/auth/sign-in" class="ml-auto mb-10">
				<LogIn class="mr-2 h-4 w-4" />
				<span>Be Our Beta Tester!</span>
			</Button>
			<img
				class="rounded-xl shadow-lg shadow-slate-800 mb-10"
				src={highlightPic}
				alt="sg-lib-books"
			/>
		</div>
	</section>
	<section class="container my-6">
		<div class="w-full flex md:flex-row flex-col justify-center md:gap-16 gap-3">
			<div class="w-72 flex flex-col gap-3 mb-9">
				<div class="flex">
					<Library class="mr-4" />
					<h3 class="text-xl font-semibold">Library View</h3>
				</div>
				<p class="text-slate-700">
					Overview of books availibility on each library. You wont missed out your favourite book
					on-shelve again!
				</p>
			</div>
			<div class="w-72 flex flex-col gap-3 mb-9">
				<div class="flex">
					<Radar class="mr-4" />
					<h3 class="text-xl font-semibold">Plan your Trip Ahead</h3>
				</div>
				<p class="text-slate-700">
					Know which library has your favourite book so you can plan your journey ahead.
				</p>
			</div>
			<div class="w-72 flex flex-col gap-3 mb-9">
				<div class="flex">
					<Sprout class="mr-4" />
					<h3 class="text-xl font-bold mb-2">Community Driven</h3>
				</div>
				<p class="text-slate-700">
					From the fellow readers to the community. We are here to resolve your pain points that
					bugs us too.
				</p>
			</div>
		</div>
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
