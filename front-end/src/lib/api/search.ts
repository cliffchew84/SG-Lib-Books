import type BackendAPIClient from "./client";

interface BookInfo {
	BID: number;
	TitleName?: string;
	Author?: string
	PublishYear?: string;
	Publisher?: string;
	Subjects?: string;
	isbns?: string;
	cover_url?: string;
}

interface APIResponse {
	total_records: number;
	has_more_records: boolean;
	next_offset: number;
	titles: BookInfo[];
}

export async function searchBook(client: BackendAPIClient, keyword: string, offset: number): Promise<APIResponse> {
	if (!keyword) {
		console.warn('Empty keywords is provided.');
		throw new Error("Empty keywords is provided");
	}

	try {
		const response = await client.get({ path: "/search", queryParams: { keyword, offset } });

		if (!response.ok) {
			if (response.status === 404) {
				return {
					total_records: 0,
					has_more_records: false,
					next_offset: 0,
					titles: []
				}
			}

			throw new Error(`HTTP error! status: ${response.status}, detail: ${await response.text()}`);
		}

		const data: APIResponse = await response.json();

		return data;
	} catch (error) {
		if (error instanceof Error) {
			console.error('Error querying api:', error.message);
		} else {
			console.error('An unknown error occurred while querying address');
		}
		throw error;
	}
};