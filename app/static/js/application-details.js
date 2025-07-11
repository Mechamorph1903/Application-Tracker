const deleteBtn =  document.getElementById('delete');
const popUp = document.getElementById('pop-up-back');
const popUpMsg = document.getElementById('pop-up-message');
const popUpCancel = document.getElementById('pop-up-cancel');
const popUpYes = document.getElementById('yes');
const popUpNo = document.getElementById('no');
const notesContainer = document.getElementById('notes-content');
const notesForm = document.getElementById('notes-form');
const notes =  document.getElementById('internship-notes');
const txtarea = document.getElementById('notes');
const forget = document.getElementById('forget');
const update = document.getElementById('update');


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


const deleteApplication = async () => {
	try{
		const confirmed = await showPopUp('delete-application');
	if (confirmed) {
		const internshipId = getInternshipId();

		if(internshipId){

			const originalHTML = deleteBtn.innerHTML;
            deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
			deleteBtn.disabled = true;


			const form = document.createElement('form');
			form.method = "POST";
			form.action = `/applications/delete/${internshipId}`;

			document.body.appendChild(form);
			form.submit();
		} else{
			console.error('Could not find internship ID');
            alert('Error: Could not identify the application to delete');
		}
	}
	} catch(error){
		console.error('Error in deleteApplication:', error);
        alert('An error occurred while trying to delete the application');
	}

}

const getInternshipId = () => {
	console.log('deleteBtn element:', deleteBtn);
    console.log('deleteBtn dataset:', deleteBtn ? deleteBtn.dataset : 'null');
    
    if (deleteBtn && deleteBtn.dataset.internshipId) {
        return deleteBtn.dataset.internshipId;
    }
	return null;
}

const editNotes = () => {
    notesContainer.style.display = 'none';
    notesForm.style.display = 'block';

    currentNotes = notes?.innerText || '';
    txtarea.value = currentNotes;
    
    // Auto-focus the textarea and move cursor to end
    txtarea.focus();
    txtarea.setSelectionRange(txtarea.value.length, txtarea.value.length);
};

	// Description modal functions
		function showDescription() {
			document.getElementById('description-modal').style.display = 'flex';
		}
		
		function hideDescription() {
			document.getElementById('description-modal').style.display = 'none';
		}
		
		// Close modal when clicking outside
		document.getElementById('description-modal').addEventListener('click', function(e) {
			if (e.target === this) {
				hideDescription();
			}
		});
		
		// Close modal with Escape key
		document.addEventListener('keydown', function(e) {
			if (e.key === 'Escape' && document.getElementById('description-modal').style.display === 'flex') {
				hideDescription();
			}
		});


// Move the event listeners outside and add them once when page loads
document.addEventListener('DOMContentLoaded', (e) => {
    if(deleteBtn) {
        deleteBtn.addEventListener('click', (e) => {
            e.preventDefault();
            deleteApplication();
        });
    }
    
    // Add the cancel button event listener
    if(forget) {
        forget.addEventListener('click', () => {
            notesContainer.style.display = 'block';
            notesForm.style.display = 'none';
        });
    }
    
    // Add the form submission event listener
    if(notesForm) {
        notesForm.addEventListener('submit', async (e) => {
            e.preventDefault(); // Fixed: Added parentheses
            
            const formData = new FormData(e.target);
            const notes = formData.get('notes');
            
            try {
                const response = await fetch(e.target.action, {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    const notesDisplay = document.getElementById('internship-notes');
                    if (notes.trim()) {
                        notesDisplay.innerText = notes;
                    } else {
                        notesDisplay.innerText = 'No Notes.';
                    }
                    
                    notesContainer.style.display = 'block';
                    notesForm.style.display = 'none';
                    
                    console.log('Notes updated successfully!');
                } else {
                    alert('Error updating notes');
                }
                
            } catch(error) {
                console.error('Error:', error);
                alert('Error updating notes');
            }
        });
    }
});