// /frontend/src/lib/services/api.ts
import { goto } from '$app/navigation';

const BASE_URL = 'http://localhost:8000'; // Your FastAPI backend URL

// This is a helper function to handle the response
async function handleResponse(response: Response) {
	if (response.ok) {
		// If the response is OK, parse the JSON
		return await response.json();
	}

	if (response.status === 401) {
		// Unauthorized (e.g., token expired)
		localStorage.removeItem('accessToken');
		console.error('Unauthorized (401). Redirecting to login.');
		await goto('/login');
		throw new Error('Unauthorized');
	}

	// Handle other server errors
	const errorData = await response.json();
	const errorMessage = errorData.detail || 'An unknown server error occurred.';
	console.error(`API Error (${response.status}): ${errorMessage}`);
	throw new Error(errorMessage);
}

// This is our main request function that sets up headers
async function request(endpoint: string, options: RequestInit = {}) {
	const token = localStorage.getItem('accessToken');
	const headers = new Headers(options.headers || {});

	// Set default JSON content type
	if (!headers.has('Content-Type') && options.body) {
		headers.set('Content-Type', 'application/json');
	}

	// Add the auth token if it exists
	if (token) {
		headers.set('Authorization', `Bearer ${token}`);
	}

	// Add cache-busting for GET requests
	let url = `${BASE_URL}${endpoint}`;
	if (options.method === 'GET' || !options.method) {
		const cacheBuster = `_=${new Date().getTime()}`;
		url += url.includes('?') ? `&${cacheBuster}` : `?${cacheBuster}`;
	}

	// Perform the fetch request
	try {
		const response = await fetch(url, {
			...options,
			headers: headers
		});
		return handleResponse(response);
	} catch (error: any) {
		// Handle network errors
		if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
			console.error('Network error. Is the backend server running?');
			throw new Error('Network error. Please try again.');
		}
		// Re-throw other errors (like the ones from handleResponse)
		throw error;
	}
}

// --- Our Exported API Functions ---

export const api = {
	get: (endpoint: string) => {
		return request(endpoint, { method: 'GET' });
	},

	post: (endpoint: string, body: object) => {
		return request(endpoint, {
			method: 'POST',
			body: JSON.stringify(body)
		});
	},

	patch: (endpoint: string, body: object) => {
		return request(endpoint, {
			method: 'PATCH',
			body: JSON.stringify(body)
		});
	},

	put: (endpoint: string, body: object) => {
		return request(endpoint, {
			method: 'PUT',
			body: JSON.stringify(body)
		});
	},

	delete: (endpoint: string) => {
		return request(endpoint, { method: 'DELETE' });
	}
};