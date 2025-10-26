from fastapi import FastAPI
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
import fitz  # PyMuPDF
import io
import requests
app = FastAPI()


app = FastAPI()

def download_pdf_from_drive(url: str) -> bytes:
    # Google Drive link formatı kontrolü
    if "drive.google.com" in url:
        # https://drive.google.com/file/d/FILE_ID/view?usp=sharing
        # formatındaysa:
        import re
        match = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
        if match:
            file_id = match.group(1)
            url = f"https://drive.google.com/uc?export=download&id={file_id}"

    response = requests.get(url, stream=True)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Failed to download file ({response.status_code})")
    return response.content

@app.get("/pdf2img")
def pdf_to_img_from_drive(link: str = Query(..., description="Drive veya direkt PDF URL'si"),
                          page: int = 1,
                          dpi: int = 200):
    try:
        data = download_pdf_from_drive(link)
        if not data:
            raise HTTPException(status_code=400, detail="Empty PDF data")

        doc = fitz.open(stream=data, filetype="pdf")
        if doc.page_count == 0:
            raise HTTPException(status_code=400, detail="No pages in PDF")

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

@app.get("/ping")
def ping():
    return {"ok": True}

