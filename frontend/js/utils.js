
export function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.position = 'fixed';
        container.style.bottom = '24px';
        container.style.right = '24px';
        container.style.zIndex = '9999';
        container.style.display = 'flex';
        container.style.flexDirection = 'column';
        container.style.gap = '12px';
        document.body.appendChild(container);
    }
    
    const toast = document.createElement('div');
    toast.className = 'card';
    toast.style.padding = '12px 24px';
    toast.style.minWidth = '250px';
    toast.style.display = 'flex';
    toast.style.justifyContent = 'space-between';
    toast.style.alignItems = 'center';
    toast.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.5)';
    toast.style.animation = 'slideIn 0.3s ease-out forwards';
    
    let color = 'var(--primary-color)';
    if (type === 'success') color = 'var(--success-color)';
    if (type === 'error') color = 'var(--danger-color)';
    if (type === 'warning') color = 'var(--warning-color)';
    
    toast.style.borderLeft = `4px solid ${color}`;
    
    toast.innerHTML = `<span style="font-weight: 500; font-size: 14px;">${message}</span>`;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-in forwards';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Add animations dynamically
const style = document.createElement('style');
style.innerHTML = `
@keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
@keyframes slideOut { from { transform: translateX(0); opacity: 1; } to { transform: translateX(100%); opacity: 0; } }
.skeleton { background: linear-gradient(90deg, var(--bg-card) 25%, #4B5563 50%, var(--bg-card) 75%); background-size: 200% 100%; animation: shimmer 1.5s infinite; border-radius: 4px; }
@keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
`;
document.head.appendChild(style);
