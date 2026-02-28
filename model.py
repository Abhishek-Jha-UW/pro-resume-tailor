import io
import json
import docx
from openai import OpenAI
import streamlit as st

def optimize_docx_resume(uploaded_file, job_title, job_description):
    """
    Optimize resume content while preserving original formatting.
    """
    try:
        # Load Word file from the UploadedFile object
        doc = docx.Document(uploaded_file)
    except Exception as e:
        st.error(f"Invalid Word document: {e}")
        return None

    # Extract non-empty paragraphs
    original_paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]

    if not original_paragraphs:
        st.error("No readable text found in document.")
        return None

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    system_prompt = """
You are an ATS resume optimization expert. 
Rewrite each paragraph to better align with the job description.

STRICT RULES:
- Keep EXACT same number of paragraphs.
- Keep paragraph order unchanged.
- Return output strictly as a JSON array of strings: ["para1", "para2", ...]
- No explanations or markdown formatting (no ```json).
"""

    user_prompt = f"TARGET ROLE: {job_title}\n\nJD: {job_description}\n\nRESUME: {json.dumps(original_paragraphs)}"

    try:
        # Fixed the API call syntax for GPT-4o
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            response_format={ "type": "json_object" } # Ensures valid JSON
        )
        
        # GPT-4o with json_object needs a key, or just parse the content
        raw_content = response.choices[0].message.content
        data = json.loads(raw_content)
        
        # Support both {"paragraphs": [...]} or a raw list if the AI shifts
        optimized_paragraphs = data if isinstance(data, list) else data.get("paragraphs", list(data.values())[0])

    except Exception as e:
        st.error(f"AI optimization failed: {e}")
        return None

    if len(optimized_paragraphs) != len(original_paragraphs):
        st.error("Paragraph count mismatch. The AI altered the structure.")
        return None

    # Replace text while attempting to preserve paragraph-level formatting
    index = 0
    for para in doc.paragraphs:
        if para.text.strip():
            # To preserve formatting, we clear the 'runs' but keep the paragraph style
            # This is the most reliable way to keep alignment/spacing
            new_text = optimized_paragraphs[index]
            
            # Clear existing runs
            for run in para.runs:
                run.text = ""
            
            # Add the new text to the first run (preserving its style) or create one
            if para.runs:
                para.runs[0].text = new_text
            else:
                para.add_run(new_text)
                
            index += 1

    # Save to buffer
    output = io.BytesIO()
    doc.save(output)
    output.seek(0)

    return output
