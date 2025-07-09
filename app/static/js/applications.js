let contacts = [];

// Helper function for proper title case
function toTitleCase(str) {
    return str.replace(/\w\S*/g, (txt) => {
        return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    });
}

// Helper function for lowercase (used in display)
function toLower(str) {
    return str.toLowerCase();
}

const addContactBtn = document.getElementById('add-contact-btn');
const contactForm = document.getElementById('contact-form');
const cancelContactBtn = document.getElementById('cancel-contact');
const saveContactBtn = document.getElementById('save-contact');
const contactsList = document.getElementById('contacts-list');
const contactsData = document.getElementById('contacts-data');
const backBtn = document.getElementById('back-btn');
const popUp = document.getElementById('pop-up-back');
const popUpMsg = document.getElementById('pop-up-message');
const popUpCancel = document.getElementById('pop-up-cancel');
const popUpYes = document.getElementById('yes');
const popUpNo = document.getElementById('no');

const initializeContacts = () => {
    console.log('Initializing contacts...');
    
    if (!contactsData) {
        console.log('contactsData element not found');
        contacts = [];
        return;
    }
    
    const rawValue = contactsData.value;
    console.log('Raw contacts data:', rawValue);
    console.log('Type of raw value:', typeof rawValue);
    console.log('Raw value length:', rawValue.length);
    
    if (rawValue && rawValue.trim() !== '' && rawValue !== '[]' && rawValue !== 'null') {
        try {
            // Parse the JSON data from the hidden input
            const parsedContacts = JSON.parse(rawValue);
            contacts = Array.isArray(parsedContacts) ? parsedContacts : [];
            console.log('Successfully loaded contacts from database:', contacts);
        } catch (error) {
            console.error('Error parsing contacts data:', error);
            console.error('Raw data was:', rawValue);
            
            // Fallback: Try to convert Python format to JSON
            try {
                console.log('Attempting to convert Python format to JSON...');
                
                // Convert Python single quotes to JSON double quotes
                let jsonData = rawValue
                    .replace(/'/g, '"')        // Replace single quotes with double quotes
                    .replace(/True/g, 'true')  // Convert Python True to JSON true
                    .replace(/False/g, 'false') // Convert Python False to JSON false
                    .replace(/None/g, 'null'); // Convert Python None to JSON null
                
                console.log('Converted to JSON format:', jsonData);
                
                const parsedContacts = JSON.parse(jsonData);
                contacts = Array.isArray(parsedContacts) ? parsedContacts : [];
                console.log('Successfully converted and loaded contacts:', contacts);
                
            } catch (conversionError) {
                console.error('Failed to convert Python format to JSON:', conversionError);
                contacts = [];
            }
        }
    } else {
        console.log('No contacts data found or empty, starting with empty array');
        contacts = [];
    }
};

if (backBtn) {
    backBtn.addEventListener('click', (e) => {
        e.preventDefault();
        leavePage();
    });
}

if (addContactBtn) {
    addContactBtn.addEventListener('click', (e) => {
        if (contactForm) {
            contactForm.classList.remove('hidden');
            addContactBtn.style.display = 'none';
        }
    });
}

if (cancelContactBtn) {
    cancelContactBtn.addEventListener('click', function() {
        if (contactForm && addContactBtn) {
            contactForm.classList.add('hidden');
            addContactBtn.style.display = 'flex';
            clearForm(); // Only clear the form, keep saved contacts!
        }
    });
}

if (saveContactBtn) {
    saveContactBtn.addEventListener('click', (e) => {
        e.preventDefault();

        // Get and validate form values
        const contactNameInput = document.getElementById('contact-name');
        let contactName = contactNameInput ? contactNameInput.value.trim() : '';
        
        // Only validate when user is trying to save a contact
        if (!contactName) {
            alert('Contact name is required when adding a contact!');
            return;
        }

        if (contactForm && addContactBtn) {
            contactForm.classList.add('hidden');
            addContactBtn.style.display = 'flex';
        }

        const contactTitleInput = document.getElementById('contact-title');
        const contactEmailInput = document.getElementById('contact-email');
        const contactPhoneInput = document.getElementById('contact-phone');
        const contactLinkedInInput = document.getElementById('contact-linkedin');
        const contactNotesInput = document.getElementById('contact-notes');

        const contactTitle = contactTitleInput ? contactTitleInput.value.trim() : '';
        const contactEmail = contactEmailInput ? contactEmailInput.value : "Not Assigned";
        const contactPhone = contactPhoneInput ? contactPhoneInput.value : "Not Assigned";
        const contactLinkedIn = contactLinkedInInput ? contactLinkedInInput.value : "Not Assigned";
        const contactNotes = contactNotesInput ? contactNotesInput.value : "Not Assigned";

        const contact = {
            name: contactName ? toTitleCase(contactName) : "Not Assigned",
            position: contactTitle || "Not Assigned",
            phone: contactPhone,
            email: contactEmail,
            linkedin: contactLinkedIn,
            notes: contactNotes
        };
        
        contacts.push(contact);
        
        console.log('Contact added:', contact);
        console.log('Updated contacts array:', contacts);

        clearForm();
        updateContactsData();
        updateContactsList();
        
        console.log('After updating - contacts array length:', contacts.length);
    });
}

const updateContactsData = () => {
    if (contactsData) {
        const jsonString = JSON.stringify(contacts);
        contactsData.value = jsonString;
        console.log('Updated contacts data in hidden field:', jsonString);
        console.log('Hidden field now contains:', contactsData.value);
    } else {
        console.error('contactsData element not found - cannot update hidden field!');
    }
}

const updateContactsList = () => {
    console.log('updateContactsList called, contacts array:', contacts);
    console.log('contacts.length:', contacts.length);
    
    if (!contactsList) {
        console.log('contactsList element not found');
        return;
    }
    
    if (contacts.length === 0) {
        console.log('No contacts to display, showing "no contacts" message');
        contactsList.innerHTML = '<p class="no-contacts">No contacts added yet.</p>';
        return;
    }
    
    console.log('Building HTML for', contacts.length, 'contacts');
    let html = '';
    contacts.forEach((contact, index) => {
        console.log('Processing contact', index, ':', contact);
        html += `
            <div class="contacts" data-index="${index}">
                <div class="contact-info">
                    <h4>${toLower(contact.name)} <i> ${contact.position != 'Not Assigned' ? ` - ${toLower(contact.position)}` : ''}</i></h4>
                    <button type="button" class="delete-contact" onclick="deleteContact(${index})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    });
    
    console.log('Setting contactsList innerHTML to:', html);
    contactsList.innerHTML = html;
    console.log('contactsList updated successfully');
}

window.deleteContact = async function(index) {
	 try {
        const confirmed = await showPopUp('delete');
        if (confirmed) {
            contacts.splice(index, 1);
            updateContactsList();
            updateContactsData();
            console.log(`Contact at index ${index} deleted`);
        }
    } catch (error) {
        console.error('Error deleting contact:', error);
    }
}

const clearForm = () => {
    if (contactForm) {
        contactForm.querySelectorAll('input, textarea, select').forEach(el => {
            if (el.type === 'checkbox' || el.type === 'radio') {
                el.checked = false;
            } else {
                el.value = '';
            }
        });
    }
}

const showPopUp = (scenario) => {
	return new Promise((resolve) => {
		console.log('Showing popup for scenario:', scenario);
		popUp.style.display ='flex';

		if (scenario === 'delete'){
			popUpMsg.innerHTML = 'Are you sure you want to <strong class="delete-indicator">DELETE</strong> this contact?';
		} else if (scenario === 'delete-application'){
			popUpMsg.innerHTML = 'Are you sure you want to <strong class="delete-indicator">DELETE</strong> this application?';

		} 
		else {
			popUpMsg.innerHTML = 'Are you sure you want to leave? Unsaved changes will be lost.'
		}

		const handleResponse = (result) => {
			closePopUp();
			resolve(result);
		};

		popUpCancel.onclick = null;
        popUpNo.onclick = null;
        popUpYes.onclick = null;

		popUpCancel.onclick = () => handleResponse(false);
		popUpNo.onclick = () => handleResponse(false);
		popUpYes.onclick = () => handleResponse(true);

		document.getElementById('pop-up-back').onclick = (e) => {
            if (e.target === document.getElementById('pop-up-back')) {
                handleResponse(false);
            }
        };
	});
};

const closePopUp = () => {
	popUp.style.display = 'none';

	popUpCancel.onclick = null;
    popUpNo.onclick = null;
    popUpYes.onclick = null;
    document.getElementById('pop-up-back').onclick = null;
}

const leavePage = async () => {
    try {
        // Check if form has data
        let hasData = false;
        
        // Check main form fields
 			const formInputs = document.querySelectorAll('.add-form form input, .add-form form textarea');        
			formInputs.forEach(input => {
				if (input.type === 'hidden') return; // Skip hidden inputs
				if (input.value && input.value.trim() !== '') {
					console.log('Found data in:', input.name, input.value);
					hasData = true;
				}
        	});
		
        // Check if there are contacts
        if (contacts.length > 0) {
            hasData = true;
        }
        
        if (hasData) {
            console.log('Form has data, showing confirmation');
            const confirmed = await showPopUp('leave');
            if (confirmed) {
                window.history.back();
            }
        } else {
            console.log('Form is empty, leaving immediately');
            window.history.back();
        }
    } catch (error) {
        console.error('Error in leavePage:', error);
        // Fallback - just go back
        window.history.back();
    }
};


// Next Action Handling
document.addEventListener('DOMContentLoaded', function() {
    const nextActionSelect = document.getElementById('next_action');
    const nextActionDate = document.getElementById('next_action_date');
    
    if (nextActionSelect && nextActionDate) {
        // Handle next action selection change
        nextActionSelect.addEventListener('change', function() {
            if (this.value === '') {
                nextActionDate.value = '';
                nextActionDate.disabled = true;
            } else {
                nextActionDate.disabled = false;
                // If no date is set, set to current date/time
                if (!nextActionDate.value) {
                    const now = new Date();
                    const year = now.getFullYear();
                    const month = String(now.getMonth() + 1).padStart(2, '0');
                    const day = String(now.getDate()).padStart(2, '0');
                    const hours = String(now.getHours()).padStart(2, '0');
                    const minutes = String(now.getMinutes()).padStart(2, '0');
                    nextActionDate.value = `${year}-${month}-${day}T${hours}:${minutes}`;
                }
            }
        });
        
        // Initialize on page load
        if (nextActionSelect.value === '') {
            nextActionDate.disabled = true;
        }
    }
});

// Add validation to ensure action and date are consistent
const form = document.querySelector('form');
if (form) {
    // Add form submission handler to ensure contacts data is updated
    form.addEventListener('submit', function(e) {
        console.log('Form is being submitted...');
        console.log('Current contacts array:', contacts);
        
        // Make sure contacts data is updated before submission
        updateContactsData();
        
        console.log('Contacts data in hidden field:', contactsData ? contactsData.value : 'contactsData not found');
        
        const nextActionElement = document.getElementById('next_action');
        const nextActionDateElement = document.getElementById('next_action_date');
        
        if (nextActionElement && nextActionDateElement) {
            const nextAction = nextActionElement.value;
            const nextActionDate = nextActionDateElement.value;
            
            if (nextAction && !nextActionDate) {
                e.preventDefault();
                alert('Please select a date for the next action or remove the action selection.');
                return false;
            }
            
            if (!nextAction && nextActionDate) {
                e.preventDefault();
                alert('Please select an action type for the scheduled date or remove the date.');
                return false;
            }
        }
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
	initializeContacts();
    updateContactsList();
    updateContactsData();
});

// Application Status Handling
document.addEventListener('DOMContentLoaded', function() {
    const statusSelect = document.getElementById('application_status');
    const nextActionSelect = document.getElementById('next_action');
    const nextActionDate = document.getElementById('next_action_date');
    
    if (statusSelect) {
        const originalStatus = statusSelect.value;
        
        // Handle status change
        statusSelect.addEventListener('change', function() {
            // Add visual indicator that status changed
            if (this.value !== originalStatus) {
                this.classList.add('status-changed');
            } else {
                this.classList.remove('status-changed');
            }
            
            // Auto-suggest next actions based on status
            if (nextActionSelect) {
                if (this.value === 'applied') {
                    // Suggest follow-up for applied status
                    if (!nextActionSelect.value) {
                        nextActionSelect.value = 'follow_up';
                        if (nextActionDate && !nextActionDate.value) {
                            // Set follow-up date to 1 week from now
                            const nextWeek = new Date();
                            nextWeek.setDate(nextWeek.getDate() + 7);
                            const year = nextWeek.getFullYear();
                            const month = String(nextWeek.getMonth() + 1).padStart(2, '0');
                            const day = String(nextWeek.getDate()).padStart(2, '0');
                            nextActionDate.value = `${year}-${month}-${day}T09:00`;
                            nextActionDate.disabled = false;
                        }
                    }
                } else if (this.value === 'interview') {
                    // Clear next action if status is already interview
                    if (nextActionSelect.value === 'interview') {
                        nextActionSelect.value = '';
                        if (nextActionDate) {
                            nextActionDate.value = '';
                            nextActionDate.disabled = true;
                        }
                    }
                } else if (this.value === 'rejected' || this.value === 'accepted') {
                    // Clear next action for final statuses
                    nextActionSelect.value = '';
                    if (nextActionDate) {
                        nextActionDate.value = '';
                        nextActionDate.disabled = true;
                    }
                }
                
                // Trigger the next action change event
                nextActionSelect.dispatchEvent(new Event('change'));
            }
        });
    }
});

// Add status validation
const statusForm = document.querySelector('form');
if (statusForm) {
    statusForm.addEventListener('submit', function(e) {
        const statusElement = document.getElementById('application_status');
        const nextActionElement = document.getElementById('next_action');
        
        if (statusElement && nextActionElement) {
            const status = statusElement.value;
            const nextAction = nextActionElement.value;
            
            // Warn if status and next action seem inconsistent
            if (status === 'rejected' || status === 'accepted') {
                if (nextAction) {
                    const confirmSubmit = confirm(`You have selected "${status}" status but also scheduled a "${nextAction}". Are you sure this is correct?`);
                    if (!confirmSubmit) {
                        e.preventDefault();
                        return false;
                    }
                }
            }
            
            if (status === 'interview' && nextAction === 'interview') {
                const confirmSubmit = confirm('Your status is already "Interview" and you\'re scheduling another interview. Is this correct?');
                if (!confirmSubmit) {
                    e.preventDefault();
                    return false;
                }
            }
        }
    });
}