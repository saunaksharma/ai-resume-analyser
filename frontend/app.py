import streamlit as st
import requests

st.set_page_config(page_title="AI Resume Analyser", layout="wide", page_icon="📄")

st.title("AI Resume Analyser")
st.caption("Upload your resume for an instant ATS score, JD match, and actionable AI feedback.")

st.divider()

col1, col2 = st.columns([1, 1])

with col1:
    file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])

with col2:
    jd = st.text_area("Paste Job Description (optional)", height=160,
                       placeholder="Paste the job description here to get a match score and targeted feedback...")

st.divider()

if file:
    if st.button("Analyse Resume", type="primary", use_container_width=True):
        with st.spinner("Analysing your resume..."):
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/analyze/",
                    files={"file": (file.name, file.getvalue(), file.type)},
                    data={"jd": jd},
                    timeout=120,
                )
                response.raise_for_status()
                data = response.json()
            except requests.exceptions.ConnectionError:
                st.error("Cannot reach the backend. Make sure the FastAPI server is running on port 8000.")
                st.stop()
            except requests.exceptions.HTTPError as e:
                detail = e.response.json().get("detail", str(e)) if e.response else str(e)
                st.error(f"Error from backend: {detail}")
                st.stop()
            except Exception as e:
                st.error(f"Unexpected error: {e}")
                st.stop()

        st.success("Analysis complete!")
        st.divider()

        # ── Top metrics ──────────────────────────────────────────────────────
        ats_score = data.get("ats_score", 0)
        match_score = data.get("match_score")

        def score_delta(score):
            if score >= 80:
                return f"+{score - 70} above good"
            elif score >= 50:
                return f"{score - 70} below good"
            else:
                return f"{score - 70} needs improvement"

        if match_score is not None:
            m1, m2 = st.columns(2)
            with m1:
                st.metric("ATS Score", f"{ats_score} / 100", delta=score_delta(ats_score))
                st.progress(ats_score / 100)
            with m2:
                st.metric("Job Match", f"{match_score}%", delta=score_delta(match_score))
                st.progress(match_score / 100)
        else:
            st.metric("ATS Score", f"{ats_score} / 100", delta=score_delta(ats_score))
            st.progress(ats_score / 100)

        st.divider()

        # ── ATS Score breakdown ──────────────────────────────────────────────
        with st.expander("ATS Score Breakdown", expanded=True):
            section_scores = data.get("section_scores", {})
            if section_scores:
                cols = st.columns(len(section_scores))
                for col, (cat, pts) in zip(cols, section_scores.items()):
                    maxes = {"Keywords": 30, "Structure": 20,
                             "Achievements": 20, "Action Verbs": 15, "Bonus Sections": 15}
                    max_pts = maxes.get(cat, 20)
                    col.metric(cat, f"{pts} / {max_pts}")
                    col.progress(pts / max_pts if max_pts else 0)

            st.markdown("**Detail**")
            for detail in data.get("details", []):
                st.write(f"• {detail}")

        # ── Missing skills ───────────────────────────────────────────────────
        missing = data.get("missing_skills", [])
        if missing:
            with st.expander(f"Missing Skills from Job Description ({len(missing)})", expanded=True):
                cols = st.columns(3)
                for i, skill in enumerate(missing):
                    cols[i % 3].warning(skill)

        # ── AI Analysis ──────────────────────────────────────────────────────
        analysis = data.get("analysis", {})
        if isinstance(analysis, dict) and analysis:
            st.divider()
            st.subheader("AI Analysis")

            if analysis.get("summary"):
                st.info(analysis["summary"])

            left, right = st.columns(2)

            with left:
                if analysis.get("strengths"):
                    st.markdown("**Strengths**")
                    for s in analysis["strengths"]:
                        st.markdown(f"- {s}")

                if analysis.get("suggestions"):
                    st.markdown("**Suggestions**")
                    for s in analysis["suggestions"]:
                        st.markdown(f"- {s}")

            with right:
                if analysis.get("weaknesses"):
                    st.markdown("**Weaknesses**")
                    for w in analysis["weaknesses"]:
                        st.markdown(f"- {w}")

                if analysis.get("missing_skills"):
                    st.markdown("**Skills to Add**")
                    for sk in analysis["missing_skills"]:
                        st.markdown(f"- {sk}")

            section_fb = analysis.get("section_feedback", {})
            if section_fb:
                with st.expander("Section-by-Section Feedback"):
                    for section, feedback in section_fb.items():
                        if feedback:
                            st.markdown(f"**{section.title()}:** {feedback}")

        elif isinstance(analysis, str) and analysis:
            st.subheader("AI Analysis")
            st.text(analysis)

else:
    st.info("Upload a resume (PDF or DOCX) to get started.")
