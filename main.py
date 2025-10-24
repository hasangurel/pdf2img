from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
import io, fitz

app = FastAPI()

@app.post("/pdf2img")
async def pdf_to_img(file: UploadFile = File(...), page: int = 1, dpi: int = 200):
    data = await file.read()
    doc = fitz.open(stream=data, filetype="pdf")
    p = max(1, min(page, len(doc))) - 1
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    pix = doc[p].get_pixmap(matrix=mat, alpha=False)
    buf = io.BytesIO(pix.tobytes("png"))
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
