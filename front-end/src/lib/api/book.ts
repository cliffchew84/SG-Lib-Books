import type BackendAPIClient from "./client";
import type { BookAvail, BookResponse } from "./models";


export async function getBooks(client: BackendAPIClient): Promise<BookResponse[]> {
	try {
		const response = await client.get({ path: "/books" });

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}, detail: ${await response.text()}`, { cause: response.status });
		}

		const data: BookResponse[] = await response.json();

		return data;
	} catch (error) {
		if (error instanceof Error) {
			console.error('Error querying api:', error.message);
		} else {
			console.error('An unknown error occurred while querying API');
		}
		throw error;
	}
};

export async function updateBooks(client: BackendAPIClient): Promise<null> {
	try {
		const response = await client.put({ path: `/books` });

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}, detail: ${await response.text()}`, { cause: response.status });
		}

		return null;
	} catch (error) {
		if (error instanceof Error) {
			console.error('Error querying api:', error.message);
		} else {
			console.error('An unknown error occurred while querying API');
		}
		throw error;
	}
};

export async function getBook(client: BackendAPIClient, brn: number, live: boolean = false): Promise<BookResponse> {
	try {
		const response = await client.get({ path: `/books/${brn}`, queryParams: { live } });

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}, detail: ${await response.text()}`, { cause: response.status });
		}

		const data: BookResponse = await response.json();

		return data;
	} catch (error) {
		if (error instanceof Error) {
			console.error('Error querying api:', error.message);
		} else {
			console.error('An unknown error occurred while querying API');
		}
		throw error;
	}
};

export async function likeBook(client: BackendAPIClient, brn: number): Promise<BookResponse> {
	try {
		const response = await client.post({ path: `/books/${brn}` });

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}, detail: ${await response.text()}`, { cause: response.status });
		}

		const data: BookResponse = await response.json();

		return data;
	} catch (error) {
		if (error instanceof Error) {
			console.error('Error querying api:', error.message);
		} else {
			console.error('An unknown error occurred while querying API');
		}
		throw error;
	}
};

export async function updateBook(client: BackendAPIClient, brn: number): Promise<BookAvail[]> {
	try {
		const response = await client.put({ path: `/books/${brn}` });

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}, detail: ${await response.text()}`, { cause: response.status });
		}

		const data: BookAvail[] = await response.json();

		return data;
	} catch (error) {
		if (error instanceof Error) {
			console.error('Error querying api:', error.message);
		} else {
			console.error('An unknown error occurred while querying API');
		}
		throw error;
	}
};

export async function unlikeBook(client: BackendAPIClient, brn: number): Promise<null> {
	try {
		const response = await client.delete({ path: `/books/${brn}` });

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}, detail: ${await response.text()}`, { cause: response.status });
		}

		return null;
	} catch (error) {
		if (error instanceof Error) {
			console.error('Error querying api:', error.message);
		} else {
			console.error('An unknown error occurred while querying API');
		}
		throw error;
	}
};
