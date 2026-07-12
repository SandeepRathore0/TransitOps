import { fetchApi, API_URL } from './api.js';

export async function login(email, password) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
    });
    
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail);
    
    localStorage.setItem('transitops_token', data.access_token);
    window.location.href = 'dashboard.html';
}

export function logout() {
    localStorage.removeItem('transitops_token');
    window.location.href = 'login.html';
}
