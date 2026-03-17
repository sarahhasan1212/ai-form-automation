# 🤖 AI-Powered Web Form Automation

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Automation-45ba4b?style=for-the-badge&logo=playwright&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-AI%20Inference-F55036?style=for-the-badge)
![Llama](https://img.shields.io/badge/Llama-3.2%20Vision-blueviolet?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

> An end-to-end automated testing framework that fills multi-step web forms using **Playwright**, then uses **Llama 3.2 Vision AI** to visually verify the result — and generates an **AI-written executive test report**.

---

## 📸 How It Works

```
form_data.csv          Playwright Browser        Groq AI (Llama Vision)
──────────────    →    ──────────────────    →    ──────────────────────
URL + Sitecore ID      1. Fill email field        Analyses screenshot
                       2. Wait for form expand    Returns PASS / FAIL
                       3. Fill all fields         + reason
                       4. Submit form
                       5. Take screenshot    →    ai_test_report.csv
                                                  + Executive Summary
```

---

## ✨ Key Features

- **Progressive Form Handling** — detects and fills forms that expand after the initial email field
- **AI Visual Validation** — sends a screenshot to Llama 3.2 Vision to confirm the post-submission page loaded correctly (video player, no UI errors)
- **AI Executive Summary** — Llama 3.3 70B reads the CSV results and writes a professional QA summary
- **Async Execution** — built with Python `asyncio` for non-blocking performance
- **CSV-driven** — test data lives in a simple spreadsheet, no code changes needed to add more URLs
- **Detailed Reporting** — outputs a CSV report with status and AI reasoning per test case

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| **Playwright (Python)** | Browser automation — form filling & screenshots |
| **Groq API** | Fast AI inference platform |
| **Llama 3.2 Vision (11B)** | Visual validation of post-submit pages |
| **Llama 3.3 (70B)** | Generating the executive test report summary |
| **Python asyncio** | Async execution for speed |
| **python-dotenv** | Secure API key management |

---

## 📁 Project Structure

```
📦 ai-form-automation/
├── 📄 automation.py        # Main script — Playwright + Groq integration
├── 📄 form_data.csv        # Test input: URLs + Sitecore IDs
├── 📄 requirements.txt     # Python dependencies
├── 📄 .env                 # API key (NOT committed to GitHub)
├── 📄 .gitignore           # Ignores .env, screenshots, reports
└── 📄 README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/ai-form-automation.git
cd ai-form-automation
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Set up your API key
Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key_here
```
Get a free API key at [console.groq.com](https://console.groq.com)

### 4. Add your test URLs
Edit `form_data.csv`:
```csv
url,sitecore_id,status
https://yoursite.com/form-page,{ITEM-001},new
https://yoursite.com/another-form,{ITEM-002},existing
```

### 5. Run
```bash
python automation.py
```

---

## 📊 Output

After the run, you get:

**`ai_test_report.csv`** — one row per form:
```
url, sitecore_id, test_status, reason
https://..., {ABC-001}, PASS, "Vision Confirmed: Video player visible and page fully loaded."
https://..., {ABC-002}, FAIL, "Vision Rejected: Page shows a 404 error overlay."
```

**Terminal Executive Summary** (written by Llama 3.3 70B):
```
🤖 GROQ AI EXECUTIVE SUMMARY:
The automated test suite processed 12 forms with a 91.6% pass rate...
```

---

## 🔐 Security

- API keys are stored in `.env` and never hardcoded
- `.env` is listed in `.gitignore` and never committed to version control

---

## 💡 Use Cases

- QA regression testing for marketing/landing page forms
- Validating webinar registration forms post-deployment
- Automated smoke testing across multiple form URLs from a CSV

---

## 👤 Author

Built by **[Your Name]**  
📧 your@email.com  
🔗 [LinkedIn](https://linkedin.com/in/yourprofile) | [GitHub](https://github.com/yourusername)
