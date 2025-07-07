let contacts = [];

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

backBtn.addEventListener('click', (e) => {
	e.preventDefault();
	leavePage();
})


addContactBtn.addEventListener('click', (e) => {
	contactForm.classList.remove('hidden');
	addContactBtn.style.display = 'none';
});

cancelContactBtn.addEventListener('click', function() {
        contactForm.classList.add('hidden');
        addContactBtn.style.display = 'flex';
		contacts = [];
		contactsData.value = [];
		clearForm();

       
});

saveContactBtn.addEventListener('click', (e) => {
	e.preventDefault();

	contactForm.classList.add('hidden');
	addContactBtn.style.display = 'flex';

	const contactName = document.getElementById('contact-name').value;
	const contactPosition = document.getElementById('contact-title').value || "Not Assigned";
	const contactEmail = document.getElementById('contact-email').value || "Not Assigned";
	const contactPhone = document.getElementById('contact-phone').value || "Not Assigned";
	const contactLinkedIn = document.getElementById('contact-linkedin').value || "Not Assigned";
	const contactNotes = document.getElementById('contact-notes').value || "Not Assigned";

	const contact = {
		name: contactName,
		position: contactPosition,
		phone: contactPhone,
		email: contactEmail,
		linkedin: contactLinkedIn,
		notes: contactNotes
	};
	
	contacts.push(contact);

	clearForm();
	updateContactsData();
	updateContactsList();

	



})

const updateContactsData = () => {
	contactsData.value = JSON.stringify(contacts);
	console.log(contactsData.value)
}

const updateContactsList = () => {
	
	 if (contacts.length === 0) {
        contactsList.innerHTML = '<p class="no-contacts">No contacts added yet.</p>';
        return;
    }
    
    let html = '';
    contacts.forEach((contact, index) => {
        html += `
            <div class="contacts" data-index="${index}">
                <div class="contact-info">
                    <h4>${contact.name} <i> ${contact.position != 'Not Assigned' ? ` - ${contact.position}` : ''}</i></h4>
                    <button type="button" class="delete-contact" onclick="deleteContact(${index})">
                    	<i class="fas fa-trash"></i>
               		</button>
                </div>
               
            </div>
        `;
    });
    
    contactsList.innerHTML = html;
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
	contactForm.querySelectorAll('input, textarea, select').forEach(el => {
		if (el.type === 'checkbox' || el.type === 'radio') {
			el.checked = false;
		} else {
			el.value = '';
		}
	});
}

const showPopUp = (scenario) => {
	return new Promise((resolve) => {
		console.log('Showing popup for scenario:', scenario);
		popUp.style.display ='flex';

		if (scenario === 'delete'){
			popUpMsg.innerHTML = 'Are you sure you want to delete this contact?';
		} else {
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


// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    updateContactsList();
    updateContactsData();
});