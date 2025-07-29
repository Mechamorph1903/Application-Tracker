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

document.querySelectorAll('.complete-goal-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const li = this.closest('.goal-item');
        const goalId = li.dataset.goalId;
        
        // Send AJAX request to complete the goal
        fetch('/complete_goal', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `goal_id=${goalId}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Reload the page to show the updated goals
                window.location.reload();
            } else {
                console.error('Error completing goal:', data.error);
                alert('Error completing goal. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error completing goal. Please try again.');
        });
    });
});

document.querySelectorAll('.cancel-goal-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const li = this.closest('.goal-item');
        const goalId = li.dataset.goalId;
        
        if (confirm('Are you sure you want to cancel this goal?')) {
            // Send AJAX request to remove the goal
            fetch('/remove_goal', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `goal_id=${goalId}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Remove the goal item with animation
                    li.style.transform = 'translateX(-100%)';
                    li.style.opacity = '0';
                    setTimeout(() => {
                        li.remove();
                        // Check if this was the last goal in the section
                        const goalsList = li.closest('.goals-list');
                        if (goalsList.children.length === 0) {
                            window.location.reload();
                        }
                    }, 300);
                } else {
                    console.error('Error removing goal:', data.error);
                    alert('Error canceling goal. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error canceling goal. Please try again.');
            });
        }
    });
});

document.querySelectorAll('.remove-goal-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const li = this.closest('.goal-item');
        const goalId = li.dataset.goalId;
        
        if (confirm('Are you sure you want to remove this completed goal?')) {
            // Send AJAX request to remove the goal
            fetch('/remove_goal', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `goal_id=${goalId}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Remove the goal item with animation
                    li.style.transform = 'translateX(-100%)';
                    li.style.opacity = '0';
                    setTimeout(() => {
                        li.remove();
                        // Check if this was the last goal in the section
                        const goalsList = li.closest('.goals-list');
                        if (goalsList.children.length === 0) {
                            window.location.reload();
                        }
                    }, 300);
                } else {
                    console.error('Error removing goal:', data.error);
                    alert('Error removing goal. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error removing goal. Please try again.');
            });
        }
    });
});