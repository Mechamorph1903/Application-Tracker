console.log('Settings.js loaded!');

const user_settings = document.querySelector('#user-settings');
const app_settings = document.querySelector('#app-settings');	
const tabButtons = document.querySelectorAll('.tab');

function switchTab(tab){
    console.log(`Switching from ${tab.id}....`)
    tabButtons.forEach(t => {
        t.classList.remove("active");
    });

    tab.classList.add('active');

    if (tab.id === "user-settings-tab"){
        user_settings.style.display = 'block';
        app_settings.style.display = 'none';
    } else{
        user_settings.style.display = 'none';
        app_settings.style.display = 'block';
    }
}

tabButtons.forEach(btn => {
    btn.addEventListener('click', function() {
        switchTab(btn);
    });
});

// Popup functionality
document.addEventListener('DOMContentLoaded', function() {
    const popup = document.getElementById('pop-up-back');
    const popupMessage = document.getElementById('pop-up-message');
    const popupCancel = document.getElementById('pop-up-cancel');
    const popupYes = document.getElementById('yes');
    const popupNo = document.getElementById('no');

    // Close popup functions
    function closePopup() {
        popup.style.display = 'none';
    }

    if (popupCancel) popupCancel.addEventListener('click', closePopup);
    if (popupNo) popupNo.addEventListener('click', closePopup);
    
    // Close popup when clicking outside
    if (popup) {
        popup.addEventListener('click', function(e) {
            if (e.target === popup) {
                closePopup();
            }
        });
    }

    // Show confirmation popup
    function showConfirmation(message, callback) {
        if (popupMessage) popupMessage.textContent = message;
        if (popup) popup.style.display = 'flex';
        
        // Remove any existing event listeners
        if (popupYes) {
            popupYes.onclick = null;
            popupYes.addEventListener('click', function() {
                closePopup();
                if (callback) callback();
            });
        }
    }

    // Form submission with confirmation
    function handleFormSubmit(form, sectionName) {
        const formData = new FormData(form);
        
        showConfirmation(`Are you sure you want to save changes to ${sectionName}?`, async function() {
            console.log('Saving changes for:', sectionName);
            
            try {
                // Determine the correct endpoint based on form
                let endpoint = '/settings/update-app-settings';
                if (form.closest('#user-settings')) {
                    endpoint = '/settings/update-user-settings';
                }
                
                const response = await fetch(endpoint, {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    // Update display values
                    updateDisplayValues(form);
                    
                    // Toggle back to display mode
                    const sectionId = form.id.replace('-form', '');
                    cancelEdit(sectionId);
                    
                    // Show success message
                    alert('Settings saved successfully!');
                    
                    // Refresh the page to show updated values
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    alert('Error saving settings: ' + (result.error || 'Unknown error'));
                }
                
            } catch (error) {
                console.error('Error:', error);
                alert('Network error saving settings');
            }
        });
    }

    // Update display values after successful save
    function updateDisplayValues(form) {
        const formData = new FormData(form);
        const sectionId = form.id.replace('-form', '');
        const displayDiv = document.getElementById(sectionId + '-display');
        
        if (displayDiv) {
            // Update display spans with new values
            displayDiv.querySelectorAll('span').forEach(span => {
                const label = span.previousElementSibling;
                if (label && label.tagName === 'LABEL') {
                    const fieldName = label.getAttribute('for') || label.textContent.toLowerCase().replace(/[^a-z]/g, '');
                    const formValue = formData.get(fieldName);
                    if (formValue !== null) {
                        // Format boolean values
                        if (formValue === 'true') {
                            span.textContent = 'Enabled';
                        } else if (formValue === 'false') {
                            span.textContent = 'Disabled';
                        } else {
                            span.textContent = formValue;
                        }
                    }
                }
            });
        }
    }

    // Add form submit listeners
    document.querySelectorAll('form[id$="-form"]').forEach(form => {
        form.addEventListener('submit', function(e) {
            const socialInput = form.querySelector('#social_media');
            if (socialInput) {
                if ((socialInput.value === '' || socialInput.value === '[]') && window._initialSocialMediaValue && window._initialSocialMediaValue !== '[]') {
                    socialInput.value = window._initialSocialMediaValue;
                }
            }
            e.preventDefault();
            const sectionName = form.id.replace('-form', '').replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase());
            handleFormSubmit(form, sectionName);
        });
    });
    
    // Initialize password features
    initializePasswordFeatures();
});

