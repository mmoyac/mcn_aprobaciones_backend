import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request, status, Depends, Response
from fastapi.responses import Response as FastAPIResponse
from app.core.api_key import verify_api_key
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.session_postgres import get_postgres_db
from app.db.tenant_session import create_tenant_session
from app.models.documento_pdf import DocumentoPDF
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()


def _get_tenant_id(request: Request) -> int:
    """Extrae tenant_id del request state. Lanza 404 si no hay tenant."""
    tenant = getattr(request.state, "tenant", None)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado para este dominio")
    return tenant.id


@router.get("/get")
async def get_documento_pdf(
    tipo: int,
    numero: int,
    request: Request,
    db: Session = Depends(get_postgres_db),
    _: bool = Depends(verify_api_key)
):
    tenant_id = _get_tenant_id(request)
    instance = db.query(DocumentoPDF).filter_by(tipo=tipo, numero=numero, tenant_id=tenant_id).first()
    if not instance or not instance.pdf:
        raise HTTPException(status_code=404, detail="Documento PDF no encontrado")
    return FastAPIResponse(content=instance.pdf, media_type="application/pdf")


@router.post("/upsert")
async def upsert_documento_pdf(
    tipo: int = Form(...),
    numero: int = Form(...),
    pdf: UploadFile = File(...),
    request: Request = None,
    db: Session = Depends(get_postgres_db),
    response: Response = None,
    _: bool = Depends(verify_api_key)
):
    tenant_id = _get_tenant_id(request)
    try:
        instance = db.query(DocumentoPDF).filter_by(tipo=tipo, numero=numero, tenant_id=tenant_id).first()
        pdf_bytes = await pdf.read()
        if instance:
            instance.pdf = pdf_bytes
            db.commit()
            db.refresh(instance)
            response.status_code = 200
            return {"id": instance.id, "tipo": instance.tipo, "numero": instance.numero, "tenant_id": instance.tenant_id}
        else:
            new_doc = DocumentoPDF(tipo=tipo, numero=numero, pdf=pdf_bytes, tenant_id=tenant_id)
            db.add(new_doc)
            db.commit()
            db.refresh(new_doc)
            response.status_code = 201
            return {"id": new_doc.id, "tipo": new_doc.tipo, "numero": new_doc.numero, "tenant_id": new_doc.tenant_id}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-cliente")
async def get_pdf_cliente(
    loc_cod: int,
    tipo: int,
    numero: int,
    request: Request,
    _: bool = Depends(verify_api_key)
):
    """
    Obtiene un PDF desde la tabla pdf001 de la base de datos del cliente (lexascl_reppdf).
    El emp_cd (PdfEmpCd) se resuelve automáticamente del tenant del request.

    Parámetros:
        loc_cod: Código de local (PdfLocCod)
        tipo:    Tipo de documento (PdfTipo)
        numero:  Número de documento (PdfNumero)
    """
    tenant = getattr(request.state, "tenant", None)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado para este dominio")
    emp_cd = tenant.id

    host = os.getenv("REPPDF_HOST", "179.27.210.204")
    port = int(os.getenv("REPPDF_PORT", "3306"))
    db_name = os.getenv("REPPDF_DB", "lexascl_reppdf")
    user = os.getenv("REPPDF_USER")
    password = os.getenv("REPPDF_PASSWORD")

    if not user or not password:
        raise HTTPException(status_code=503, detail="Credenciales de base de datos de PDFs no configuradas")

    db_cliente = create_tenant_session(
        db_host=host,
        db_port=port,
        db_name=db_name,
        db_user=user,
        db_password=password
    )

    try:
        result = db_cliente.execute(
            text("""
                SELECT PdfBlob FROM pdf001
                WHERE PdfEmpCd = :emp_cd
                  AND PdfLocCod = :loc_cod
                  AND PdfTipo   = :tipo
                  AND PdfNumero = :numero
                LIMIT 1
            """),
            {"emp_cd": emp_cd, "loc_cod": loc_cod, "tipo": tipo, "numero": numero}
        )
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="PDF no encontrado en la base de datos del cliente")
        if not row[0] or len(bytes(row[0])) == 0:
            raise HTTPException(status_code=422, detail="El registro existe pero no tiene contenido PDF")

        return FastAPIResponse(content=bytes(row[0]), media_type="application/pdf")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener PDF del cliente: {str(e)}")
    finally:
        db_cliente.close()
