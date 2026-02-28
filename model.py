import io
import docx
from openai import OpenAI
import streamlit as st


# -----------------------------
# OPTIMIZE WORD DOCUMENT IN-PLACE
# -----------------------------
def optimize_docx_resume(uploaded_file, job_title, job_description):
    """
    Preserves formatting and replaces only text content
    inside the existing Word document.
    """

    try:
        doc = docx.Document(uploaded_file)
    except Exception:
        st.error("Invalid Word document.")
        return None

    # Extract paragraphs
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    if not paragraphs:
        st.error("Could not extract text from document.")
        return None

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    system_prompt = """
    You are an elite ATS resume optimization expert.

    Your job:
    Rewrite each paragraph to better align with the job description,
    while preserving original meaning and credibility.

    STRICT RULES:
    - Do NOT add new sections.
    - Do NOT remove sections.
    - Do NOT change ordering.
    - Do NOT invent new companies or roles.
    - Return optimized text in the exact same number of paragraphs.
    - Return results as a JSON list of strings.
    """

    user_prompt = f"""
    TARGET ROLE: {job_title}

    JOB DESCRIPTION:
    {job_description}

    RESUME PARAGRAPHS:
    {paragraphs}
    """

    try:
        response = client.responses.create(
            model="gpt-4o",
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_output_tokens=2000
        )

        optimized_paragraphs = eval(response.output_text)

    except Exception as e:
        st.error("AI optimization failed.")
        return None

    # Replace paragraph text while preserving formatting
    index = 0
    for para in doc.paragraphs:
        if para.text.strip():
            if index < len(optimized_paragraphs):
                para.text = optimized_paragraphs[index]
                index += 1

    # Save updated document
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)

    return bio
