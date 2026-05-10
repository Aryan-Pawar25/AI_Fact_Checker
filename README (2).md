# 🛡️ Fact-Check Agent

A deployed web app that automatically verifies factual claims in PDF documents using AI + live web search.

## Live Demo
> Deploy using steps below and paste your Streamlit Cloud URL here.

## What It Does
1. **Extract** — Reads your PDF and identifies specific verifiable claims (stats, dates, figures)
2. **Verify** — Cross-references each claim against live web data using Claude's web search
3. **Report** — Flags each claim as ✅ Verified, ⚠️ Inaccurate, or ❌ False with explanations and sources

## Tech Stack
- **Frontend**: Streamlit
- **AI**: Claude claude-sonnet-4-20250514 (Anthropic)
- **Web Search**: Built-in web_search tool via Anthropic API
- **PDF Parsing**: PyPDF2

## Deployment (Streamlit Cloud — Free)

### 1. Clone / Fork the repo
```bash
git clone https://github.com/YOUR_USERNAME/fact-check-agent
cd fact-check-agent
```

### 2. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/fact-check-agent.git
git push -u origin main
```

### 3. Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **New app**
3. Select your repository and `app.py`
4. Click **Deploy**

The app will be live at: `https://YOUR_USERNAME-fact-check-agent-app-XXXX.streamlit.app`

## Local Development
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Usage
1. Enter your [Anthropic API key](https://console.anthropic.com)
2. Upload any PDF (marketing docs, reports, articles)
3. Click **Analyze PDF**
4. Review the verdict report with source links

## Evaluation — "Trap Document" Test
The app is designed to catch:
- Outdated statistics (e.g., "Population of India is 1.2 billion" — actually 1.44B)
- Fabricated figures (e.g., wrong revenue numbers)
- Misattributed dates or rankings

## Files
```
fact-check-agent/
├── app.py              # Main Streamlit app
├── requirements.txt    # Python dependencies
└── README.md           # This file
```
