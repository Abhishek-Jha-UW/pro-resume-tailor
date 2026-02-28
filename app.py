import streamlit as st
import model  # Importing our logic from model.py

# --- Page Configuration ---
st.set_page_config(
    page_title="ResumeAlign Pro | AI Career Suite",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom Professional Styling ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #004a99;
        color: white;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #003366;
        color: white;
    }
    .reportview-container .main .block-container {
        padding-top: 2rem;
    }
    h1 {
        color: #1c1c1c;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    </style>
    """, unsafe_allow_view_allowed=True)

def main():
    # --- Header ---
    st.title("💼 ResumeAlign Pro")
    st.markdown("##### *Enterprise-grade AI resume optimization for technical and financial analysts.*")
    st.divider()

    # --- Main Dashboard Layout ---
    col_input, col_preview = st.columns([1, 1], gap="large")

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
            target_title = st.text_input("Enter Custom Job Title", placeholder="e.g. Senior Quantitative Researcher")
        else:
            target_title = selected_role

        st.subheader("2. Job Requirements")
        job_description = st.text_area(
            "Paste the complete Job Description / Requirements:",
            height=250,
            placeholder="Paste text here... The AI will extract key competencies and required technologies."
        )

        st.subheader("3. Source Document")
        uploaded_file = st.file_uploader("Upload your current resume (PDF or DOCX)", type=["pdf", "docx"])

        generate_btn = st.button("OPTIMIZE RESUME")

    # --- Processing & Output ---
    with col_preview:
        st.subheader("4. Optimization Output")
        
        if generate_btn:
            if not uploaded_file or not job_description:
                st.warning("⚠️ Action Required: Please provide both a resume file and a job description to proceed.")
            else:
                # Using a status container for a professional 'processing' feel
                with st.status("Analyzing alignment...", expanded=True) as status:
                    st.write("Extracting source text...")
                    file_ext = uploaded_file.name.split('.')[-1].lower()
                    original_text = model.extract_text(uploaded_file, file_ext)
                    
                    if original_text:
                        st.write("Mapping keywords to Job Description...")
                        st.write("Synthesizing 'Truth-Adjacent' metrics...")
                        
                        # Call the AI Logic
                        optimized_resume = model.generate_tailored_resume(
                            target_title, 
                            job_description, 
                            original_text
                        )
                        
                        status.update(label="Optimization Complete!", state="complete", expanded=False)

                        # Display Preview
                        st.markdown("### Preview Optimized Draft")
                        st.info("The text below has been restructured for ATS compatibility and keyword density.")
                        st.text_area("Live Editor", value=optimized_resume, height=400)

                        # Create the Word Doc for Download
                        doc_download = model.create_word_doc(optimized_resume)
                        
                        st.download_button(
                            label="📥 DOWNLOAD PROFESSIONAL .DOCX",
                            data=doc_download,
                            file_name=f"Optimized_Resume_{target_title.replace(' ', '_')}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
                    else:
                        status.update(label="Error reading file.", state="error")
        else:
            # Placeholder when no resume is generated yet
            st.info("Upload your details and click 'Optimize' to view the generated resume here.")
            

if __name__ == "__main__":
    main()
