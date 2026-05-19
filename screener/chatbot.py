"""
RecruitAI Chatbot — Real World Intent Detection
Handles both HR mode and Candidate mode
"""

# ── Intent definitions ────────────────────────────────────────────
INTENTS = [

    # ── HR Intents ────────────────────────────────────────────────
    {'name': 'top_candidate',
     'keywords': ['top candidate', 'best candidate', 'highest score', 'rank 1',
                  'number one', 'who is best', 'who is top', 'best match',
                  'highest match', 'first rank', 'topper']},

    {'name': 'show_rankings',
     'keywords': ['show ranking', 'show all', 'list candidate', 'all candidate',
                  'rank list', 'ranking', 'candidates list', 'show candidates',
                  'all applicant', 'leaderboard']},

    {'name': 'average_score',
     'keywords': ['average score', 'avg score', 'mean score', 'overall score',
                  'average match', 'typical score']},

    {'name': 'shortlisted',
     'keywords': ['shortlist', 'shortlisted', 'selected candidate', 'who is selected',
                  'approved', 'who passed', 'qualified']},

    {'name': 'rejected',
     'keywords': ['rejected', 'auto rejected', 'failed', 'disqualified',
                  'who failed', 'not selected', 'rejected candidate']},

    {'name': 'count_candidates',
     'keywords': ['how many candidate', 'total candidate', 'count candidate',
                  'number of candidate', 'how many applied', 'total applicant',
                  'how many resume']},

    {'name': 'how_scoring',
     'keywords': ['how scoring work', 'how score', 'scoring system', 'how calculate',
                  'how ai work', 'how does ai', 'scoring formula', 'how rating',
                  'how does scoring', 'explain score', 'what is scoring']},

    {'name': 'download_report',
     'keywords': ['download report', 'pdf report', 'export report', 'get report',
                  'generate report', 'report download', 'recruitment report']},

    {'name': 'required_skills',
     'keywords': ['required skill', 'must have skill', 'mandatory skill',
                  'skill requirement', 'what skill needed', 'job skill']},

    {'name': 'pending_candidates',
     'keywords': ['pending', 'pending candidate', 'not reviewed', 'awaiting review',
                  'pending review', 'not screened']},

    {'name': 'candidate_skills',
     'keywords': ['candidate skill', 'who has', 'skill of candidate',
                  'which candidate know', 'skill distribution']},

    # ── Candidate Intents ─────────────────────────────────────────
    {'name': 'my_score',
     'keywords': ['my score', 'my result', 'my match', 'how did i do',
                  'what is my score', 'my percentage', 'my rating',
                  'my performance', 'check my score']},

    {'name': 'my_skills',
     'keywords': ['my skill', 'what skill', 'skill detected', 'found skill',
                  'skills on my resume', 'what did you find']},

    {'name': 'missing_skills',
     'keywords': ['missing skill', 'skill gap', 'what to add', 'lacking skill',
                  'which skill missing', 'skill i need', 'what skill should i add',
                  'improve skill', 'gap analysis']},

    {'name': 'improve_resume',
     'keywords': ['improve', 'how to improve', 'better resume', 'increase score',
                  'tips', 'suggestion', 'recommendation', 'how to get better',
                  'boost score', 'what to do']},

    {'name': 'application_status',
     'keywords': ['my status', 'application status', 'any update', 'am i selected',
                  'did i pass', 'result', 'my application', 'what happened',
                  'am i shortlisted', 'did i get selected']},

    {'name': 'what_is_bert',
     'keywords': ['what is bert', 'bert model', 'semantic matching', 'semantic',
                  'transformer', 'embedding', 'how ai understand', 'nlp',
                  'what is semantic', 'how does ai read']},

    {'name': 'what_is_required_skills',
     'keywords': ['what is required skill', 'required skill meaning', 'must have',
                  'why required skill', 'what are required']},

    {'name': 'cgpa_impact',
     'keywords': ['cgpa', 'percentage impact', 'does cgpa matter', 'marks matter',
                  'academic score', 'how cgpa', 'gpa impact', 'education score']},

    {'name': 'experience_impact',
     'keywords': ['experience score', 'how experience', 'years matter',
                  'does experience matter', 'fresher score', 'work experience']},

    # ── General ───────────────────────────────────────────────────
    {'name': 'greeting',
     'keywords': ['hello', 'hi', 'hey', 'good morning', 'good evening',
                  'good afternoon', 'namaste', 'hii', 'helo']},

    {'name': 'help',
     'keywords': ['help', 'what can you do', 'commands', 'options', 'menu',
                  'what can i ask', 'guide', 'features']},

    {'name': 'thanks',
     'keywords': ['thank', 'thanks', 'thank you', 'great', 'awesome',
                  'perfect', 'good', 'nice', 'helpful']},
]


