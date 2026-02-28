import streamlit as st
import model


st.set_page_config(
    page_title="ResumeAlign Pro",
    layout="centered"
)

st.title("ResumeAlign Pro")
st.caption("AI-powered resume optimization while preserving your original formatting.")

st.divider()

job_title = st.text_input("Target Job Title")

job_description = st.text_area(
    "Paste Job Description",
    height=200
)

uploaded_file = st.file_uploader(
    "Upload your Word Resume (.docx only)",
    type=["docx"]
)

if st.button("Optimize Resume"):

    if not uploaded_file or not job_description:
        st.warning("Please provide resume and job description.")
    else:
        with st.spinner("Optimizing your resume..."):

            optimized_doc = model.optimize_docx_resume(
                uploaded_file,
                job_title,
                job_description
            )

            if optimized_doc:
                st.success("Optimization complete.")

                st.download_button(
                    label="Download Optimized Resume",
                    data=optimized_doc,
                    file_name="Optimized_Resume.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
