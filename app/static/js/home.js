const goals_back =  document.getElementById('goals-back');
const add_goal_btn = document.getElementById('add-goal-btn');
const close_goals = document.getElementById('close-goals-form');
const regularGoalBtn = document.getElementById('regular-goal');
const appCountGoalBtn = document.getElementById('app-count-goal');
const regularGoalForm = document.getElementById('regular-goal-form');
const appCountGoalForm = document.getElementById('app-count-goal-form');
const section2 = document.querySelector('.section-2');
const goalTypeContainer = document.querySelector('.goal-type-container');


function goalFormIsVisible() {
    return goals_back.style.display === 'flex';
}

add_goal_btn.addEventListener('click', (e) => {
	goals_back.style.display = 'flex';
	
})


close_goals.addEventListener('click', (e)=>{
	goals_back.style.display = 'none';
	regularGoalForm.classList.remove('active');
	appCountGoalForm.classList.remove('active');
	goalTypeContainer.style.display = 'flex';
})

document.addEventListener('keydown', (e) => {
	if (goalFormIsVisible()){
		if (e.key === "Escape"){
			goals_back.style.display = 'none';
			regularGoalForm.classList.remove('active');
			appCountGoalForm.classList.remove('active');
			goalTypeContainer.style.display = 'flex';
		}
	};
})

// Show Regular Goal Form
regularGoalBtn.addEventListener('click', () => {
    regularGoalForm.classList.add('active');
    appCountGoalForm.classList.remove('active');
    goalTypeContainer.style.display = 'none';
});

// Show Application Target Form
appCountGoalBtn.addEventListener('click', () => {
    appCountGoalForm.classList.add('active');
    regularGoalForm.classList.remove('active');
    goalTypeContainer.style.display = 'none';
});