import type BackendAPIClient from './client';
import type { Library, LibraryResponse } from './models';

export async function getLibraries(client: BackendAPIClient): Promise<LibraryResponse[]> {
	try {
		const response = await client.get({ path: `/library` });

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}, detail: ${await response.text()}`, {
				cause: response.status
			});
		}

		const data: LibraryResponse[] = await response.json();

		return data;
	} catch (error) {
		if (error instanceof Error) {
			console.error('Error querying api:', error.message);
		} else {
			console.error('An unknown error occurred while querying API');
		}
		throw error;
	}
}

export async function getLibrary(client: BackendAPIClient, name: string): Promise<Library> {
	try {
		const response = await client.get({ path: `/library/${name}` });

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}, detail: ${await response.text()}`, {
				cause: response.status
			});
		}

		const data: Library = await response.json();

		return data;
	} catch (error) {
		if (error instanceof Error) {
			console.error('Error querying api:', error.message);
		} else {
			console.error('An unknown error occurred while querying API');
		}
		throw error;
	}
}

export async function favouriteLibrary(client: BackendAPIClient, name: string): Promise<null> {
	try {
		const response = await client.post({ path: `/library/${name}` });

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}, detail: ${await response.text()}`, {
				cause: response.status
			});
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
}

export async function unfavouriteLibrary(client: BackendAPIClient, name: string): Promise<null> {
	try {
		const response = await client.delete({ path: `/library/${name}` });

		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}, detail: ${await response.text()}`, {
				cause: response.status
			});
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
}
