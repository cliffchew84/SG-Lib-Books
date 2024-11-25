import { redirect } from '@sveltejs/kit'
import type { LayoutLoad } from './$types'

export const load: LayoutLoad = async ({ parent }) => {
	/**
	 * Check if user session is available, else redirect to login
	 */
	const { session } = await parent();
	if (!session) {
		redirect(307, '/auth/sign-in')
	}
}
