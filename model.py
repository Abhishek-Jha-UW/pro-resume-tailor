import io
import json
import docx
from openai import OpenAI
import streamlit as st


def optimize_docx_resume(uploaded_file, job_title, job_description):
    """
    Optimizes resume content while preserving original formatting.
    Works only with .docx files.
    """

    try:
        doc = docx.Document(uploaded_file)
    except Exception:
        st.error("Invalid Word document.")
        return None

    # Extract non-empty paragraphs
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]

    if not paragraphs:
        st.error("No readable text found in document.")
        return None

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    system_prompt = """
You are an ATS resume optimization expert.

Rewrite each paragraph to better align with the job description.

STRICT RULES:
- Keep the exact same number of paragraphs.
- Keep paragraph order unchanged.
- Do NOT invent companies, roles, or degrees.
- Return output strictly as a valid JSON list of strings.
"""

    user_prompt = f"""
TARGET ROLE: {job_title}

JOB DESCRIPTION:
{job_description}

RESUME PARAGRAPHS:
{json.dumps(paragraphs)}
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

        optimized_paragraphs = json.loads(response.output_text)

    except Exception as e:
        st.error("AI optimization failed.")
        return None

    # Safety check
    if len(optimized_paragraphs) != len(paragraphs):
        st.error("Paragraph mismatch detected. Try again.")
        return None

    # Replace text in-place (formatting preserved)
    index = 0
    for para in doc.paragraphs:
        if para.text.strip():
            para.text = optimized_paragraphs[index]
            index += 1

    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)

    return bio
