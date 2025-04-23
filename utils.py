import os
import pdfplumber
import docx
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def extract_text_from_pdf(filepath):
    try:
        text = ''
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'
        return text.strip()
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def extract_text_from_docx(filepath):
    try:
        doc = docx.Document(filepath)
        return '\n'.join([para.text for para in doc.paragraphs]).strip()
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

def analyze_resume(filepath, city):
    file_ext = filepath.split('.')[-1].lower()

    if file_ext == 'pdf':
        content = extract_text_from_pdf(filepath)
    elif file_ext == 'docx':
        content = extract_text_from_docx(filepath)
    else:
        return {"error": "Unsupported file format. Only PDF and DOCX allowed."}

    if not content or content.startswith("Error"):
        return {"error": "Could not extract readable text from the resume."}

    prompt = f"""
You are an expert career counselor, resume analyzer, and job market researcher.

Carefully analyze the following resume content. Provide crisp, bullet-pointed responses for these 7 points. Do not number the answers.

Sections:
- Assessment (resume positioning and market impression)
- Gaps/Weaknesses (red flags, missing elements, reasons for rejection)
- Power Keywords to Add (2-3 strong keywords or phrases for ATS and recruiters)
- Resume Improvement Suggestions (3-5 actionable improvements)
- ATS Friendliness Check (Yes/No + 2 lines explanation)
- Recommended Job Roles (5-7 suitable job positions)
- Suggested Companies in {city} (20 specific company names with their locations)

Resume content:
{content}

Please label each section clearly with the section heading above. Use bullet points inside each section but do not number the sections themselves. Stay precise and avoid long paragraphs.

    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        answer = response.choices[0].message.content
        return {"result": answer}

    except Exception as e:
        return {"error": f"GPT analysis failed: {str(e)}"}
