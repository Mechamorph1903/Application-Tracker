document.addEventListener('DOMContentLoaded', function() {
    // No AJAX or notification logic for friend actions; forms submit normally for Flask flash/redirect UX.

    // Add hover effects to action buttons
    const actionBtns = document.querySelectorAll('.action-btn');
    actionBtns.forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            if (this.id === 'add-friend-btn') {
                const btnText = this.querySelector('.btn-text');
                if (btnText) {
                    btnText.textContent = 'Unlock Applications 🔓';
                }
            }
        });

        btn.addEventListener('mouseleave', function() {
            if (this.id === 'add-friend-btn') {
                const btnText = this.querySelector('.btn-text');
                if (btnText) {
                    btnText.textContent = 'Add Friend';
                }
            }
        });
    });

    // Animate mutual friends on load
    const friendAvatars = document.querySelectorAll('.friend-avatar');
    friendAvatars.forEach((avatar, index) => {
        setTimeout(() => {
            avatar.style.opacity = '0';
            avatar.style.transform = 'scale(0.8)';
            avatar.style.transition = 'all 0.3s ease';
            
            setTimeout(() => {
                avatar.style.opacity = '1';
                avatar.style.transform = 'scale(1)';
            }, 50);
        }, index * 100);
    });
});

// Utility function to show notifications
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fa-solid fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Add styles
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '12px 16px',
        borderRadius: '8px',
        backgroundColor: type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3',
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        zIndex: '10000',
        transform: 'translateX(100%)',
        transition: 'transform 0.3s ease',
        boxShadow: '0 4px 12px rgba(0,0,0,0.2)'
    });
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 10);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}