import type { Session } from '@supabase/supabase-js';

interface APIRequestOptions {
	method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
	path?: string;
	queryParams?: Record<string, string | number | boolean>;
	body?: Record<string, any>;
	headers?: Record<string, string>;
}

class BackendAPIClient {
	private baseURL: string;
	private session: Session | null;

	constructor(
		baseURL: string,
		session: Session | null
	) {
		this.baseURL = baseURL;
		this.session = session;
	}


	private buildURL(path: string = '', queryParams: Record<string, string | number | boolean> = {}): string {
		const url = new URL(`${this.baseURL}/${path.replace(/^\//, '')}`);

		Object.entries(queryParams).forEach(([key, value]) => {
			url.searchParams.append(key, String(value));
		});

		return url.toString();
	}

	async request({
		method = 'GET',
		path = '',
		queryParams = {},
		body = {},
		headers = {}
	}: APIRequestOptions): Promise<Response> {
		const requestHeaders: Record<string, string> = {
			'Content-Type': 'application/json',
			...headers
		};

		if (this.session) {
			requestHeaders['Authorization'] = `Bearer ${this.session.access_token}`
		}

		const fullURL = this.buildURL(path, queryParams);

		const response = await fetch(fullURL, {
			method,
			headers: requestHeaders,
			body: method !== 'GET' ? JSON.stringify(body) : undefined
		});

		return response
	}

	// Convenience methods for common HTTP verbs
	async get(options: Omit<APIRequestOptions, 'method'>) {
		return this.request({ ...options, method: 'GET' });
	}

	async post(options: Omit<APIRequestOptions, 'method'>) {
		return this.request({ ...options, method: 'POST' });
	}

	async put(options: Omit<APIRequestOptions, 'method'>) {
		return this.request({ ...options, method: 'PUT' });
	}

	async delete(options: Omit<APIRequestOptions, 'method'>) {
		return this.request({ ...options, method: 'DELETE' });
	}

	async patch(options: Omit<APIRequestOptions, 'method'>) {
		return this.request({ ...options, method: 'PATCH' });
	}
}

export default BackendAPIClient;

