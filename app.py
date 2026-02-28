import streamlit as st
import model


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="ResumeAlign Pro | AI Career Suite",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# -----------------------------
# PROFESSIONAL STYLING
# -----------------------------
st.markdown("""
<style>
.main {
    background-color: #f4f6f9;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

h1 {
    font-size: 40px;
    font-weight: 700;
    color: #1a1a1a;
}

.stButton>button {
    width: 100%;
    border-radius: 6px;
    height: 3em;
    background-color: #0f172a;
    color: white;
    font-weight: 600;
    border: none;
}

.stButton>button:hover {
    background-color: #1e293b;
}

.stDownloadButton>button {
    background-color: #1d4ed8;
    color: white;
    font-weight: 600;
    border-radius: 6px;
    height: 3em;
}

footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "optimized_resume" not in st.session_state:
    st.session_state.optimized_resume = None


def main():

    # -----------------------------
    # HEADER
    # -----------------------------
    st.title("ResumeAlign Pro")
    st.markdown("##### Enterprise-grade AI resume optimization for analytical and technical professionals.")
    st.divider()

    col_input, col_preview = st.columns([1, 1], gap="large")

    # =============================
    # INPUT SECTION
    # =============================
    with col_input:

        st.subheader("1. Position & Context")

        job_options = [
            "Data Scientist (Entry Level)",
            "Data Scientist (Senior)",
            "Data Analyst",
            "Financial Analyst",
            "Pricing Analyst",
            "Business Intelligence Analyst",
            "Custom Role..."
        ]

        selected_role = st.selectbox("Select Target Job Title", job_options)

        if selected_role == "Custom Role...":
            target_title = st.text_input(
                "Enter Custom Job Title",
                placeholder="e.g. Senior Quantitative Researcher"
            )
        else:
            target_title = selected_role

        st.subheader("2. Job Requirements")

        job_description = st.text_area(
            "Paste Complete Job Description",
            height=250,
            placeholder="Paste the full job description here..."
        )

        st.subheader("3. Source Resume")

        uploaded_file = st.file_uploader(
            "Upload Resume (PDF or DOCX)",
            type=["pdf", "docx"]
        )

        generate_btn = st.button("OPTIMIZE RESUME")

        # ---------- GENERATION ----------
        if generate_btn:

            if not uploaded_file or not job_description:
                st.warning("Please provide both resume and job description.")
                return

            with st.status("Analyzing alignment and optimizing resume...", expanded=True) as status:

                file_ext = uploaded_file.name.split('.')[-1].lower()
                original_text = model.extract_text(uploaded_file, file_ext)

                if not original_text:
                    status.update(label="Error extracting text.", state="error")
                    return

                optimized = model.generate_tailored_resume(
                    target_title,
                    job_description,
                    original_text
                )

                if optimized:
                    st.session_state.optimized_resume = optimized
                    status.update(label="Optimization Complete!", state="complete")
                else:
                    status.update(label="Optimization failed.", state="error")


    # =============================
    # OUTPUT SECTION
    # =============================
    with col_preview:

        st.subheader("4. Optimized Output")

        if st.session_state.optimized_resume:

            st.markdown("### ATS-Optimized Resume Draft")
            st.caption("You may edit the content before downloading.")

            edited_resume = st.text_area(
                "Live Editor",
                value=st.session_state.optimized_resume,
                height=450,
                key="resume_editor"
            )

            # Update session state with edits
            st.session_state.optimized_resume = edited_resume

            doc_download = model.create_word_doc(edited_resume)

            if doc_download:
                st.download_button(
                    label="Download Professional .DOCX",
                    data=doc_download,
                    file_name=f"Optimized_Resume_{target_title.replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

        else:
            st.info("Upload your resume and job details to generate an optimized version.")


    # -----------------------------
    # FOOTER
    # -----------------------------
    st.divider()
    st.markdown(
        "<center><small>Designed & Developed by Abhishek Jha</small></center>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
