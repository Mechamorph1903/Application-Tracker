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
    
    if (!contactsData) {
        contacts = [];
        return;
    }
    
    const rawValue = contactsData.value;
    
    if (rawValue && rawValue.trim() !== '' && rawValue !== '[]' && rawValue !== 'null') {
        try {
            // Parse the JSON data from the hidden input
            const parsedContacts = JSON.parse(rawValue);
            contacts = Array.isArray(parsedContacts) ? parsedContacts : [];
        } catch (error) {
            console.error('Error parsing contacts data:', error);
            console.error('Raw data was:', rawValue);
            
            // Fallback: Try to convert Python format to JSON
            try {
                
                // Convert Python single quotes to JSON double quotes
                let jsonData = rawValue
                    .replace(/'/g, '"')        // Replace single quotes with double quotes
                    .replace(/True/g, 'true')  // Convert Python True to JSON true
                    .replace(/False/g, 'false') // Convert Python False to JSON false
                    .replace(/None/g, 'null'); // Convert Python None to JSON null
                
                console.log('Converted to JSON format:', jsonData);
                
                const parsedContacts = JSON.parse(jsonData);
                contacts = Array.isArray(parsedContacts) ? parsedContacts : [];
                
            } catch (conversionError) {
                console.error('Failed to convert Python format to JSON:', conversionError);
                contacts = [];
            }
        }
    } else {
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

        // Get LinkedIn URL and ensure it has https://
        let contactLinkedIn = document.getElementById('contact-linkedin')?.value || "Not Assigned";
        if (contactLinkedIn !== "Not Assigned" && !contactLinkedIn.startsWith('http')) {
            contactLinkedIn = 'https://' + contactLinkedIn;
        }

        const contact = {
            name: contactName ? toTitleCase(contactName) : "Not Assigned",
            position: document.getElementById('contact-title')?.value || "Not Assigned",
            phone: document.getElementById('contact-phone')?.value || "Not Assigned",
            email: document.getElementById('contact-email')?.value || "Not Assigned",
            linkedin: contactLinkedIn,
            notes: document.getElementById('contact-notes')?.value || "Not Assigned"
        };
        
        contacts.push(contact);

        clearForm();
        updateContactsData();
        updateContactsList();
        
    });
}

const updateContactsData = () => {
    if (contactsData) {
        const jsonString = JSON.stringify(contacts);
        contactsData.value = jsonString;
    } else {
        console.error('contactsData element not found - cannot update hidden field!');
    }
}

const updateContactsList = () => {
    
    if (!contactsList) {
        console.log('contactsList element not found');
        return;
    }
    
    if (contacts.length === 0) {
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
            const confirmed = await showPopUp('leave');
            if (confirmed) {
                window.history.back();
            }
        } else {
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
        
        // Make sure contacts data is updated before submission
        updateContactsData();
                
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

    if (mOverlay) {
        showMaduka();
    }
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

document.addEventListener('DOMContentLoaded', function() {
    const linkInput = document.querySelector('input[name="link"]');
    if (linkInput) {
        linkInput.addEventListener('blur', function() {
            if (this.value && !this.value.startsWith('http')) {
                this.value = 'https://' + this.value;
            }
        });
    }
});



//Auto PArsing JS aka MAduka
const mOverlay = document.getElementById("maduka-overlay");

    const mScreen1_Choice = document.getElementById("maduka-screen1");
    const mScreen2_Link = document.getElementById("maduka-screen2");
    const mScreen3Bad_Result = document.getElementById("maduka-screen3");
    const mAutofill_Choice = document.getElementById("maduka-auto-btn");
    const mManual_Choice = document.getElementById("maduka-manual-entry-btn");
    const mURL_Input = document.getElementById("maduka-url-input");
    const mFetch = document.getElementById("maduka-fetch-btn");
    const mErrorDisplay = document.getElementById("maduka-error-reason");
    const mRetry_Result = document.getElementById("maduka-retry-btn");
    const mManual_Result = document.getElementById("maduka-fallback-btn");
    const mloading_screen = document.getElementById("loading_screen");
    const mScreen2_main = document.getElementById("screen2_main");
    const warn = document.getElementById("warn");
    const case1 = document.getElementById("dot1");
    const case2 = document.getElementById("dot2");
    const case_div = document.querySelector(".elements_div");
    const heart = document.querySelector("#heart")
    const fetch_text = document.getElementById("fetch-text");
    const mCancel = document.getElementById("maduka-cancel");
    const mAuto = document.getElementById("auto-btn");


let job_details = null;
let successhandled = false;
let failHandled = false;

function showMaduka() {
    mOverlay.style.opacity = '0'
    mOverlay.style.display = 'flex'
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            mOverlay.style.opacity = '1'
        })
    })
}

function closeMaduka() {
    mOverlay.style.opacity = '0'
    
    const onClose = (e) => {
        if (e.target === mOverlay && e.propertyName === 'opacity') {
            mOverlay.style.display = 'none'
            mOverlay.style.opacity = '1' //show for next opening
            case_div.classList.remove("success-anim")
            case_div.classList.remove("flying")
            case_div.classList.remove("failed")
            case_div.classList.remove("show-heart")
            fetch_text.innerHTML = `Fetching details<span>.</span><span>.</span><span>.</span>`
            mScreen2_Link.style.opacity = '1'
            mScreen3Bad_Result.style.opacity = '1'
            successhandled = false
            failHandled = false
            job_details = null
            mURL_Input.value = ''
            showMadukaScreen(0)  // back to screen 1
            mOverlay.removeEventListener('transitionend', onClose)
        }
    }
    mOverlay.addEventListener('transitionend', onClose)
}

