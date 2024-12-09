import type { PageLoad } from './$types'
import { getLibrary } from '$lib/api/library'

export const load: PageLoad = async ({ parent, params }) => {
  /**
   * Query book data from backend
   */
  const { client } = await parent()

  const lid = params.lid;
  const libraryResponse = getLibrary(client, lid);

  return { libraryResponse }
}
