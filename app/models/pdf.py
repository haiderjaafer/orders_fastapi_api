from pydantic import BaseModel





class PdfTableCreate(BaseModel):
    orderID: int
    orderNo: str
    orderYear: str

class PdfTableOut(BaseModel):
    message: str
    pdfID: int
    filePath: str    