// Toggle edit mode for sections
function toggleEdit(sectionId) {
    const displayDiv = document.getElementById(sectionId + '-display');
    const formDiv = document.getElementById(sectionId + '-form');
    
    if (displayDiv && formDiv) {
        displayDiv.classList.add('hidden');
        formDiv.classList.remove('hidden');
    }
}

// Cancel edit mode
function cancelEdit(sectionId) {
    const displayDiv = document.getElementById(sectionId + '-display');
    const formDiv = document.getElementById(sectionId + '-form');
    
    if (displayDiv && formDiv) {
        displayDiv.classList.remove('hidden');
        formDiv.classList.add('hidden');
    }
}

// Export internships function
async function exportInternships() {
    try {
        const response = await fetch('/settings/export-internships');
        
        if (response.ok) {
            // Get filename from response headers or create default
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'internships.csv';
            if (contentDisposition) {
                const match = contentDisposition.match(/filename="(.+)"/);
                if (match) filename = match[1];
            }
            
            // Create download
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            alert('Internships exported successfully!');
        } else {
            const error = await response.json();
            alert('Export failed: ' + (error.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Export error:', error);
        alert('Network error during export');
    }
}

// Social Media Management
let socialMediaLinks = [];
const maxSocialLinks = 6;

const socialPlatforms = [
    { name: 'LinkedIn', icon: 'fa-brands fa-linkedin', placeholder: 'https://linkedin.com/in/username' },
    { name: 'GitHub', icon: 'fa-brands fa-github', placeholder: 'https://github.com/username' },
    { name: 'Facebook', icon: 'fa-brands fa-facebook', placeholder: 'https://facebook.com/username' },
    { name: 'Instagram', icon: 'fa-brands fa-instagram', placeholder: 'https://instagram.com/username' },
    { name: 'Twitter', icon: 'fa-brands fa-twitter', placeholder: 'https://twitter.com/username' },
    { name: 'YouTube', icon: 'fa-brands fa-youtube', placeholder: 'https://youtube.com/@username' },
    { name: 'Discord', icon: 'fa-brands fa-discord', placeholder: 'https://discord.gg/username' },
    { name: 'Twitch', icon: 'fa-brands fa-twitch', placeholder: 'https://twitch.tv/username' },
    { name: 'DeviantArt', icon: 'fa-brands fa-deviantart', placeholder: 'https://deviantart.com/username' },
    { name: 'Steam', icon: 'fa-brands fa-steam', placeholder: 'https://steamcommunity.com/id/username' },
    { name: 'Xbox', icon: 'fa-brands fa-xbox', placeholder: 'https://account.xbox.com/en-us/profile?gamertag=username' },
    { name: 'PlayStation', icon: 'fa-brands fa-playstation', placeholder: 'https://my.playstation.com/profile/username' },
    { name: 'Nintendo', icon: 'fas fa-gamepad', placeholder: 'https://accounts.nintendo.com/profile/username' },
    { name: 'Personal Website', icon: 'fas fa-globe', placeholder: 'https://yourwebsite.com' }
];

function initializeSocialMedia() {
    // Load existing social media links from the template
    const socialInput = document.getElementById('social_media');
    if (socialInput) {
        try {
            socialMediaLinks = JSON.parse(socialInput.value) || [];
        } catch (e) {
            socialMediaLinks = [];
        }
    }
    // renderSocialLinks();
}

function addSocialMediaLink() {
    if (socialMediaLinks.length >= maxSocialLinks) {
        alert(`You can only add up to ${maxSocialLinks} social media links.`);
        return;
    }
    
    socialMediaLinks.push({ platform: '', url: '' });
    renderSocialLinks();
}

function removeSocialMediaLink(index) {
    socialMediaLinks.splice(index, 1);
    renderSocialLinks();
}

function renderSocialLinks() {
    const container = document.getElementById('social-media-container');
    const addBtn = document.getElementById('add-social-btn');
    
    if (!container) return;
    
    container.innerHTML = '';
    
    socialMediaLinks.forEach((link, index) => {
        const linkDiv = document.createElement('div');
        linkDiv.className = 'social-link-item';
        linkDiv.innerHTML = `
            <div class="social-link-row">
                <select onchange="updateSocialPlatform(${index}, this.value)" class="social-platform-select">
                    <option value="">Select Platform...</option>
                    ${socialPlatforms.map(platform => 
                        `<option value="${platform.name}" ${link.platform === platform.name ? 'selected' : ''}>
                            ${platform.name}
                        </option>`
                    ).join('')}
                </select>
                <input type="url" 
                       placeholder="${getSocialPlaceholder(link.platform)}" 
                       value="${link.url || (link.platform ? getSocialPlaceholder(link.platform) : '')}" 
                       onchange="updateSocialUrl(${index}, this.value)"
                       onfocus="handleInputFocus(this, ${index})"
                       class="social-url-input">
                <button type="button" onclick="removeSocialMediaLink(${index})" class="btn-remove-social">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        container.appendChild(linkDiv);
    });
    
    // Update hidden input
    document.getElementById('social_media').value = JSON.stringify(socialMediaLinks);
    
    // Show/hide add button
    addBtn.style.display = socialMediaLinks.length >= maxSocialLinks ? 'none' : 'block';
}

function updateSocialPlatform(index, platform) {
    socialMediaLinks[index].platform = platform;
    
    // Auto-fill the URL with placeholder template when platform is selected
    if (platform && !socialMediaLinks[index].url) {
        socialMediaLinks[index].url = getSocialPlaceholder(platform);
    }
    
    renderSocialLinks();
}

function updateSocialUrl(index, url) {
    socialMediaLinks[index].url = url;
    
    // Update the hidden input field so changes are saved
    document.getElementById('social_media').value = JSON.stringify(socialMediaLinks);
}

function handleInputFocus(input, index) {
    // If the input contains the placeholder template, select the "username" part
    const placeholder = getSocialPlaceholder(socialMediaLinks[index].platform);
    if (input.value === placeholder) {
        // Select the "username" part for easy replacement
        setTimeout(() => {
            if (placeholder.includes('gamertag=username')) {
                // Xbox special case
                const start = placeholder.indexOf('gamertag=username') + 9; // "gamertag=".length
                const end = start + 'username'.length;
                input.setSelectionRange(start, end);
            } else if (placeholder.includes('@username')) {
                // YouTube case
                const start = placeholder.indexOf('@username') + 1;
                const end = start + 'username'.length;
                input.setSelectionRange(start, end);
            } else if (placeholder.includes('username')) {
                // Standard case
                const start = placeholder.indexOf('username');
                const end = start + 'username'.length;
                input.setSelectionRange(start, end);
            }
        }, 0);
    }
}

function getSocialPlaceholder(platform) {
    const platformData = socialPlatforms.find(p => p.name === platform);
    return platformData ? platformData.placeholder : 'https://...';
}

// Load majors data and initialize Select2
async function initializeMajors() {
    try {
        const response = await fetch('/static/js/majors.json');
        const data = await response.json();
        
        const majorSelect = document.getElementById('major');
        if (majorSelect) {
            // Clear existing options except the first one
            majorSelect.innerHTML = '<option value="">Select Major...</option>';
            
            // Get current major from data attribute
            const currentMajor = majorSelect.dataset.currentMajor || '';
            
            // Add majors from JSON
            data.Majors.forEach(major => {
                const option = document.createElement('option');
                option.value = major.major;
                option.textContent = major.major;
                if (major.major === currentMajor) {
                    option.selected = true;
                }
                majorSelect.appendChild(option);
            });
            
            // Initialize Select2
            $(majorSelect).select2({
                placeholder: 'Search for your major...',
                allowClear: true,
                width: '100%'
            });
        }
    } catch (error) {
        console.error('Error loading majors:', error);
    }
}

// Profile picture preview functionality
function initializeProfilePicturePreview() {
    const fileInput = document.getElementById('profile_picture');
    const previewContainer = document.getElementById('profile-preview');
    const previewImage = document.getElementById('preview-image');
    const previewFilename = document.getElementById('preview-filename');
    
    if (fileInput) {
        fileInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                // Check file type
                if (!file.type.startsWith('image/')) {
                    alert('Please select an image file.');
                    this.value = '';
                    return;
                }
                
                // Check file size (5MB limit)
                if (file.size > 5 * 1024 * 1024) {
                    alert('File size too large. Maximum 5MB allowed.');
                    this.value = '';
                    return;
                }
                
                // Create preview
                const reader = new FileReader();
                reader.onload = function(e) {
                    if (previewImage && previewFilename && previewContainer) {
                        previewImage.src = e.target.result;
                        previewFilename.textContent = file.name;
                        previewContainer.classList.remove('hidden');
                    }
                };
                reader.readAsDataURL(file);
            } else {
                // Hide preview if no file selected
                if (previewContainer) {
                    previewContainer.classList.add('hidden');
                }
            }
        });
    }
}

// Password functionality
function initializePasswordFeatures() {
    const passwordForm = document.getElementById('password-form');
    const newPasswordInput = document.getElementById('new_password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    const strengthIndicator = document.getElementById('password-strength');
    const matchFeedback = document.getElementById('password-match-feedback');

    if (passwordForm) {
        passwordForm.addEventListener('submit', handlePasswordSubmit);
    }

    if (newPasswordInput) {
        newPasswordInput.addEventListener('input', function() {
            showPasswordStrength(this.value);
            validatePasswordMatch();
        });
    }

    if (confirmPasswordInput) {
        confirmPasswordInput.addEventListener('input', validatePasswordMatch);
    }

    function showPasswordStrength(password) {
        if (!strengthIndicator) return;

        if (password.length === 0) {
            strengthIndicator.style.display = 'none';
            return;
        }

        const strength = checkPasswordStrength(password);
        strengthIndicator.className = `password-strength ${strength}`;
        strengthIndicator.style.display = 'block';

        const messages = {
            weak: 'Weak password - Add more characters, numbers, and symbols',
            medium: 'Medium password - Good, but could be stronger',
            strong: 'Strong password - Excellent!'
        };

        strengthIndicator.textContent = messages[strength];
    }

    function checkPasswordStrength(password) {
        let strength = 0;
        const checks = {
            length: password.length >= 8,
            lowercase: /[a-z]/.test(password),
            uppercase: /[A-Z]/.test(password),
            numbers: /\d/.test(password),
            symbols: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };

        strength = Object.values(checks).filter(Boolean).length;

        if (strength < 3) return 'weak';
        if (strength < 5) return 'medium';
        return 'strong';
    }

    function validatePasswordMatch() {
        if (!newPasswordInput || !confirmPasswordInput || !matchFeedback) return;

        const newPassword = newPasswordInput.value;
        const confirmPassword = confirmPasswordInput.value;

        if (confirmPassword.length === 0) {
            matchFeedback.style.display = 'none';
            confirmPasswordInput.setCustomValidity('');
            return;
        }

        if (newPassword === confirmPassword) {
            matchFeedback.className = 'password-feedback success';
            matchFeedback.textContent = 'Passwords match!';
            matchFeedback.style.display = 'block';
            confirmPasswordInput.setCustomValidity('');
        } else {
            matchFeedback.className = 'password-feedback error';
            matchFeedback.textContent = 'Passwords do not match';
            matchFeedback.style.display = 'block';
            confirmPasswordInput.setCustomValidity('Passwords do not match');
        }
    }

    async function handlePasswordSubmit(event) {
        event.preventDefault();

        const formData = new FormData(event.target);
        const data = {
            current_password: formData.get('current_password'),
            new_password: formData.get('new_password'),
            confirm_password: formData.get('confirm_password')
        };

        // Validate client-side first
        if (!data.current_password || !data.new_password || !data.confirm_password) {
            alert('All password fields are required');
            return;
        }

        if (data.new_password.length < 8) {
            alert('New password must be at least 8 characters long');
            return;
        }

        if (data.new_password !== data.confirm_password) {
            alert('New passwords do not match');
            return;
        }

        try {
            const submitButton = event.target.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            submitButton.textContent = 'Changing...';
            submitButton.disabled = true;

            const response = await fetch('/settings/change-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                alert('Password changed successfully!');
                
                // Clear form
                event.target.reset();
                
                // Hide strength indicators
                if (strengthIndicator) strengthIndicator.style.display = 'none';
                if (matchFeedback) matchFeedback.style.display = 'none';
                
                // Close edit mode
                cancelEdit('password');
            } else {
                alert('Error: ' + result.error);
            }
        } catch (error) {
            console.error('Password change error:', error);
            alert('Network error. Please try again.');
        } finally {
            const submitButton = event.target.querySelector('button[type="submit"]');
            submitButton.textContent = 'Change Password';
            submitButton.disabled = false;
        }
    }
}

// Initialize everything when page loads
document.addEventListener('DOMContentLoaded', function() {
    window._initialSocialMediaValue = '';
    const socialInputInit = document.getElementById('social_media');
    if (socialInputInit) {
        window._initialSocialMediaValue = socialInputInit.value;
    }
    // Initialize social media and majors
    initializeSocialMedia();
    initializeMajors();
    initializeProfilePicturePreview();
    initializePasswordFeatures();
});

switchTab(document.querySelector('#user-settings-tab'));
