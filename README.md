# 🎯 Internship Tracker (Flask Web App)

A simple web app to help you track internship applications — whether you’ve applied, are interviewing, or got the job!

---

## 🚀 Features (Coming Soon)
- Add and view internship applications
- Track application status (e.g. applied, interviewing, rejected)
- Receive Reminders about applications (upcoming OAs/Interviews/, No status update for a while...)
- Simple and clean interface using HTML, CSS, and Flask

---

## 🧰 Requirements
- Python 3.8+
- pip

---

## 🛠️ Setup Instructions

### 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/internship-tracker.git
cd internship-tracker
🔁 Replace YOUR_USERNAME with your GitHub username.

### 2. (Optional but Recommended) Create a Virtual Environment
python -m venv venv
source venv/bin/activate     # macOS/Linux
venv\Scripts\activate        # Windows

### 3. Install Requirements
Make sure you're inside the project folder where requirements.txt is located:
pip install -r requirements.txt

---

### 💻 Quick Setup (Optional Script)

For a faster setup, run one of the provided scripts in the path of the project👂🏾:

#### 🔹 On Mac/Linux

./setup.sh

#### 🔹 On Windows

setup.bat

This will:

- Create a virtual environment
- Activate it
- Install all required packages

---

🔹 Activate Virtual Environment (if you have an exisating one):

Make sure you're in the project folder, then run:

✅ On Windows (Command Prompt):

- venv\Scripts\activate

✅ On Windows (PowerShell):

- .\venv\Scripts\Activate.ps1

✅ On Mac/Linux:

- source venv/bin/activate

After activation, you should see the virtual environment name (like (venv)) at the beginning of your terminal line.



### 4. Run the App

python app.py
Visit http://127.0.0.1:5000 in your browser.

---

### 📁 Folder Structure (Base Version)

application_tracker/

├── app/

│   ├── __init__.py ← App factory (creates and configures Flask)

│   ├── models.py ← User & Internship database models

│   ├── routes.py ← (Optional) for organizing API routes

│   ├── templates/ ← HTML templates (Jinja2) — optional

│   └── static/ ← CSS, JS, or images — optional

│

├── internships.db ← Local SQLite database (auto-created)

├── run.py ← Entry point for running the app

├── requirements.txt ← All project dependencies

├── LICENSE ← Apache 2.0 license

├── NOTICE ← Acknowledgments or third-party notices

├── README.md ← Project overview, setup instructions

---

💡 Contributing
Pull requests and improvements are welcome — keep it beginner-friendly and clear for others who want to learn Flask!

🧠 Credits
Built by students, for students — to help you land that internship 🚀
