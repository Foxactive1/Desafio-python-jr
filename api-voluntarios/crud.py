"""
Operações CRUD para certificados
"""
from typing import List, Optional, Dict, Any
from datetime import date
import models, schemas, database


def get_certificate(db: database.FakeDatabase, certificate_id: int) -> Optional[models.Certificate]:
    """Obtém um certificado pelo ID"""
    certificate = db.get_certificate(certificate_id)
    if certificate and not certificate.is_deleted:
        return certificate
    return None


def get_certificates(
    db: database.FakeDatabase,
    skip: int = 0,
    limit: int = 100,
    **filters
) -> List[models.Certificate]:
    """Lista certificados com filtros"""
    all_certificates = db.get_all_certificates()
    
    # Aplicar filtros
    filtered_certificates = []
    
    for cert in all_certificates:
        # Ignorar certificados excluídos
        if cert.is_deleted:
            continue
        
        # Aplicar filtros
        if filters.get("user_id") and cert.user_id != filters["user_id"]:
            continue
        
        if filters.get("course_id") and cert.course_id != filters["course_id"]:
            continue
        
        if filters.get("status") and cert.status != filters["status"]:
            continue
        
        if filters.get("issue_date_start") and cert.issue_date < filters["issue_date_start"]:
            continue
        
        if filters.get("issue_date_end") and cert.issue_date > filters["issue_date_end"]:
            continue
        
        if filters.get("expiration_date_start") and cert.expiration_date < filters["expiration_date_start"]:
            continue
        
        if filters.get("expiration_date_end") and cert.expiration_date > filters["expiration_date_end"]:
            continue
        
        filtered_certificates.append(cert)
    
    # Aplicar paginação
    return filtered_certificates[skip:skip + limit]


def create_certificate(
    db: database.FakeDatabase,
    certificate: schemas.CertificateCreate
) -> models.Certificate:
    """Cria um novo certificado"""
    # Converter schema para modelo
    cert_model = models.Certificate(
        id=0,  # Será definido pelo banco de dados
        user_id=certificate.user_id,
        username=certificate.username,
        course_id=certificate.course_id,
        course_name=certificate.course_name,
        issue_date=certificate.issue_date,
        expiration_date=certificate.expiration_date,
        status=certificate.status,
        is_deleted=False
    )
    
    # Salvar no banco de dados
    return db.add_certificate(cert_model)


def update_certificate(
    db: database.FakeDatabase,
    certificate_id: int,
    certificate_update: schemas.CertificateUpdate
) -> Optional[models.Certificate]:
    """Atualiza um certificado"""
    # Verificar se o certificado existe
    existing_cert = get_certificate(db, certificate_id)
    if not existing_cert:
        return None
    
    # Preparar dados para atualização
    update_data = certificate_update.dict(exclude_unset=True)
    
    # Atualizar no banco de dados
    return db.update_certificate(certificate_id, **update_data)


def delete_certificate(db: database.FakeDatabase, certificate_id: int) -> bool:
    """Exclui um certificado (soft delete)"""
    # Verificar se o certificado existe
    existing_cert = get_certificate(db, certificate_id)
    if not existing_cert:
        return False
    
    # Marcar como excluído
    return db.delete_certificate(certificate_id)


def restore_certificate(db: database.FakeDatabase, certificate_id: int) -> Optional[models.Certificate]:
    """Restaura um certificado excluído"""
    certificate = db.get_certificate(certificate_id)
    if not certificate:
        return None
    
    # Restaurar certificado
    return db.restore_certificate(certificate_id)