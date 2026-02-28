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
        # Load Word file
        doc = docx.Document(uploaded_file)
    except Exception as e:
        st.error(f"Invalid Word document: {e}")
        return None

    # Extract non-empty paragraphs to match against
    original_paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]

    if not original_paragraphs:
        st.error("No readable text found in document.")
        return None

    # Initialize OpenAI Client
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    # Refined prompt for maximum structural rigidity
    system_prompt = """
You are an ATS resume optimization expert. 
Rewrite each paragraph provided in the input list to better align with the job description.

STRICT RULES:
1.  **Count Constraint**: You must return exactly the same number of paragraphs as provided in the input list.
2.  **Order Constraint**: The order of paragraphs must remain identical to the input list.
3.  **Content Constraint**: Do not introduce new sections, headers, or fictional information.
4.  **Format Constraint**: Return output strictly as a JSON array of strings: ["para1", "para2", ...].
5.  **No Explanation**: Do not include any text before or after the JSON array.
"""

    user_prompt = f"TARGET ROLE: {job_title}\n\nJD: {job_description}\n\nRESUME: {json.dumps(original_paragraphs)}"

    try:
        # Correct API call for chat completion
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            response_format={ "type": "json_object" } # Ensures valid JSON structure
        )
        
        raw_content = response.choices[0].message.content
        data = json.loads(raw_content)
        
        # Handle potential dictionary wrapper from json_object mode
        if isinstance(data, dict):
            optimized_paragraphs = list(data.values())[0] if len(data) == 1 else data
        else:
            optimized_paragraphs = data

    except Exception as e:
        st.error(f"AI optimization failed: {e}")
        return None

    # Final Safety Check
    if len(optimized_paragraphs) != len(original_paragraphs):
        st.error(f"Structure mismatch: Input {len(original_paragraphs)} vs Output {len(optimized_paragraphs)}.")
        return None

    # Replace text while preserving paragraph-level formatting
    index = 0
    for para in doc.paragraphs:
        if para.text.strip():
            # Clear existing runs to preserve paragraph style, but remove old text
            for run in para.runs:
                run.text = ""
            
            # Add new text to the first run
            if para.runs:
                para.runs[0].text = optimized_paragraphs[index]
            else:
                para.add_run(optimized_paragraphs[index])
                
            index += 1

    # Save to buffer
    output = io.BytesIO()
    doc.save(output)
    output.seek(0)

    return output
