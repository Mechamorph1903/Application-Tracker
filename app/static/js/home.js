const goals_back =  document.getElementById('goals-back');
const add_goal_btn = document.getElementById('add-goal-btn');
const close_goals = document.getElementById('close-goals-form');

function goalFormIsVisible() {
    return goals_back.style.display === 'flex';
}


add_goal_btn.addEventListener('click', (e) => {
	goals_back.style.display = 'flex';
})


close_goals.addEventListener('click', (e)=>{
	goals_back.style.display = 'none';
})

document.addEventListener('keydown', (e) => {
	if (goalFormIsVisible()){
		if (e.key === "Escape"){
			goals_back.style.display = 'none'
		}
	};
})