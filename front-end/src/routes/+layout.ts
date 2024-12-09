import { createBrowserClient } from '@supabase/ssr'
import { PUBLIC_SUPABASE_ANON_KEY, PUBLIC_SUPABASE_URL, PUBLIC_BACKEND_URL } from '$env/static/public'
import BackendAPIClient from '$lib/api/client'
import type { LayoutLoad } from './$types'

// Client-side rendering only
export const ssr = false

// Disable prerender to save API bandwidth
export const prerender = false

export const load: LayoutLoad = async ({ depends, fetch }) => {
	/**
	 * Declare a dependency so the layout can be invalidated, for example, on
	 * session refresh.
	 */
	depends('supabase:auth')

	const supabase =
		createBrowserClient(PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY, {
			global: {
				fetch,
			},
		})

	const {
		data: { session },
	} = await supabase.auth.getSession()

	const {
		data: { user },
	} = await supabase.auth.getUser()

	// TODO: change endpoint based on configuration
	const client = new BackendAPIClient(PUBLIC_BACKEND_URL, session)

	return { session, supabase, user, client }
}
