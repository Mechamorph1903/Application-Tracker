function switchTab(tab) {
    // Remove active class from all tabs and forms
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('form').forEach(f => f.classList.remove('active'));
    
    // Add active class to clicked tab
    document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
    
    // Add active class to corresponding form
    if (tab === 'login') {
        document.getElementById('loginForm').classList.add('active');
    } else {
        document.getElementById('registerForm').classList.add('active');
    }
}

function getTabFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('tab') || 'register';
}

// Set initial state when page loads
window.onload = () => {
    const tab = getTabFromURL();
    switchTab(tab);
};