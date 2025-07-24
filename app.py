# wisc_app.py
# A Streamlit prototype for the WISC (Why I Should Care) app
# This app takes a user's profile and a news article, and explains why the article might be relevant to them

import streamlit as st
import openai
import pdfplumber

# Set OpenAI key securely
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="WISC – Why I Should Care", layout="centered")

# App title
st.title("🧠 WISC – Why I Should Care")
st.markdown("This tool helps you understand how a news article may be personally relevant to your life.")

# User profile input
st.header("👤 Your Profile")
user_age = st.number_input("Age", min_value=10, max_value=100, step=1)
user_gender = st.selectbox("Gender", ["Prefer not to say", "Male", "Female", "Non-binary", "Other"])
user_location = st.text_input("Where do you live?")
user_family = st.text_input("Describe your family role (e.g., parent of 2, single, caregiver)")
user_job = st.text_input("What do you do for work or study?")

# Article input
st.header("📰 Paste or Upload a News Article")
news_article = st.text_area("Paste the article or summary here:", height=200)

# File upload option
uploaded_file = st.file_uploader("Or upload a text or PDF file:", type=["txt", "pdf"])
if uploaded_file:
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            news_article = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    else:
        news_article = uploaded_file.read().decode("utf-8")

# Tone/style selector
tone = st.selectbox("Preferred explanation style:", ["Neutral", "Friendly", "Casual / Gen Z", "Professional", "Sarcastic"])

# Analyze button
if st.button("Why Should I Care?") and news_article:
    # Construct prompt
    prompt = f"""
A user has this profile:
- Age: {user_age}
- Gender: {user_gender}
- Location: {user_location}
- Family: {user_family}
- Work/Study: {user_job}

Based on the following news article, explain why this article might matter to them personally.
Use the selected tone/style: {tone}
Focus on their age, job, location, family, or anything that connects the news to their real life.
Write it in clear, plain English, in 3-5 bullet points.

News article:
{news_article}
"""

    # Call OpenAI
    with st.spinner("Analyzing relevance..."):
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that explains how news is personally relevant to users based on their profile."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
        )
        explanation = response.choices[0].message.content

    st.markdown("## 📌 Why This Matters to You")
    st.markdown(explanation)

    # Option to export
    st.download_button("💾 Download Explanation as .txt", explanation, file_name="wisc_summary.txt")

elif not news_article:
    st.info("Please paste or upload a news article to begin.")
