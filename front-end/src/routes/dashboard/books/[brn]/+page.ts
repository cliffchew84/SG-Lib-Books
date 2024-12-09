import type { PageLoad } from './$types'
import { getBook } from '$lib/api/book'

export const load: PageLoad = async ({ parent, params }) => {
  /**
   * Query book data from backend
   */
  const { client } = await parent()

  const brn = parseInt(params.brn)
  const bookResponse = getBook(client, brn)

  return { bookResponse }
}
