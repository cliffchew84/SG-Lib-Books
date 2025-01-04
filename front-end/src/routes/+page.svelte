<script lang="ts">
	import { LogIn, Library, Radar, Sprout, Smartphone, Bell } from 'lucide-svelte';

	import Header from '$lib/components/layout/Header.svelte';
	import Footer from '$lib/components/layout/Footer.svelte';
	import { Button } from '$lib/components/ui/button';
	import readingPic from '$lib/images/reading.gif';
	import highlightPic from '$lib/images/library-overview.png';

	import { goto } from '$app/navigation';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
	$effect(() => {
		if (data.session != null) {
			goto('/dashboard');
		}
	});
</script>

<svelte:head>
	<title>SG Lib Books</title>
</svelte:head>

<Header user={data.user} />
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
				Borrowing your favourite books easier at your neighbourhood public libraries
			</p>
			<Button href="/auth/sign-in" class="ml-auto mb-10">
				<LogIn class="mr-2 h-4 w-4" />
				<span>Be Our Beta Tester!</span>
			</Button>
			<img
				class="rounded-xl shadow-lg shadow-slate-500 mb-10"
				src={highlightPic}
				alt="sg-lib-books"
			/>
		</div>
	</section>
	<section class="container my-6">
		<div class="flex lg:flex-row flex-col items-center lg:gap-16 gap-3">
			<div class="w-72 flex flex-col gap-3 mb-9">
				<div class="flex items-center">
					<Library class="mr-4 w-6 h-6" />
					<h3 class="text-2xl font-semibold">Library View</h3>
				</div>
				<p class="text-slate-700">
					Overview of books availibility on each library. You wont missed out your favourite book
					on-shelve again!
				</p>
			</div>
			<div class="w-72 flex flex-col gap-3 mb-9">
				<div class="flex items-center">
					<Radar class="mr-4 w-6 h-6" />
					<h3 class="text-2xl font-semibold">Plan your Trip Ahead</h3>
				</div>
				<p class="text-slate-700">
					Know which library has your favourite book so you can plan your journey ahead.
				</p>
			</div>
			<div class="w-72 flex flex-col gap-3 mb-9">
				<div class="flex items-center">
					<Smartphone class="mr-4 w-6 h-6" />
					<h3 class="text-2xl font-semibold">Mobile Friendly</h3>
				</div>
				<p class="text-slate-700">
					Easily check the availability of your favorite books anytime, anywhere, on any device.
				</p>
			</div>
			<div class="w-72 flex flex-col gap-3 mb-9">
				<div class="flex items-center">
					<Sprout class="mr-4 w-6 h-6" />
					<h3 class="text-2xl font-semibold">Community Driven</h3>
				</div>
				<p class="text-slate-700">
					From fellow readers to the community, we're here to tackle the pain points that bugs us
					too.
				</p>
			</div>
		</div>
	</section>

	<section class="container mb-9 flex flex-col md:flex-row gap-6">
		<div class="flex items-center">
			<div>
				<h2 class="mb-6 text-4xl font-semibold text-slate-700">
					Calling all Singapore library users!
				</h2>
				<p class="text-slate-700 text-lg mb-3">
					We are a group of Singapore tech and book enthusiasts who wanted to improve our physical
					library book borrowing experience.
				</p>
				<ul class="list-disc pl-4 text-slate-700 text-lg">
					<li>Mark your favourite books</li>
					<li>Check for book availibility from all public libraries</li>
					<li>
						Join our <a
							href="https://github.com/cliffchew84/SG-Lib-Books"
							class="underline font-semibold">open source</a
						> movement to make book borrowing easier
					</li>
					<li>Other exciting features in coming soon!</li>
				</ul>
			</div>
		</div>
		<div class="rounded-xl max-w-sm mx-auto">
			<a
				class="w-full text-slate-500 text-sm mx-auto"
				href="https://www.flaticon.com/free-animated-icons/reading"
				title="reading animated icons"
			>
				<img class="rounded-xl" src={readingPic} alt="reading animated icons" />
			</a>
		</div>
	</section>
	<section class="bg-gradient-to-b from-white to-slate-100">
		<div class="max-w-3xl mx-auto text-center">
			<h2 class="mb-6 text-4xl font-semibold text-slate-700">Join our waitlist!</h2>
			<p class="text-slate-600 mb-8 text-lg">
				Loves what we are doing? Receives an email from us as soon as our web application is ready
				for everyone.
			</p>
			<Button class="mb-10" href="https://forms.gle/C4MyKxAyUhhgds4U9">
				<Bell class="mr-2 h-4 w-4" />
				<span>Notify when Ready!</span>
			</Button>
			<p class="text-slate-600 pt-8 pb-1 text-sm">
				SG Lib Books is an independent project that has no affiliation with the National Library
				Board.
			</p>
			<p class="text-slate-600 pb-2 text-sm">
				Data displayed by SG Lib Books is licensed under <a
					href="https://data.gov.sg/open-data-licence"
					class="underline">Singapore Open Data Licence</a
				>.
			</p>
		</div>
	</section>
</main>
<Footer />
