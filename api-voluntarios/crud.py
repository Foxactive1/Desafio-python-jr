"""
Operações CRUD para voluntários
"""
from typing import List, Optional
from datetime import date

from models import VolunteerInDB, VolunteerModel
import schemas, database


def get_volunteer(db: database.FakeDatabase, volunteer_id: int) -> Optional[VolunteerModel]:
    """Obtém um voluntário pelo ID e converte para Pydantic model"""
    volunteer = db.get_volunteer(volunteer_id)
    if volunteer and not volunteer.is_deleted:
        return volunteer.to_model()
    return None


def get_volunteers(
    db: database.FakeDatabase,
    skip: int = 0,
    limit: int = 100,
    **filters
) -> List[VolunteerModel]:
    """Lista voluntários com filtros e converte para Pydantic models"""
    all_volunteers = db.get_all_volunteers()
    
    # Aplicar filtros
    filtered_volunteers = []
    
    for vol in all_volunteers:
        # Ignorar voluntários excluídos
        if vol.is_deleted:
            continue
        
        # Aplicar filtros
        if filters.get("status") and vol.status != filters["status"]:
            continue
        
        if filters.get("cargo_pretendido") and vol.cargo_pretendido != filters["cargo_pretendido"]:
            continue
        
        if filters.get("disponibilidade") and vol.disponibilidade != filters["disponibilidade"]:
            continue
        
        filtered_volunteers.append(vol.to_model())
    
    # Aplicar paginação
    return filtered_volunteers[skip:skip + limit]


def create_volunteer(
    db: database.FakeDatabase,
    volunteer: schemas.VolunteerCreate
) -> VolunteerModel:
    """Cria um novo voluntário"""
    # Verificar se email já existe
    if db.email_exists(volunteer.email):
        raise ValueError("Email já cadastrado")
    
    # Converter schema para modelo de domínio
    vol_domain = VolunteerInDB(
        id=0,  # Será definido pelo banco de dados
        nome=volunteer.nome,
        email=volunteer.email,
        telefone=volunteer.telefone,
        cargo_pretendido=volunteer.cargo_pretendido,
        disponibilidade=volunteer.disponibilidade,
        status=volunteer.status,
        data_inscricao=date.today(),  # Data atual automaticamente
        is_deleted=False
    )
    
    # Salvar no banco de dados
    saved_volunteer = db.add_volunteer(vol_domain)
    
    # Retornar como Pydantic model
    return saved_volunteer.to_model()


def update_volunteer(
    db: database.FakeDatabase,
    volunteer_id: int,
    volunteer_update: schemas.VolunteerUpdate
) -> Optional[VolunteerModel]:
    """Atualiza um voluntário"""
    # Verificar se o voluntário existe
    existing_vol = db.get_volunteer(volunteer_id)
    if not existing_vol or existing_vol.is_deleted:
        return None
    
    # Verificar se o novo email já existe (para outro voluntário)
    if volunteer_update.email and db.email_exists(volunteer_update.email, exclude_id=volunteer_id):
        raise ValueError("Email já cadastrado")
    
    # Preparar dados para atualização
    update_data = volunteer_update.model_dump(exclude_unset=True)
    
    # Atualizar no banco de dados
    updated_volunteer = db.update_volunteer(volunteer_id, **update_data)
    if updated_volunteer:
        return updated_volunteer.to_model()
    
    return None


def delete_volunteer(db: database.FakeDatabase, volunteer_id: int) -> bool:
    """Exclui um voluntário (soft delete)"""
    # Verificar se o voluntário existe
    existing_vol = db.get_volunteer(volunteer_id)
    if not existing_vol or existing_vol.is_deleted:
        return False
    
    # Marcar como excluído
    return db.delete_volunteer(volunteer_id)


def restore_volunteer(db: database.FakeDatabase, volunteer_id: int) -> Optional[VolunteerModel]:
    """Restaura um voluntário excluído"""
    volunteer = db.get_volunteer(volunteer_id)
    if not volunteer:
        return None
    
    # Restaurar voluntário
    restored = db.restore_volunteer(volunteer_id)
    if restored:
        return restored.to_model()
    
    return None