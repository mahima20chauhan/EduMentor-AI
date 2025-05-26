import streamlit as st
import os
import time
import requests
from fpdf import FPDF
from dotenv import load_dotenv

# ----------------- Load API Key -----------------
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}
api_url = "https://openrouter.ai/api/v1/chat/completions"
model = "openchat/openchat-3.5-1210"  # Supported free model

# ----------------- Helper Function -----------------
def generate_response(prompt):
    try:
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"❌ Error fetching response: {e}"

def clean_text(text):
    # Remove emojis or non-latin characters
    return text.encode("latin-1", "ignore").decode("latin-1")

# ----------------- Streamlit App -----------------
st.set_page_config(page_title="EduMentor AI", page_icon="📘")
st.title("📘 EduMentor AI - Your Study Companion")

topic = st.text_input("Enter a topic (e.g. Linear Regression, OS Scheduling):")

if st.button("Generate Content") and topic:
    with st.spinner("Generating..."):

        # 1. Explanation
        explain_prompt = f"Explain the topic '{topic}' in simple words, under 200 words."
        explanation = generate_response(explain_prompt)

        # 2. MCQs
        mcq_prompt = f"Create 3 MCQs with 4 options and answers for topic: {topic}"
        mcqs = generate_response(mcq_prompt)

        # 3. Flashcards
        flash_prompt = f"Create 3 flashcards for topic '{topic}' like: Q: ... A: ..."
        flashcards = generate_response(flash_prompt)

        # 4. Notes
        notes_prompt = f"Give quick revision notes for '{topic}' as bullet points."
        notes = generate_response(notes_prompt)

        # ------------------ Display Output ------------------
        st.subheader("📖 Explanation")
        st.write(explanation)

        st.subheader("❓ MCQs")
        st.write(mcqs)

        st.subheader("🧠 Flashcards")
        for pair in flashcards.strip().split("Q:")[1:]:
            qa = pair.strip().split("A:")
            if len(qa) == 2:
                st.markdown(f"**Q:** {qa[0].strip()}")
                st.markdown(f"**A:** {qa[1].strip()}")
                st.markdown("---")

        st.subheader("📝 Revision Notes")
        st.write(notes)

        # ------------------ PDF Download ------------------
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        content = f"Topic: {topic}\n\nExplanation:\n{explanation}\n\nMCQs:\n{mcqs}\n\nFlashcards:\n{flashcards}\n\nNotes:\n{notes}"
        pdf.multi_cell(0, 10, clean_text(content))
        pdf_path = f"{topic.replace(' ', '_')}_{int(time.time())}.pdf"
        pdf.output(pdf_path)

        with open(pdf_path, "rb") as f:
            st.download_button("📄 Download PDF", f, file_name=pdf_path)
