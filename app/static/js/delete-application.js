const deleteBtn =  document.getElementById('delete');
const popUp = document.getElementById('pop-up-back');
const popUpMsg = document.getElementById('pop-up-message');
const popUpCancel = document.getElementById('pop-up-cancel');
const popUpYes = document.getElementById('yes');
const popUpNo = document.getElementById('no');

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

document.addEventListener('DOMContentLoaded', (e) => {
	if(deleteBtn) {
		deleteBtn.addEventListener('click', (e) => {
            e.preventDefault();
            deleteApplication();
        });
	}
});	