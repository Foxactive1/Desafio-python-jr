"""
Operações CRUD para voluntários
"""
from typing import List, Optional
from datetime import date

import models, schemas, database


def get_volunteer(db: database.FakeDatabase, volunteer_id: int) -> Optional[models.Volunteer]:
    """Obtém um voluntário pelo ID"""
    volunteer = db.get_volunteer(volunteer_id)
    if volunteer and not volunteer.is_deleted:
        return volunteer
    return None


def get_volunteers(
    db: database.FakeDatabase,
    skip: int = 0,
    limit: int = 100,
    **filters
) -> List[models.Volunteer]:
    """Lista voluntários com filtros"""
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
        
        filtered_volunteers.append(vol)
    
    # Aplicar paginação
    return filtered_volunteers[skip:skip + limit]


def create_volunteer(
    db: database.FakeDatabase,
    volunteer: schemas.VolunteerCreate
) -> models.Volunteer:
    """Cria um novo voluntário"""
    # Verificar se email já existe
    if db.email_exists(volunteer.email):
        raise ValueError("Email já cadastrado")
    
    # Converter schema para modelo
    vol_model = models.Volunteer(
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
    return db.add_volunteer(vol_model)


def update_volunteer(
    db: database.FakeDatabase,
    volunteer_id: int,
    volunteer_update: schemas.VolunteerUpdate
) -> Optional[models.Volunteer]:
    """Atualiza um voluntário"""
    # Verificar se o voluntário existe
    existing_vol = get_volunteer(db, volunteer_id)
    if not existing_vol:
        return None
    
    # Verificar se o novo email já existe (para outro voluntário)
    if volunteer_update.email and db.email_exists(volunteer_update.email, exclude_id=volunteer_id):
        raise ValueError("Email já cadastrado")
    
    # Preparar dados para atualização
    update_data = volunteer_update.dict(exclude_unset=True)
    
    # Atualizar no banco de dados
    return db.update_volunteer(volunteer_id, **update_data)


def delete_volunteer(db: database.FakeDatabase, volunteer_id: int) -> bool:
    """Exclui um voluntário (soft delete)"""
    # Verificar se o voluntário existe
    existing_vol = get_volunteer(db, volunteer_id)
    if not existing_vol:
        return False
    
    # Marcar como excluído
    return db.delete_volunteer(volunteer_id)


def restore_volunteer(db: database.FakeDatabase, volunteer_id: int) -> Optional[models.Volunteer]:
    """Restaura um voluntário excluído"""
    volunteer = db.get_volunteer(volunteer_id)
    if not volunteer:
        return None
    
    # Restaurar voluntário
    return db.restore_volunteer(volunteer_id)