from fastapi import FastAPI, Form, File, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from typing import Optional
import os
import openai
import fitz  # PyMuPDF
from docx import Document

# Create FastAPI app
app = FastAPI()

# Mount static directory (for CSS, JS, Logo)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates directory
templates = Jinja2Templates(directory="templates")

# Setup Together API Key
os.environ["TOGETHER_API_KEY"] = "Your_API_Key"
client = openai.OpenAI(
    api_key=os.environ.get("TOGETHER_API_KEY"),
    base_url="https://api.together.xyz/v1",
)

# 🧠 Extract text from PDF
def extract_text_from_pdf(file_bytes):
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

# 🧠 Extract text from DOCX
def extract_text_from_docx(file_bytes):
    with open("temp.docx", "wb") as f:
        f.write(file_bytes)
    doc = Document("temp.docx")
    text = "\n".join([para.text for para in doc.paragraphs])
    os.remove("temp.docx")
    return text

# 🧠 Unified content extractor
async def extract_content(text, file):
    if text and text.strip() != "":
        return text
    elif file:
        file_bytes = await file.read()
        filename = file.filename.lower()

        if filename.endswith(".pdf"):
            return extract_text_from_pdf(file_bytes)
        elif filename.endswith(".docx"):
            return extract_text_from_docx(file_bytes)
        elif filename.endswith(".txt"):
            return file_bytes.decode("utf-8")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type.")
    else:
        raise HTTPException(status_code=400, detail="Please provide either text or a file.")

# 🧠 Summarization logic
async def summarize_content(content: str):
    try:
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional summarization assistant.\n\n"
                        "Your task is to carefully read the provided content and generate a high-quality summary that is:\n"
                        "- Accurate and faithful to the original content\n"
                        "- Clear, concise, and logically structured\n"
                        "- Free from repetition or unnecessary detail\n"
                        "- Completely neutral, without inserting personal opinions\n"
                        "- Optimized for quick understanding by busy professionals\n\n"
                        "Rules:\n"
                        "- Do not add any new information or interpretation.\n"
                        "- Focus on capturing the main ideas and key details.\n"
                        "- Maintain the original tone and purpose of the content.\n"
                        "- If the text is long, condense it into 4–6 sentences.\n"
                        "- If appropriate, you may use bullet points for clarity."
                    )
                },
                {
                    "role": "user",
                    "content": f'Summarize the following content:\n\n"""\n{content}\n"""'
                }
            ]
        )
        summary = response.choices[0].message.content.strip()
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

# 🔁 POST: Summarization endpoint (for both text and document)
@app.post("/summarize")
async def summarize_post(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    content = await extract_content(text, file)
    return await summarize_content(content)

# 🌐 UI Routes (Templates)
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/text-summarizer", response_class=HTMLResponse)
async def text_summarizer(request: Request):
    return templates.TemplateResponse("text_summarizer.html", {"request": request})

@app.get("/doc-summarizer", response_class=HTMLResponse)
async def doc_summarizer(request: Request):
    return templates.TemplateResponse("doc_summarizer.html", {"request": request})