function showMadukaScreen(screen_no) {
    mScreen1_Choice.style.display = 'none';
    mScreen2_Link.style.display = 'none';
    mScreen3Bad_Result.style.display = 'none';
    mloading_screen.style.display = 'none';
    mScreen2_main.style.display = 'none'

    switch(screen_no) {
        case 2:
            mScreen2_Link.style.display = 'flex';
            mScreen2_main.style.display = 'flex';
            break;
        case 3:
            mScreen3Bad_Result.style.display = 'flex';
            break;
        case 4:
            mScreen2_Link.style.display = 'flex';
            mloading_screen.style.display = 'flex';
            break;
        default:
            mScreen1_Choice.style.display = 'flex';
    }
}

function triggerSuccess(){
    console.log('case_div:', case_div)
    console.log('case1:', case1)
    case_div.classList.add("success-anim");
    fetch_text.innerText = `Details Found!`

    case1.addEventListener("transitionend", (e) => {
        if (e.propertyName === 'opacity' && !successhandled){
            successhandled = true;
            console.log('dots faded, ready for next phase');
            case_div.classList.add('flying')
        }
    }, { once: true })

    case2.addEventListener('animationend', (e) =>{
        if (e.animationName === "flyUp"){
            prefillForm();
            closeMaduka();
            console.log('sky high, now for the finale');

        }
    },{ once: true })

    return;
}


function triggerFail() {
    case_div.classList.add("failed");
    fetch_text.innerText = "Fetch Unsuccessful";

    case1.addEventListener("transitionend", (e) => {
        if (e.propertyName === "opacity" && !failHandled) {
            failHandled = true;
            case_div.classList.add("show-heart");
        }
    }, { once: true });

    heart.addEventListener("transitionend", (e) => {
        if (e.propertyName === "opacity"){
            setTimeout(() => fadeToScreen3(), 2000)
        }
    }, { once: true })

    
}

function prefillForm(){
    // DOM filling eith jobe details
    if (!job_details){
        return 
    }

    document.querySelector('input[name="app_name"]').value = job_details.job_name || '';
    document.querySelector('input[name="company"]').value = job_details.company_name || '';
    document.querySelector('input[name="location"]').value = job_details.location || '';
    document.querySelector('input[name="role"]').value = job_details.role_name || '';
    document.querySelector('input[name="link"]').value = mURL_Input.value.trim();
    document.querySelector('textarea[name="description"]').value = job_details.job_description || '';

    if (job_details.work_arrangement) {
        const arrangement = job_details.work_arrangement.toLowerCase();
        const jobTypeSelect = document.querySelector('select[name="job_type"]');
        if (arrangement === 'remote') jobTypeSelect.value = 'remote'
        else if (arrangement === 'hybrid') jobTypeSelect.value = 'hybrid'
        else jobTypeSelect.value = 'on-site';
    }

    if (job_details.deadline) {
        try {
            const d = new Date(job_details.deadline)
            if (!isNaN(d)) {
                document.querySelector('input[name="deadline_date"]').value =
                    d.toISOString().split('T')[0]
            }
        } catch(e) {}
    }
}

mAuto.addEventListener("click", showMaduka)
mCancel.addEventListener("click", closeMaduka)


mAutofill_Choice.addEventListener("click",(e) => {
    console.log("been clicked idk wagwan")
    showMadukaScreen(2);
    return;
})


mManual_Choice.addEventListener("click", (e) => {
    closeMaduka();
})

mFetch.addEventListener("click", async (e) => {
    const value = mURL_Input.value;
    warn.innerText = ``;
    if (!value){
        warn.innerText = `Please provide a valid link`;
        return;
    }

    showMadukaScreen(4);

    const response = await fetch('/applications/parse-job', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: mURL_Input.value.trim() })
    })

    const data = await response.json();

    

    if (!data || !data.status){
        mErrorDisplay.innerText = data?.reason || 'Something went wrong'
        triggerFail();
        return;
    }
    job_details = data;
    triggerSuccess();

    return;
})


mRetry_Result.addEventListener("click", (e) => {
    case_div.classList.remove("show-heart");
    case_div.classList.remove("failed");
    fetch_text.innerHTML = `Fetching details<span>.</span><span>.</span><span>.</span>`;
    case_div.classList.remove("success-anim");
    case_div.classList.remove("success-anim");
    failHandled = false;
    successhandled = false;
    mScreen2_Link.style.opacity = '1';

    showMadukaScreen(2);
    return;
})

mManual_Result.addEventListener("click", (e) => {
    closeMaduka();
    return;
})


function fadeToScreen3(){
    mScreen2_Link.style.opacity = '0';

    mScreen2_Link.addEventListener('transitionend', (e) => {
        if (e.propertyName === "opacity"){
            mScreen2_Link.style.display = 'none'
            mScreen3Bad_Result.style.display = 'flex'
            mScreen3Bad_Result.style.opacity = '0';

            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    mScreen3Bad_Result.style.opacity = '1'
                })
            })
        }
    }, { once: true })
}