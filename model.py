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
        doc = docx.Document(uploaded_file)
    except Exception as e:
        st.error(f"Invalid Word document: {e}")
        return None

    original_paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]

    if not original_paragraphs:
        st.error("No readable text found in document.")
        return None

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            response_format={ "type": "json_object" }
        )
        
        # --- FIX STARTS HERE ---
        raw_content = response.choices[0].message.content
        
        if not raw_content:
            st.error("AI returned an empty response. Try reducing content length.")
            return None
        
        data = json.loads(raw_content)
        # --- FIX ENDS HERE ---
        
        if isinstance(data, dict):
            optimized_paragraphs = list(data.values())[0] if len(data) == 1 else data
        else:
            optimized_paragraphs = data

    except Exception as e:
        st.error(f"AI optimization failed: {e}")
        return None

    if len(optimized_paragraphs) != len(original_paragraphs):
        st.error(f"Structure mismatch: Input {len(original_paragraphs)} vs Output {len(optimized_paragraphs)}.")
        return None

    index = 0
    for para in doc.paragraphs:
        if para.text.strip():
            for run in para.runs:
                run.text = ""
            
            if para.runs:
                para.runs[0].text = optimized_paragraphs[index]
            else:
                para.add_run(optimized_paragraphs[index])
                
            index += 1

    output = io.BytesIO()
    doc.save(output)
    output.seek(0)

    return output
