import { createBrowserClient } from '@supabase/ssr'
import { PUBLIC_SUPABASE_ANON_KEY, PUBLIC_SUPABASE_URL } from '$env/static/public'
import type { LayoutLoad } from './$types'

// Client-side rendering only
export const ssr = false

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

	return { session, supabase, user }
}
