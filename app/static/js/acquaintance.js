// Acquaintance Profile Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const addFriendBtn = document.getElementById('add-friend-btn');
    const cancelRequestBtn = document.getElementById('cancel-request-btn');
    const friendRequestForm = document.getElementById('friend-request-form');

    // Handle add friend button click
    if (addFriendBtn && friendRequestForm) {
        friendRequestForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Add loading state
            addFriendBtn.classList.add('btn-loading');
            addFriendBtn.disabled = true;
            
            // Get form data
            const formData = new FormData(friendRequestForm);
            
            // Send friend request
            fetch(friendRequestForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Hide add friend button, show cancel request button
                    addFriendBtn.style.display = 'none';
                    cancelRequestBtn.classList.remove('hidden');
                    
                    // Update friendship status
                    const friendshipStatus = document.querySelector('.friendship-status');
                    if (friendshipStatus) {
                        friendshipStatus.textContent = 'Friend request sent';
                        friendshipStatus.style.color = '#f39c12';
                    }
                    
                    // Show success message
                    showNotification('Friend request sent successfully!', 'success');
                } else {
                    // Show error message
                    showNotification(data.message || 'Failed to send friend request', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('An error occurred. Please try again.', 'error');
            })
            .finally(() => {
                // Remove loading state
                addFriendBtn.classList.remove('btn-loading');
                addFriendBtn.disabled = false;
            });
        });
    }

    // Handle cancel request button click
    if (cancelRequestBtn) {
        cancelRequestBtn.addEventListener('click', function() {
            // Add loading state
            cancelRequestBtn.classList.add('btn-loading');
            cancelRequestBtn.disabled = true;
            
            // Send cancel request (you'll need to implement this endpoint)
            fetch('/friends/cancel-friend-request', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    user_id: document.querySelector('input[name="user_id"]').value
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show add friend button, hide cancel request button
                    addFriendBtn.style.display = 'flex';
                    cancelRequestBtn.classList.add('hidden');
                    
                    // Update friendship status
                    const friendshipStatus = document.querySelector('.friendship-status');
                    if (friendshipStatus) {
                        friendshipStatus.textContent = "You're not yet friends";
                        friendshipStatus.style.color = '#b993fd';
                    }
                    
                    // Show success message
                    showNotification('Friend request cancelled', 'info');
                } else {
                    showNotification(data.message || 'Failed to cancel friend request', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('An error occurred. Please try again.', 'error');
            })
            .finally(() => {
                // Remove loading state
                cancelRequestBtn.classList.remove('btn-loading');
                cancelRequestBtn.disabled = false;
            });
        });
    }

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