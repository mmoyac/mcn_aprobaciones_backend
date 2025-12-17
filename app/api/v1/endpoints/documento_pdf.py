from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends, Response
from fastapi.responses import Response as FastAPIResponse
from app.core.api_key import verify_api_key
from sqlalchemy.orm import Session
from app.db.session_postgres import get_postgres_db
from app.models.documento_pdf import DocumentoPDF
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()


@router.get("/get")
async def get_documento_pdf(
    tipo: int,
    numero: int,
    db: Session = Depends(get_postgres_db),
    _: bool = Depends(verify_api_key)
):
    instance = db.query(DocumentoPDF).filter_by(tipo=tipo, numero=numero).first()
    if not instance or not instance.pdf:
        raise HTTPException(status_code=404, detail="Documento PDF no encontrado")
    return FastAPIResponse(content=instance.pdf, media_type="application/pdf")



@router.post("/upsert")
async def upsert_documento_pdf(
    tipo: int = Form(...),
    numero: int = Form(...),
    pdf: UploadFile = File(...),
    db: Session = Depends(get_postgres_db),
    response: Response = None,
    _: bool = Depends(verify_api_key)
):
    try:
        instance = db.query(DocumentoPDF).filter_by(tipo=tipo, numero=numero).first()
        pdf_bytes = await pdf.read()
        if instance:
            instance.pdf = pdf_bytes
            db.commit()
            db.refresh(instance)
            response.status_code = 200
            return {"id": instance.id, "tipo": instance.tipo, "numero": instance.numero}
        else:
            new_doc = DocumentoPDF(tipo=tipo, numero=numero, pdf=pdf_bytes)
            db.add(new_doc)
            db.commit()
            db.refresh(new_doc)
            response.status_code = 201
            return {"id": new_doc.id, "tipo": new_doc.tipo, "numero": new_doc.numero}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
