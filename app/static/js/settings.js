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

switchTab(document.querySelector('#user-settings-tab'));
