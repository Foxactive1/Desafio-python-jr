"""
API Principal - Endpoints da aplicação
"""
from fastapi import FastAPI, Depends, HTTPException, Query
from typing import List, Optional
from datetime import date

import crud, schemas, models, database
from dependencies import get_db

app = FastAPI(
    title="Certificate API",
    description="API para gerenciamento de certificados",
    version="1.0.0"
)


@app.get("/")
def read_root():
    """Endpoint raiz"""
    return {"message": "API de Certificados - Challenge Técnico"}


@app.post("/certificates/", response_model=schemas.Certificate, status_code=201)
def create_certificate(
    certificate: schemas.CertificateCreate,
    db: dict = Depends(get_db)
):
    """Cria um novo certificado"""
    return crud.create_certificate(db, certificate)


@app.get("/certificates/", response_model=List[schemas.Certificate])
def read_certificates(
    skip: int = Query(0, ge=0, description="Número de itens para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de resultados"),
    user_id: Optional[int] = Query(None, description="Filtrar por ID do usuário"),
    course_id: Optional[int] = Query(None, description="Filtrar por ID do curso"),
    status: Optional[models.CertificateStatus] = Query(None, description="Filtrar por status"),
    issue_date_start: Optional[date] = Query(None, description="Data de emissão inicial"),
    issue_date_end: Optional[date] = Query(None, description="Data de emissão final"),
    expiration_date_start: Optional[date] = Query(None, description="Data de expiração inicial"),
    expiration_date_end: Optional[date] = Query(None, description="Data de expiração final"),
    db: dict = Depends(get_db)
):
    """Lista certificados com filtros"""
    filters = {
        "user_id": user_id,
        "course_id": course_id,
        "status": status,
        "issue_date_start": issue_date_start,
        "issue_date_end": issue_date_end,
        "expiration_date_start": expiration_date_start,
        "expiration_date_end": expiration_date_end,
    }
    certificates = crud.get_certificates(db, skip=skip, limit=limit, **filters)
    return certificates


@app.get("/certificates/{certificate_id}", response_model=schemas.Certificate)
def read_certificate(
    certificate_id: int,
    db: dict = Depends(get_db)
):
    """Obtém um certificado pelo ID"""
    certificate = crud.get_certificate(db, certificate_id)
    if certificate is None:
        raise HTTPException(status_code=404, detail="Certificado não encontrado")
    return certificate


@app.put("/certificates/{certificate_id}", response_model=schemas.Certificate)
def update_certificate(
    certificate_id: int,
    certificate_update: schemas.CertificateUpdate,
    db: dict = Depends(get_db)
):
    """Atualiza um certificado"""
    certificate = crud.update_certificate(db, certificate_id, certificate_update)
    if certificate is None:
        raise HTTPException(status_code=404, detail="Certificado não encontrado")
    return certificate


@app.delete("/certificates/{certificate_id}")
def delete_certificate(
    certificate_id: int,
    db: dict = Depends(get_db)
):
    """Exclui um certificado (soft delete)"""
    success = crud.delete_certificate(db, certificate_id)
    if not success:
        raise HTTPException(status_code=404, detail="Certificado não encontrado")
    return {"message": "Certificado excluído com sucesso"}


@app.post("/certificates/{certificate_id}/restore", response_model=schemas.Certificate)
def restore_certificate(
    certificate_id: int,
    db: dict = Depends(get_db)
):
    """Restaura um certificado excluído"""
    certificate = crud.restore_certificate(db, certificate_id)
    if certificate is None:
        raise HTTPException(status_code=404, detail="Certificado não encontrado")
    return certificate


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)