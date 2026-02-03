/**
 * API Client Configuration
 * 
 * Centralized configuration for API requests with authentication
 */

/**
 * Get API headers with authentication
 */
export function getApiHeaders(): HeadersInit {
    const headers: HeadersInit = {
        'Content-Type': 'application/json',
    };

    // Add API key if configured (for production)
    const apiKey = process.env.NEXT_PUBLIC_API_KEY;
    if (apiKey) {
        headers['X-API-Key'] = apiKey;
    }

    return headers;
}

/**
 * Fetch wrapper with automatic authentication
 */
export async function apiFetch(url: string, options: RequestInit = {}): Promise<Response> {
    const headers = {
        ...getApiHeaders(),
        ...options.headers,
    };

    return fetch(url, {
        ...options,
        headers,
    });
}

/**
 * Typed API fetch with JSON response
 */
export async function apiFetchJSON<T = any>(url: string, options: RequestInit = {}): Promise<T> {
    const response = await apiFetch(url, options);

    if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(error.error || error.message || `HTTP ${response.status}`);
    }

    return response.json();
}
