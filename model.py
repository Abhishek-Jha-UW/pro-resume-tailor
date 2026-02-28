import io
import docx
from pypdf import PdfReader
from openai import OpenAI
import streamlit as st


# -----------------------------
# TEXT EXTRACTION
# -----------------------------
def extract_text(uploaded_file, file_type):
    """Safely extracts raw text from uploaded PDF or DOCX files."""
    text = ""

    try:
        if file_type == "pdf":
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"

        elif file_type == "docx":
            doc = docx.Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"

    except Exception as e:
        st.error(
            "Error reading your file. Please ensure it is a valid PDF or DOCX."
        )
        return None

    return text.strip()


# -----------------------------
# OPENAI RESUME GENERATION
# -----------------------------
def generate_tailored_resume(job_title, job_desc, original_resume):
    """Calls OpenAI to optimize the resume based on the job description."""

    # Guardrail: prevent massive inputs
    if len(original_resume.split()) > 2500:
        st.warning("Resume is too long. Please upload a resume under 2500 words.")
        return None

    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        system_prompt = (
            "You are an elite Executive Recruiter and ATS Optimization Expert.\n\n"

            "CORE OBJECTIVE:\n"
            "Rewrite the candidate's resume to maximize alignment with the job description "
            "while preserving authenticity and credibility.\n\n"

            "RULES:\n"
            "1. MAXIMUM RETENTION: Preserve real company names, roles, and dates.\n"
            "2. DO NOT invent new companies, job titles, or degrees.\n"
            "3. You may reframe responsibilities to logically incorporate required skills.\n"
            "4. Use exact terminology from the job description where appropriate.\n"
            "5. Every bullet must start with a strong action verb.\n"
            "6. Quantify achievements with metrics whenever possible.\n"
            "7. Maintain professional, concise language.\n"
            "8. Ensure important keywords appear in both Core Skills and Experience.\n"
            "9. Keep the resume within 1–2 pages.\n\n"

            "FORMAT STRICTLY AS:\n"
            "### Name & Contact\n"
            "### Professional Summary\n"
            "### Core Skills\n"
            "### Experience\n"
            "### Education\n\n"

            "FORMATTING RULES:\n"
            "- Use '###' for section headers\n"
            "- Use '-' for bullet points\n"
            "- Output ONLY the resume text. No explanations."
        )

        user_prompt = (
            f"TARGET ROLE: {job_title}\n\n"
            f"JOB DESCRIPTION:\n{job_desc}\n\n"
            f"ORIGINAL RESUME:\n{original_resume}"
        )

        response = client.responses.create(
            model="gpt-4o",
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.4,
            max_output_tokens=2000
        )

        return response.output_text.strip()

    except Exception as e:
        st.error("Error generating resume. Please try again later.")
        return None


# -----------------------------
# WORD DOCUMENT CREATION
# -----------------------------
def create_word_doc(generated_text):
    """
    Converts AI-generated Markdown-style resume
    into a formatted Word document.
    """
    if not generated_text:
        return None

    doc = docx.Document()

    for line in generated_text.split("\n"):
        line = line.strip()

        if not line:
            continue

        # Section Headers
        if line.startswith("###"):
            clean_text = line.replace("###", "").strip()
            doc.add_heading(clean_text.title(), level=2)

        # Bullet Points
        elif line.startswith("-"):
            clean_text = line.replace("-", "", 1).strip()
            doc.add_paragraph(clean_text, style="List Bullet")

        # Normal Paragraph
        else:
            doc.add_paragraph(line)

    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)

    return bio
