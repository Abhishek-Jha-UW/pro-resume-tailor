import streamlit as st
import model

st.set_page_config(
    page_title="ResumeAlign Pro",
    layout="centered"
)

st.title("ResumeAlign Pro")
st.caption("Optimize your resume while preserving your original Word formatting.")

st.divider()

# --- Session State Management ---
if "optimized_doc" not in st.session_state:
    st.session_state.optimized_doc = None
if "file_name" not in st.session_state:
    st.session_state.file_name = "Optimized_Resume.docx"

# --- UI Inputs ---
job_title = st.text_input("Target Job Title", placeholder="Senior Software Engineer")
job_description = st.text_area(
    "Paste Job Description",
    height=200,
    placeholder="Paste the requirements here..."
)

uploaded_file = st.file_uploader(
    "Upload Word Resume (.docx only)",
    type=["docx"]
)

# --- Action ---
if st.button("Optimize Resume"):
    if not uploaded_file or not job_description:
        st.warning("Please upload a resume and paste a job description.")
    else:
        with st.spinner("Optimizing your resume (this may take a minute)..."):
            
            # Call model
            result = model.optimize_docx_resume(
                uploaded_file,
                job_title,
                job_description
            )
            
            if result:
                st.success("Optimization complete!")
                # Store in session state
                st.session_state.optimized_doc = result
                st.session_state.file_name = f"Optimized_{uploaded_file.name}"
            else:
                st.error("Failed to generate document.")

# --- Persistent Download Button ---
if st.session_state.optimized_doc:
    st.divider()
    st.download_button(
        label="📥 Download Optimized Resume",
        data=st.session_state.optimized_doc,
        file_name=st.session_state.file_name,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
