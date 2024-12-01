<script lang="ts">
	import { goto } from '$app/navigation';
	import type { LayoutData } from './$types';

	let { data }: { data: LayoutData } = $props();

	if (data.user?.user_metadata.name === undefined) {
		// Redirect user to fill in username if it is empty
		// when new user signed-in via email
		goto('/auth/new-sign-in');
	}
	// Else, redirect to library page
	goto('/dashboard/library');
</script>
