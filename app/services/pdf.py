from sqlalchemy.orm import Session  
from app.models.pdf import PdfTableCreate,PdfTableOut
from sqlalchemy import text
import os






class PdfService:
    @staticmethod
    def get_next_count(db: Session, order_id: int) -> int:
        query = text("SELECT MAX(countPdf) FROM dbo.pdfTable WHERE orderID = :order_id")
        result = db.execute(query, {"order_id": order_id}).scalar()
        return (result or 0) + 1

    @staticmethod
    def insert_pdf(db: Session, pdf_data: PdfTableCreate, file_content: bytes, base_path: str) -> dict:
        # Get next count
        count = PdfService.get_next_count(db, pdf_data.orderID)

        # Construct filename and path
        filename = f"{pdf_data.orderNo}.{pdf_data.orderYear}.{count}.pdf"
        full_path = os.path.join(base_path, filename)

        # Make sure base folder exists
        os.makedirs(base_path, exist_ok=True)

        # Save the file
        with open(full_path, 'wb') as f:
            f.write(file_content)

        # Insert into DB
        insert_query = text("""
            INSERT INTO dbo.pdfTable (orderID, orderNo, orderYear, countPdf, pdf)
            VALUES (:orderID, :orderNo, :orderYear, :countPdf, :pdf)
        """)

        db.execute(insert_query, {
            "orderID": pdf_data.orderID,
            "orderNo": pdf_data.orderNo,
            "orderYear": pdf_data.orderYear,
            "countPdf": count,
            "pdf": full_path
        })
        db.commit()

        # Get the last inserted pdfID
        get_id_query = text("SELECT IDENT_CURRENT('dbo.pdfTable')")
        pdf_id = db.execute(get_id_query).scalar()

        return {
            "pdfID": int(pdf_id),
            "filePath": full_path
        }

