<script lang="ts">
	import type { SupabaseClient } from '@supabase/supabase-js';
	import LoaderCircle from 'lucide-svelte/icons/loader-circle';

	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import SignInWithGoogle from '$lib/components/buttons/sign-in-with-google.svelte';

	import { cn } from '$lib/utils.js';
	import { goto } from '$app/navigation';

	let {
		class: className = undefined,
		supabase,
		...restProps
	}: { class: string | undefined | null; supabase: SupabaseClient } = $props();
	let isLoading = $state(false);
	let email = $state('');
	let errorMessage = $state('');

	async function onSubmitEmail(e: SubmitEvent) {
		e.preventDefault();
		if (email === '') {
			errorMessage = 'Email cannot be empty';
			return;
		}
		isLoading = true;
		const { error } = await supabase.auth.signInWithOtp({
			email: email,
			options: {
				// set this to false if you do not want the user to be automatically signed up
				shouldCreateUser: true
			}
		});
		if (error) {
			isLoading = false;
			errorMessage = error.message;
			return;
		}
		await supabase.auth.refreshSession();
		goto('/auth/email-confirmation');
	}
</script>

<div class={cn('grid gap-6', className)} {...restProps}>
	<form onsubmit={onSubmitEmail}>
		<div class="grid gap-2">
			<div class="grid gap-1">
				<Label class="sr-only" for="email">Email</Label>
				<Input
					id="email"
					placeholder="name@example.com"
					type="email"
					autocapitalize="none"
					autocomplete="email"
					autocorrect="off"
					bind:value={email}
					disabled={isLoading}
				/>
			</div>
			<Button type="submit" disabled={isLoading}>
				{#if isLoading}
					<LoaderCircle class="mr-2 h-4 w-4 animate-spin" />
				{/if}
				Sign In with Email
			</Button>
			{#if errorMessage}
				<p class="text-sm text-red-600">{errorMessage}</p>
			{/if}
		</div>
	</form>
	<div class="relative">
		<div class="absolute inset-0 flex items-center">
			<span class="w-full border-t"></span>
		</div>
		<div class="relative flex justify-center text-xs uppercase">
			<span class="bg-background text-muted-foreground px-2"> Or continue with </span>
		</div>
	</div>
	<SignInWithGoogle
		onClickFunction={() => {
			supabase.auth.signInWithOAuth({ provider: 'google' });
		}}
	/>
</div>
