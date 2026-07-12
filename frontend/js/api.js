export const API_URL = 'http://localhost:8000/api/v1';

export async function fetchApi(endpoint, options = {}) {
    const token = localStorage.getItem('transitops_token');
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers
    });

    if (response.status === 401) {
        localStorage.removeItem('transitops_token');
        window.location.href = 'login.html';
        throw new Error("Unauthorized");
    }

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.detail || "API Error");
    }
    return data;
}
