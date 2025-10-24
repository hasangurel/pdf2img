from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import io, fitz  # pip install pymupdf

app = FastAPI()

@app.get("/ping")
def ping():
    return {"ok": True}

@app.post("/pdf2img")
async def pdf_to_img(file: UploadFile = File(...), page: int = 1, dpi: int = 200):
    try:
        if not file:
            raise HTTPException(status_code=400, detail="file is required (multipart/form-data)")
        data = await file.read()
        if not data:
            raise HTTPException(status_code=400, detail="empty file")
        doc = fitz.open(stream=data, filetype="pdf")
        if doc.page_count == 0:
            raise HTTPException(status_code=400, detail="no pages in pdf")
        p = max(1, min(page, doc.page_count)) - 1
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)
        pix = doc[p].get_pixmap(matrix=mat, alpha=False)
        buf = io.BytesIO(pix.tobytes("png"))
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/png")
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
