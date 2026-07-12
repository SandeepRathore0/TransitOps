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

    if (response.status === 204) {
        return null;
    }

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.detail || "API Error");
    }
    return data;
}

export function applyRBAC() {
    const token = localStorage.getItem('transitops_token');
    if (!token) return;
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const role = payload.role;
        // Global Inject: Show who is logged in
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn && !document.getElementById('userGreeting')) {
            const greeting = document.createElement('span');
            greeting.id = 'userGreeting';
            greeting.style.marginRight = '20px';
            greeting.style.fontSize = '14px';
            greeting.style.color = '#9ca3af';
            greeting.innerHTML = `Logged in as: <strong style="color:#d97706">${role}</strong>`;
            logoutBtn.parentNode.insertBefore(greeting, logoutBtn);
        }
        
        if (role === 'Admin') return; // Admin sees everything

        const navItems = document.querySelectorAll('.sidebar .nav-item');
        navItems.forEach(item => {
            const href = item.getAttribute('href');
            let allowed = false;

            if (role === 'Fleet Manager') {
                if (href.includes('dashboard') || href.includes('vehicles') || href.includes('drivers') || href.includes('maintenance')) allowed = true;
            } else if (role === 'Dispatcher') {
                if (href.includes('dashboard') || href.includes('vehicles') || href.includes('drivers') || href.includes('trips') || href.includes('dispatch')) allowed = true;
            } else if (role === 'Safety Officer') {
                if (href.includes('dashboard') || href.includes('vehicles') || href.includes('drivers') || href.includes('audit')) allowed = true;
            } else if (role === 'Financial Analyst') {
                if (href.includes('dashboard') || href.includes('vehicles') || href.includes('drivers') || href.includes('fuel') || href.includes('expenses') || href.includes('analytics') || href.includes('operational')) allowed = true;
            }

            if (!allowed) {
                item.style.display = 'none';
            }
        });
    } catch (err) {
        console.error("Error parsing JWT for RBAC", err);
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyRBAC);
} else {
    applyRBAC();
}
