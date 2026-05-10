import streamlit as st
import anthropic
import PyPDF2
import json
import re
import io

st.set_page_config(
    page_title="Fact-Check Agent",
    page_icon="🛡️",
    layout="centered"
)

st.markdown("""
<style>
    .verdict-verified { background:#EAF3DE; color:#3B6D11; padding:4px 12px; border-radius:99px; font-size:13px; font-weight:500; }
    .verdict-inaccurate { background:#FAEEDA; color:#854F0B; padding:4px 12px; border-radius:99px; font-size:13px; font-weight:500; }
    .verdict-false { background:#FCEBEB; color:#A32D2D; padding:4px 12px; border-radius:99px; font-size:13px; font-weight:500; }
    .claim-box { border:1px solid #e0e0e0; border-radius:10px; padding:14px 18px; margin-bottom:12px; }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ Fact-Check Agent")
st.markdown("Upload a PDF to extract claims and verify them against live web data.")

api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

def extract_text_from_pdf(file_bytes):
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_claims(client, text):
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"""Extract ALL specific verifiable factual claims from this text. Focus on: statistics, percentages, dates, monetary figures, named facts, rankings, and technical specifications.

Return ONLY a JSON array of strings, no preamble, no markdown backticks.
Example: ["Global smartphone users reached 6.8 billion in 2023","Apple revenue was $394 billion in FY2022"]
Extract up to 10 most verifiable claims.

Text:
{text[:8000]}"""
        }]
    )
    raw = response.content[0].text.strip()
    clean = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)

def verify_claims(client, claims):
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": f"""You are a fact-checking agent. For each claim below, search the web and verify it.
Return ONLY a JSON array (no preamble, no markdown). Each object must have:
- claim (string)
- verdict ("Verified" | "Inaccurate" | "False")
- explanation (1-2 sentences)
- realFact (the correct fact if wrong, or empty string if verified)
- source (URL if found, else "")

Claims to verify:
{json.dumps(claims)}"""
        }]
    )
    text_content = " ".join(b.text for b in response.content if hasattr(b, "text"))
    match = re.search(r'\[[\s\S]*\]', text_content)
    return json.loads(match.group(0)) if match else []

if uploaded_file and api_key:
    if st.button("🔍 Analyze PDF", use_container_width=True):
        try:
            client = anthropic.Anthropic(api_key=api_key)
            file_bytes = uploaded_file.read()

            with st.spinner("Extracting text from PDF..."):
                text = extract_text_from_pdf(file_bytes)
                if not text.strip():
                    st.error("Could not extract text from PDF. Make sure it's not a scanned image-only PDF.")
                    st.stop()

            with st.spinner("Identifying factual claims..."):
                claims = extract_claims(client, text)
                if not claims:
                    st.warning("No verifiable claims found in this document.")
                    st.stop()

            st.info(f"Found **{len(claims)}** verifiable claims. Now cross-referencing with live web data...")

            with st.spinner(f"Verifying {len(claims)} claims against live web data..."):
                results = verify_claims(client, claims)

            if not results:
                st.error("Verification failed. Please try again.")
                st.stop()

            counts = {"Verified": 0, "Inaccurate": 0, "False": 0}
            for r in results:
                v = r.get("verdict", "")
                if v in counts:
                    counts[v] += 1

            st.markdown("### 📊 Verification Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("✅ Verified", counts["Verified"])
            col2.metric("⚠️ Inaccurate", counts["Inaccurate"])
            col3.metric("❌ False", counts["False"])

            st.markdown("---")
            st.markdown("### 📋 Claim-by-Claim Report")

            for r in results:
                verdict = r.get("verdict", "Unknown")
                claim = r.get("claim", "")
                explanation = r.get("explanation", "")
                real_fact = r.get("realFact", "")
                source = r.get("source", "")

                border_color = {"Verified": "#639922", "Inaccurate": "#BA7517", "False": "#E24B4A"}.get(verdict, "#888")
                icon = {"Verified": "✅", "Inaccurate": "⚠️", "False": "❌"}.get(verdict, "❓")

                with st.container():
                    st.markdown(f"""
<div style="border:1px solid {border_color}; border-left:4px solid {border_color}; border-radius:10px; padding:14px 18px; margin-bottom:12px; background:white;">
  <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:12px; margin-bottom:10px;">
    <div style="font-size:14px; color:#222; line-height:1.5; flex:1;"><em>"{claim}"</em></div>
    <div style="font-weight:600; color:{border_color}; white-space:nowrap;">{icon} {verdict}</div>
  </div>
  <div style="font-size:13px; color:#555; border-top:1px solid #eee; padding-top:10px;">
    <strong>Analysis:</strong> {explanation}
    {f'<div style="margin-top:8px; background:#f5f5f5; border-radius:6px; padding:8px 12px; font-size:13px;"><strong>Correct fact:</strong> {real_fact}</div>' if real_fact and verdict != "Verified" else ""}
    {f'<div style="margin-top:6px; font-size:12px;"><a href="{source}" target="_blank">🔗 Source</a></div>' if source else ""}
  </div>
</div>""", unsafe_allow_html=True)

            report_data = json.dumps(results, indent=2)
            st.download_button("⬇️ Download JSON Report", report_data, file_name="fact_check_report.json", mime="application/json")

        except json.JSONDecodeError as e:
            st.error(f"Failed to parse AI response: {e}")
        except Exception as e:
            st.error(f"Error: {e}")
else:
    if not api_key:
        st.info("https://api.anthropic.com keys are required to use this app. Please enter your API key above.")
    if not uploaded_file:
        st.info("Upload a PDF file to begin fact-checking.")
