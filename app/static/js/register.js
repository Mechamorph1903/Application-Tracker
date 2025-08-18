const passwordInput = document.getElementById('password');
const registerForm = document.getElementById('registerForm');
const requirements = {
	length: document.getElementById('length'),
	uppercase: document.getElementById('uppercase'),
	lowercase: document.getElementById('lowercase'),
	number: document.getElementById('number'),
	symbol: document.getElementById('symbol')
	};
const flashMessages = document.querySelectorAll('.flash-message');

passwordInput.addEventListener('input',(e) => {
	const password = e.target.value;

	//cheeeeeck lengthhhhhhh
	if (password.length >= 6){
		requirements.length.classList.add('valid');
		requirements.length.classList.remove('invalid');
	} else {
		requirements.length.classList.add('invalid');
		requirements.length.classList.add('valid');
	}

	//CHECK UPPERCASE
	if (/[A-Z]/.test(password)){
		requirements.uppercase.classList.add('valid');
		requirements.uppercase.classList.remove('invalid');
	} else {
		requirements.uppercase.classList.add('invalid');
		requirements.uppercase.classList.add('valid');
	}

	//check lowercase
	if (/[a-z]/.test(password)){
		requirements.lowercase.classList.add('valid');
		requirements.lowercase.classList.remove('invalid');
	} else {
		requirements.lowercase.classList.add('invalid');
		requirements.lowercase.classList.add('valid');
	}

	//ch3ck d161t5
	if (/\d/.test(password)){
		requirements.number.classList.add('valid');
		requirements.number.classList.remove('invalid');
	} else {
		requirements.number.classList.add('invalid');
		requirements.number.classList.add('valid');
	}

	//check $ymb@ls
	if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)){
		requirements.symbol.classList.add('valid');
		requirements.symbol.classList.remove('invalid');
	} else {
		requirements.symbol.classList.add('invalid');
		requirements.symbol.classList.add('valid');
	}
})

registerForm.addEventListener('submit', function(e) {
	const password = passwordInput.value;

	if (password.length < 6 || !/[A-Z]/.test(password) || !/[a-z]/.test(password) || !/\d/.test(password) || !/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
		e.preventDefault();
		passwordInput.focus();																																																																																					
		return false;
	}
});

//tab switching

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

// flash messages  
flashMessages.forEach(function(message) {
	// Auto-dismiss after 5 seconds
	setTimeout(function() {
	message.classList.add('flash-dismissing');
	setTimeout(function() {
		message.remove();
	}, 300);
	}, 5000);
});