# RecruitAI 🤖
### AI-Powered Resume Screening System

RecruitAI is a full-stack web application that automates the resume screening process for HR teams using advanced NLP and transformer-based AI models — eliminating bias, saving time, and surfacing the best candidates instantly.

---

## 🚀 Features

### For HR Recruiters
- Create structured job postings with required skills, optional skills, experience, education, CGPA, job type, and salary range
- Run AI screening on all applicants with one click
- View ranked candidate list with detailed score breakdowns
- Auto-rejection of unqualified candidates (zero skill match or below CGPA cutoff)
- Download PDF reports with full rankings and top 3 candidate breakdowns
- AI Chatbot to query candidate rankings, scores, and details

### For Candidates
- Register, browse job postings, and upload resumes (PDF, DOCX, TXT)
- View personal AI score breakdown after screening
- See detected skills, missing skills, and application status
- AI Chatbot for personalized improvement tips and skill gap analysis

---

## 🧠 AI Scoring Engine (6 Factors)

| Factor | Weight |
|---|---|
| Required Skills Match | 35% |
| BERT Semantic Similarity (all-MiniLM-L6-v2) | 25% |
| Experience Match | 15% |
| Education & CGPA | 15% |
| Optional Skills Bonus | 10% |
| Resume Completeness Bonus | +3% |

---

## 🛠️ Tech Stack

- **Backend:** Python 3.12, Django 4.2
- **AI/NLP:** BERT (sentence-transformers/all-MiniLM-L6-v2), PyTorch
- **Database:** SQLite
- **File Parsing:** PDF, DOCX, TXT resume support
- **Frontend:** Custom bioluminescent dark theme with glowing animations and floating particles
- **Security:** PBKDF2 SHA256 password hashing, 7-rule password validation

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.12+
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/kitto577/RecruitAI.git
cd RecruitAI

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run database migrations
python manage.py migrate

# 5. Start the development server
python manage.py runserver
```

Visit `http://127.0.0.1:8000` in your browser.

---

## 🗄️ Database Models

- **UserProfile** — extended user data for HR and candidates
- **JobPosting** — structured job listings with skill and qualification requirements
- **Candidate** — resume uploads, AI scores, skill analysis, and application status
- **ChatMessage** — chatbot conversation history per user

---

## 📊 Project Structure

```
RecruitAI/
├── manage.py
├── requirements.txt
├── .gitignore
├── core/                  # Main Django app
│   ├── models.py          # 4 custom models
│   ├── views.py           # HR and candidate views
│   ├── ai_engine.py       # 6-factor scoring engine
│   ├── chatbot.py         # Dual chatbot logic
│   └── templates/         # Custom UI templates
└── RecruitAI/             # Django project settings
```

---

## ✨ Highlights

- **BERT-powered semantic matching** — goes beyond keyword matching to understand meaning
- **Dual AI chatbots** — separate bots for HR and candidates with context-aware responses
- **Auto PDF report generation** — downloadable candidate ranking reports
- **Bioluminescent UI** — custom dark theme with glowing effects, floating particles, and custom cursor

---

## 👩‍💻 Author

**Kitto577** — MCA Graduate | AI & Full-Stack Enthusiast  
🔗 [GitHub](https://github.com/kitto577)

---

> *"Most recruiters spend 6 seconds on a resume. RecruitAI spends 6 factors."*
