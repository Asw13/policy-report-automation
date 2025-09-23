
# Policy Report Automation 📑⚡

[![Netlify Status](https://api.netlify.com/api/v1/badges/your-badge-id/deploy-status)](https://automation-html-reports-asw13.netlify.app/)

🔗 **Live Demo**: [https://automation-html-reports-asw13.netlify.app/](https://automation-html-reports-asw13.netlify.app/)

---

## 📌 Project Overview
This project automates the generation of **structured policy reports** using **Google Gemini AI** and Python.  
The system produces:
- 📑 Multi-part **HTML reports**  
- 🖼️ **Image prompts** with automatic image downloads  
- 🎨 **CSS styling** for readability  
- 📂 Auto-organization of results in `output_parts/`  
- 🚀 Automatic deployment to **Netlify** via GitHub  

---

## ✨ Features
- AI-powered stepwise content generation (`Part1.html`, `Part2.html`, …)  
- Auto-merge into a single `index.html`  
- Image search & download (policy, company, product)  
- Professional CSS for tables, sections, and images  
- Daily run automation via Windows Task Scheduler  
- GitHub → Netlify CI/CD for hosting  

---

## 📂 Project Structure
```

automation\_html/
├── mani\_banifect.txt     # Main report prompt
├── prmopt2.txt           # Image prompt instructions
├── output\_parts/         # Generated reports & assets
│   ├── index.html        # Final report (merged)
│   ├── style.css         # Report styling
│   ├── image\_prompt.txt  # AI-generated image queries
│   ├── policy\_announcement.png
│   ├── company\_announcement.png
│   └── product\_announcement.png
├── html\_prompt.py        # Main automation script

````

---

## 🚀 Usage
1. Clone the repo:
   ```bash
   git clone https://github.com/Asw13/policy-report-automation.git
   cd policy-report-automation
````

2. Install dependencies:

   ```bash
   pip install google-genai ddgs requests
   ```
3. Run the script:

   ```bash
   python html_prompt.py
   ```
4. View results in `output_parts/index.html`.

---

## 🌐 Deployment

* Hosted on **Netlify**: [https://automation-html-reports-asw13.netlify.app/](https://automation-html-reports-asw13.netlify.app/)
* Every `git push` triggers automatic deployment.

---

