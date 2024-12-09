<script lang="ts">
	import type { SupabaseClient } from '@supabase/supabase-js';
	import LoaderCircle from 'lucide-svelte/icons/loader-circle';

	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';

	import { goto } from '$app/navigation';

	let { supabase }: { supabase: SupabaseClient } = $props();
	let isLoading = $state(false);
	let username = $state('');
	let errorMessage = $state('');

	async function onSubmitUsername(e: SubmitEvent) {
		e.preventDefault();
		isLoading = true;
		const { error } = await supabase.auth.updateUser({
			data: {
				name: username
			}
		});
		if (error) {
			isLoading = false;
			errorMessage = error.message;
			return;
		}
		await supabase.auth.refreshSession();
		goto('/dashboard');
	}
</script>

<div class="grid gap-6">
	<form onsubmit={onSubmitUsername}>
		<div class="grid gap-2">
			<div class="grid gap-1">
				<Label class="sr-only" for="username">Username</Label>
				<Input
					id="username"
					type="text"
					autocapitalize="none"
					autocorrect="off"
					bind:value={username}
					disabled={isLoading}
				/>
			</div>
			<Button type="submit" disabled={isLoading}>
				{#if isLoading}
					<LoaderCircle class="mr-2 h-4 w-4 animate-spin" />
				{/if}
				Confirm Username
			</Button>
			{#if errorMessage}
				<p class="text-sm text-red-600">{errorMessage}</p>
			{/if}
		</div>
	</form>
</div>
