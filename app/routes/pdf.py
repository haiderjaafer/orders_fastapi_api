from app.database.database import get_db
from app.database.config import settings
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Request ,UploadFile, File, Form
from app.models.pdf import PdfTableCreate
from app.services.pdf import PdfService

from sqlalchemy.orm import Session  






routerPdf = APIRouter(prefix="/api/pdfs", tags=["pdfs"])


base_path = settings.PDF_BASE_PATH

# You should define your base PDF folder
PDF_BASE_PATH = base_path

@routerPdf.post("/upload")
async def upload_pdf(
    orderID: int = Form(...),
    orderNo: str = Form(...),
    orderYear: str = Form(...),
    pdf: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validate PDF extension
    if not pdf.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    # Read file content
    file_content = await pdf.read()

    # Create PdfTableCreate model
    pdf_data = PdfTableCreate(
        orderID=orderID,
        orderNo=orderNo,
        orderYear=orderYear
    )

    try:
        result = PdfService.insert_pdf(db, pdf_data, file_content, PDF_BASE_PATH)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload PDF: {str(e)}")

    return {
        "message": "PDF uploaded successfully",
        "pdfID": result["pdfID"],
        "filePath": result["filePath"]
    }
