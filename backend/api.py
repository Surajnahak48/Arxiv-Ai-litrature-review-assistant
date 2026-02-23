from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse
from backend.agents import run_review, stream_review
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

app = FastAPI(title="AI Literature Review API")

@app.get("/review")
async def review(topic: str, papers: int = 5):
    task = f"Conduct a literature review on {topic} and return exactly {papers} papers"
    return {"result": await run_review(task, papers)}

@app.get("/stream")
async def stream(topic: str, papers: int = 5):
    task = f"Conduct a literature review on {topic} and return exactly {papers} papers"
    return StreamingResponse(stream_review(task, papers), media_type="text/plain")

@app.get("/download")
async def download(topic: str, papers: int = 5):
    task = f"Conduct a literature review on {topic} and return exactly {papers} papers"
    text = await run_review(task, papers)

    file_path = "review.pdf"
    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()
    doc.build([Paragraph(text.replace("\n", "<br/>"), styles["Normal"])])

    return FileResponse(file_path, filename="literature_review.pdf")
