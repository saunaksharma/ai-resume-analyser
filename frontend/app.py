import streamlit as st
import requests
import pandas as pd
# Page config
st.set_page_config(page_title="AI Resume Booster", layout="wide")

# Header
st.title("🧠 AI Resume Booster")
st.caption("Analyze your resume, check ATS score, and match with job descriptions")

st.divider()

# Upload + JD input
col1, col2 = st.columns(2)

with col1:
    file = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])

with col2:
    jd = st.text_area("🧾 Paste Job Description (optional)", height=150)

st.divider()

# Analyze button
if file and st.button("🚀 Analyze Resume"):
    st.info("Analyzing your resume... ⏳")

    try:
        response = requests.post(
            "http://127.0.0.1:8000/analyze/",
            files={"file": file},
            data={"jd": jd}
        )

        data = response.json()

        st.success("Analysis Complete ✅")

        st.divider()

        # =============================
        # 📊 TOP METRICS
        # =============================
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                label="📊 ATS Score",
                value=f"{data.get('ats_score', 0)} / 100"
            )

        with col2:
            if jd and data.get("match_score") is not None:
                st.metric(
                    label="🎯 Job Match",
                    value=f"{data.get('match_score')} %"
                )
            else:
                st.metric(
                    label="🎯 Job Match",
                    value="N/A"
                )

        st.divider()

        # =============================
        # 📌 SCORE BREAKDOWN
        # =============================
        st.markdown("## 📌 Score Breakdown")

        for d in data.get("details", []):
            st.write(f"✔️ {d}")

        st.divider()

        # =============================
        # ❌ MISSING SKILLS
        # =============================
        if jd and data.get("missing_skills"):
            st.markdown("## ❌ Missing Skills")

            cols = st.columns(3)

            for i, skill in enumerate(data["missing_skills"]):
                cols[i % 3].warning(skill)

            st.divider()

        # =============================
        # 📄 ANALYSIS
        # =============================
        st.markdown("## 📄 AI Resume Analysis")

        if data.get("analysis"):
            st.text(data["analysis"])
        else:
            st.error("No analysis received")

    except Exception as e:
        st.error(f"Error: {e}")
