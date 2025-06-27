homeButton = document.getElementById('homeBtn');
applicationButton = document.getElementById('applicationsBtn');
friendsButton = document.getElementById('friendsBtn');
calendarButton = document.getElementById('calendarBtn');

function switchTab(tab) {
	//Remove active class from all tabs
	document.querySelectorAll(".nav-item").forEach(t => t.classList.remove("active"));
	//Add active class to clicked tab
	tab.classList.add("active");
}

// Add click event listeners when page loads
window.addEventListener('DOMContentLoaded', function() {
	const homeButton = document.getElementById('homeBtn');
	const applicationButton = document.getElementById('applicationsBtn');
	const friendsButton = document.getElementById('friendsBtn');
	const calendarButton = document.getElementById('calendarBtn');

	homeButton.addEventListener('click', (e) => {
		e.preventDefault();
		switchTab(homeButton);
	});

	applicationButton.addEventListener('click', (e) => {
		e.preventDefault();
		switchTab(applicationButton);
	});

	friendsButton.addEventListener('click', (e) => {
		e.preventDefault();
		switchTab(friendsButton);
	});

	calendarButton.addEventListener('click', (e) => {
		e.preventDefault();
		switchTab(calendarButton);
	});
});

function getTabFromURL() {
	const urlParams = new URLSearchParams(window.location.search);
	return urlParams.get("tab") || "home";
}

// Logout function
function logout() {
	window.location.href = '/auth/logout';
}

