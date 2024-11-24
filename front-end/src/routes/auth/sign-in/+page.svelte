<script lang="ts">
	import UserAuthForm from '$lib/components/forms/user-auth-form.svelte';
</script>

<div
	class="container relative h-[100vh] flex-col items-center justify-center grid lg:max-w-none lg:grid-cols-2 lg:px-0"
>
	<div class="bg-muted relative hidden h-full flex-col p-10 text-white lg:flex dark:border-r">
		<div
			class="absolute inset-0 bg-cover"
			style="
				background-image:
					url(https://images.unsplash.com/photo-1481627834876-b7833e8f5570?q=80&w=2128&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D);"
		></div>
		<a class="relative z-20 flex items-center text-lg font-medium" href="/">SG Lib Books</a>
	</div>
	<div class="lg:p-8">
		<div class="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
			<div class="flex flex-col space-y-2 text-center">
				<h1 class="text-2xl font-semibold tracking-tight">Sign In</h1>
				<p class="text-muted-foreground text-sm">
					Enter your email below to sign-in to your account
				</p>
			</div>
			<UserAuthForm class={undefined} />
		</div>
	</div>
</div>
