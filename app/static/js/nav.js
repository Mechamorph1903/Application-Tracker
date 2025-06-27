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

	// All buttons now have real URLs, so just update visual state and allow navigation
	homeButton.addEventListener('click', () => {
		switchTab(homeButton);
	});

	friendsButton.addEventListener('click', () => {
		switchTab(friendsButton);
	});

	applicationButton.addEventListener('click', () => {
		switchTab(applicationButton);
	});

	calendarButton.addEventListener('click', () => {
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