def detect_intent(message):
    """Match message to best intent using keyword scanning."""
    msg = message.lower().strip()

    # Check each intent
    for intent in INTENTS:
        for keyword in intent['keywords']:
            if keyword in msg:
                return intent['name']

    # Fuzzy fallback — single word checks
    words = msg.split()
    single_word_map = {
        'score': 'my_score', 'scores': 'show_rankings',
        'rank': 'show_rankings', 'ranks': 'show_rankings',
        'skill': 'my_skills', 'skills': 'candidate_skills',
        'reject': 'rejected', 'rejected': 'rejected',
        'shortlist': 'shortlisted', 'pending': 'pending_candidates',
        'report': 'download_report', 'bert': 'what_is_bert',
        'cgpa': 'cgpa_impact', 'experience': 'experience_impact',
        'improve': 'improve_resume', 'status': 'application_status',
        'top': 'top_candidate', 'best': 'top_candidate',
        'average': 'average_score', 'avg': 'average_score',
        'count': 'count_candidates', 'total': 'count_candidates',
        'missing': 'missing_skills', 'gap': 'missing_skills',
    }
    for word in words:
        if word in single_word_map:
            return single_word_map[word]

    return 'unknown'


def generate_response(intent, job=None, candidate=None, mode='hr'):
    """Generate contextual response based on intent."""

    try:

        # ════════════════════════════════════════════════════
        # HR RESPONSES
        # ════════════════════════════════════════════════════

        if intent == 'top_candidate':
            if not job:
                return "Please select a job from the sidebar first to see candidate rankings."
            top = job.candidates.filter(final_score__gt=0).order_by('-final_score').first()
            if not top:
                return "No candidates have been screened yet.\n\nClick '🧠 Run AI Screening' to analyze resumes."
            return (f"🥇 Top Candidate: {top.name}\n\n"
                    f"• Final Score: {top.score_pct}%\n"
                    f"• Required Skills: {top.tfidf_pct}%\n"
                    f"• BERT Match: {top.bert_pct}%\n"
                    f"• Status: {top.get_status_display()}\n"
                    f"• Skills: {', '.join(top.skills[:5]) if top.skills else 'Not detected'}")

        if intent == 'show_rankings':
            if not job:
                return "Please select a job from the sidebar to see rankings."
            cands = list(job.candidates.filter(final_score__gt=0).order_by('-final_score')[:5])
            if not cands:
                return "No screened candidates yet. Run AI Screening first."
            medals = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣']
            lines = [f"Top Candidates for {job.title}:\n"]
            for i, c in enumerate(cands):
                lines.append(f"{medals[i]} {c.name} — {c.score_pct}% ({c.get_status_display()})")
            return "\n".join(lines)

        if intent == 'average_score':
            if not job:
                return "Please select a job first."
            cands = list(job.candidates.filter(final_score__gt=0))
            if not cands:
                return "No screened candidates to calculate average."
            avg = sum(c.final_score for c in cands) / len(cands)
            highest = max(c.score_pct for c in cands)
            lowest  = min(c.score_pct for c in cands)
            return (f"📊 Score Summary for {job.title}:\n\n"
                    f"• Average Score: {avg*100:.1f}%\n"
                    f"• Highest Score: {highest}%\n"
                    f"• Lowest Score: {lowest}%\n"
                    f"• Total Screened: {len(cands)}")

        if intent == 'shortlisted':
            if not job:
                return "Please select a job first."
            sl = list(job.candidates.filter(status='shortlisted'))
            if not sl:
                return "No candidates have been shortlisted yet.\n\nShortlist candidates by changing their status in the dashboard."
            names = "\n".join(f"✅ {c.name} — {c.score_pct}%" for c in sl)
            return f"Shortlisted Candidates ({len(sl)}):\n\n{names}"

        if intent == 'rejected':
            if not job:
                return "Please select a job first."
            auto_rej = list(job.candidates.filter(auto_rejected=True))
            manual_rej = list(job.candidates.filter(status='rejected', auto_rejected=False))
            lines = []
            if auto_rej:
                lines.append(f"🤖 Auto Rejected ({len(auto_rej)}):")
                for c in auto_rej[:3]:
                    lines.append(f"  • {c.name} — {c.rejection_reason[:60]}")
            if manual_rej:
                lines.append(f"\n👤 Manually Rejected ({len(manual_rej)}):")
                for c in manual_rej[:3]:
                    lines.append(f"  • {c.name} — {c.score_pct}%")
            if not lines:
                return "No rejected candidates for this job."
            return "\n".join(lines)

        if intent == 'count_candidates':
            if not job:
                return "Please select a job first."
            total     = job.candidates.count()
            screened  = job.candidates.filter(final_score__gt=0).count()
            shortlist = job.candidates.filter(status='shortlisted').count()
            pending   = job.candidates.filter(status='pending').count()
            auto_rej  = job.candidates.filter(auto_rejected=True).count()
            return (f"📋 Candidate Summary for {job.title}:\n\n"
                    f"• Total Applied: {total}\n"
                    f"• Screened: {screened}\n"
                    f"• Shortlisted: {shortlist}\n"
                    f"• Pending Review: {pending}\n"
                    f"• Auto Rejected: {auto_rej}")

        if intent == 'how_scoring':
            return ("🧠 How RecruitAI Scoring Works:\n\n"
                    "We use a 6-factor scoring system:\n\n"
                    "1️⃣ Required Skills — 35%\n"
                    "   Must-have skills from job form\n\n"
                    "2️⃣ BERT Semantic Match — 25%\n"
                    "   AI understands meaning, not just keywords\n\n"
                    "3️⃣ Experience Match — 15%\n"
                    "   Years of experience vs job requirement\n\n"
                    "4️⃣ Education + CGPA — 15%\n"
                    "   Degree level and academic performance\n\n"
                    "5️⃣ Optional Skills Bonus — 10%\n"
                    "   Nice-to-have skills give extra points\n\n"
                    "6️⃣ Resume Completeness — +3% bonus\n"
                    "   Well-structured resume gets bonus points")

        if intent == 'download_report':
            if job:
                return (f"📄 To download the PDF report for {job.title}:\n\n"
                        "Click the '📄 PDF Report' button in the top bar.\n\n"
                        "The report includes:\n"
                        "• Summary statistics\n"
                        "• Full candidate rankings table\n"
                        "• Top 3 candidate detailed breakdown\n"
                        "• Skills and rejection reasons")
            return "Click the '📄 PDF Report' button in the top bar to download the recruitment report."

        if intent == 'required_skills':
            if not job:
                return "Please select a job first."
            req = job.required_skills_list
            opt = job.optional_skills_list
            if not req:
                return ("No required skills defined for this job.\n\n"
                        "Edit the job posting to add Required and Optional skills "
                        "for more accurate AI scoring.")
            return (f"Skills for {job.title}:\n\n"
                    f"🔴 Required (Must Have):\n{', '.join(req)}\n\n"
                    f"🟡 Optional (Good to Have):\n{', '.join(opt) if opt else 'None defined'}")

        if intent == 'pending_candidates':
            if not job:
                return "Please select a job first."
            pending = list(job.candidates.filter(status='pending'))
            if not pending:
                return "No pending candidates! All have been reviewed."
            names = "\n".join(f"⏳ {c.name} — {c.score_pct}%" for c in pending[:5])
            return f"Pending Review ({len(pending)}):\n\n{names}"

        if intent == 'candidate_skills':
            if not job:
                return "Please select a job first."
            cands = list(job.candidates.filter(final_score__gt=0)[:5])
            if not cands:
                return "No screened candidates yet."
            lines = [f"Skills Summary for top candidates:\n"]
            for c in cands:
                skills_str = ', '.join(c.skills[:4]) if c.skills else 'None detected'
                lines.append(f"• {c.name}: {skills_str}")
            return "\n".join(lines)

        # ════════════════════════════════════════════════════
        # CANDIDATE RESPONSES
        # ════════════════════════════════════════════════════

        if intent == 'my_score':
            if not candidate or candidate.final_score == 0:
                return ("Your score is not available yet.\n\n"
                        "HR needs to run AI Screening first. "
                        "Check back after your application has been reviewed.")
            status_msg = {
                'shortlisted':   '🎉 Congratulations! You have been shortlisted!',
                'review':        '👀 Your application is under review by HR.',
                'pending':       '⏳ Your application is pending review.',
                'rejected':      '❌ Unfortunately you were not selected this time.',
                'auto_rejected': f'❌ Auto Rejected: {candidate.rejection_reason}',
            }.get(candidate.status, '')
            return (f"📊 Your Score for {candidate.job.title}:\n\n"
                    f"• Final Score: {candidate.score_pct}%\n"
                    f"• Required Skills: {candidate.tfidf_pct}%\n"
                    f"• BERT Match: {candidate.bert_pct}%\n"
                    f"• Experience: {candidate.experience_pct}%\n"
                    f"• Education: {candidate.education_pct}%\n\n"
                    f"{status_msg}")

        if intent == 'my_skills':
            if not candidate:
                return "Please log in to see your detected skills."
            skills = candidate.skills
            if not skills:
                return "No skills detected yet. Wait for HR to run AI Screening."
            return (f"✅ Skills Detected on Your Resume ({len(skills)}):\n\n"
                    f"{', '.join(skills)}\n\n"
                    "These were automatically extracted from your resume text.")

        if intent == 'missing_skills':
            if not candidate:
                return "Please log in to see your skill gaps."
            if candidate.final_score == 0:
                return "Screening hasn't run yet. Check back after HR screens your resume."
            missing = candidate.missing_required_skills
            if not missing:
                return "🎉 Great news! You have all the required skills for this position!"
            return (f"⚠️ Missing Required Skills ({len(missing)}):\n\n"
                    f"{', '.join(missing)}\n\n"
                    "Adding these skills to your resume could significantly improve your score.")

        if intent == 'improve_resume':
            tips = ("💡 Tips to Improve Your Resume Score:\n\n"
                    "1️⃣ Add Missing Required Skills\n"
                    "   Check skill gap analysis and add those skills\n\n"
                    "2️⃣ Use Job Keywords\n"
                    "   Mirror the exact words from the job description\n\n"
                    "3️⃣ Quantify Your Experience\n"
                    "   '3 years Python experience' scores better than just 'Python'\n\n"
                    "4️⃣ Add CGPA/Percentage\n"
                    "   Clearly mention CGPA x.x/10 or percentage%\n\n"
                    "5️⃣ Complete All Resume Sections\n"
                    "   Summary, Education, Experience, Skills, Certifications\n\n"
                    "6️⃣ Get Relevant Certifications\n"
                    "   Certifications in required technologies boost score")
            if candidate and candidate.final_score > 0:
                missing = candidate.missing_required_skills
                if missing:
                    tips += f"\n\n🎯 Your Priority: Add these skills:\n{', '.join(missing)}"
            return tips

        if intent == 'application_status':
            if not candidate:
                return "Please log in to check your application status."
            if candidate.final_score == 0:
                return ("⏳ Status: Pending AI Screening\n\n"
                        "HR has not run AI screening yet. "
                        "Your application has been received successfully.")
            status_responses = {
                'shortlisted':   ("🎉 Status: SHORTLISTED\n\n"
                                  "Congratulations! You have been shortlisted for this position. "
                                  "HR will contact you soon for the next steps."),
                'review':        ("👀 Status: UNDER REVIEW\n\n"
                                  f"Your score is {candidate.score_pct}%. "
                                  "HR is currently reviewing your application."),
                'pending':       (f"⏳ Status: PENDING\n\n"
                                  f"Your score is {candidate.score_pct}%. "
                                  "Your application is in the queue for review."),
                'rejected':      ("❌ Status: NOT SELECTED\n\n"
                                  "Unfortunately your application was not selected this time. "
                                  "Keep improving your skills and apply again!"),
                'auto_rejected': (f"❌ Status: AUTO REJECTED\n\n"
                                  f"Reason: {candidate.rejection_reason}\n\n"
                                  "You can improve your profile and apply for other positions."),
            }
            return status_responses.get(candidate.status, "Status unknown. Please contact HR.")

        if intent == 'what_is_bert':
            return ("🤖 What is BERT AI Matching?\n\n"
                    "BERT stands for Bidirectional Encoder Representations from Transformers.\n\n"
                    "Unlike simple keyword matching, BERT understands the MEANING of text.\n\n"
                    "Example:\n"
                    "• Job needs: 'developer'\n"
                    "• Resume says: 'programmer'\n"
                    "• BERT knows these mean the same thing ✅\n\n"
                    "We use the 'all-MiniLM-L6-v2' model which converts your resume "
                    "into a 384-dimensional vector and compares it with the job description. "
                    "The similarity between these vectors is your BERT score.")

        if intent == 'what_is_required_skills':
            return ("🔴 What are Required Skills?\n\n"
                    "Required Skills are MUST HAVE skills that HR sets when creating a job.\n\n"
                    "• If you have ALL required skills → high score\n"
                    "• If you're MISSING required skills → lower score\n"
                    "• If you have ZERO required skills → possible auto rejection\n\n"
                    "Required Skills carry 35% weight in your final score — "
                    "it is the most important factor!")

        if intent == 'cgpa_impact':
            return ("🎓 How CGPA/Percentage Affects Your Score:\n\n"
                    "Education + CGPA carries 15% weight in total score.\n\n"
                    "CGPA scoring:\n"
                    "• 9.0+ / 90%+ → 100% education score\n"
                    "• 7.5+ / 75%+ → 85% education score\n"
                    "• 6.0+ / 60%+ → 70% education score\n"
                    "• Below 6.0   → 50% education score\n\n"
                    "⚠️ If HR sets a minimum CGPA cutoff and you are below it → Auto Rejected\n\n"
                    "Make sure your CGPA is clearly written as:\n"
                    "'CGPA 8.2/10' or '82%' in your resume.")

        if intent == 'experience_impact':
            return ("💼 How Experience Affects Your Score:\n\n"
                    "Experience carries 15% weight in total score.\n\n"
                    "How it works:\n"
                    "• Fresher applying for fresher job → 100% ✅\n"
                    "• 2 years applying for 2+ years job → 100% ✅\n"
                    "• Fresher applying for 3+ years job → 30% ❌\n"
                    "• 5 years applying for junior job → 85% ⚠️ (overqualified)\n\n"
                    "Tips:\n"
                    "• Clearly write '2 years experience' in your resume\n"
                    "• Mention internships as '6 months internship'\n"
                    "• For fresher jobs, write 'fresher' explicitly")

        # ════════════════════════════════════════════════════
        # GENERAL RESPONSES
        # ════════════════════════════════════════════════════

        if intent == 'greeting':
            if mode == 'hr':
                return ("👋 Hello! I am your RecruitAI Assistant.\n\n"
                        "I can help you with:\n"
                        "• Top candidates and rankings\n"
                        "• Score analysis and summaries\n"
                        "• Shortlisted / rejected candidates\n"
                        "• How the AI scoring works\n"
                        "• Downloading reports\n\n"
                        "What would you like to know?")
            return ("👋 Hello! I am your Career Assistant.\n\n"
                    "I can help you with:\n"
                    "• Your match score and breakdown\n"
                    "• Missing skills and skill gaps\n"
                    "• Tips to improve your resume\n"
                    "• Your application status\n"
                    "• How the AI evaluates resumes\n\n"
                    "What would you like to know?")

        if intent == 'help':
            if mode == 'hr':
                return ("📋 HR Assistant Commands:\n\n"
                        "• 'Top candidate' — best match\n"
                        "• 'Show rankings' — top 5 list\n"
                        "• 'Average score' — stats summary\n"
                        "• 'Shortlisted' — selected candidates\n"
                        "• 'Rejected' — auto/manual rejections\n"
                        "• 'How many candidates' — count\n"
                        "• 'Required skills' — job skill list\n"
                        "• 'Pending candidates' — queue\n"
                        "• 'How scoring works' — AI explanation\n"
                        "• 'Download report' — PDF guide")
            return ("📋 Candidate Assistant Commands:\n\n"
                    "• 'My score' — your match score\n"
                    "• 'My skills' — detected skills\n"
                    "• 'Missing skills' — skill gaps\n"
                    "• 'How to improve' — resume tips\n"
                    "• 'My status' — application status\n"
                    "• 'What is BERT' — AI explanation\n"
                    "• 'CGPA impact' — academic scoring\n"
                    "• 'Experience impact' — exp scoring")

        if intent == 'thanks':
            return "You're welcome! 😊 Let me know if you need anything else."

        # Unknown intent
        if mode == 'hr':
            return ("I didn't quite understand that.\n\n"
                    "Try asking:\n"
                    "• 'Who is the top candidate?'\n"
                    "• 'Show me rankings'\n"
                    "• 'How many candidates applied?'\n"
                    "• 'How does scoring work?'\n\n"
                    "Or type 'help' for all commands.")
        return ("I didn't quite understand that.\n\n"
                "Try asking:\n"
                "• 'What is my score?'\n"
                "• 'What skills am I missing?'\n"
                "• 'How can I improve?'\n"
                "• 'What is my status?'\n\n"
                "Or type 'help' for all commands.")

    except Exception as e:
        print(f"[chatbot] Error: {e}")
        return "Sorry, I encountered an error. Please try again."


def process_chat(message, job=None, candidate=None, user=None, mode='hr'):
    """Main entry point — detect intent and return response."""
    intent  = detect_intent(message)
    reply   = generate_response(intent, job=job, candidate=candidate, mode=mode)
    print(f"[chatbot] mode={mode} intent={intent} message='{message[:50]}'")
    return {
        'intent':  intent,
        'message': reply,
    }
