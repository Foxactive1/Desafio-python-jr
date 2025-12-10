"""
API Principal - Endpoints da aplicação para Voluntários
"""
from fastapi import FastAPI, Depends, HTTPException, Query
from typing import List, Optional

import crud, schemas, models, database
from dependencies import get_db

app = FastAPI(
    title="Volunteer Management API",
    description="API para gerenciamento de voluntários",
    version="1.0.0"
)


@app.get("/")
def read_root():
    """Endpoint raiz"""
    return {"message": "API de Gerenciamento de Voluntários - Challenge Técnico"}


@app.post("/voluntarios/", response_model=schemas.Volunteer, status_code=201)
def create_volunteer(
    volunteer: schemas.VolunteerCreate,
    db: database.FakeDatabase = Depends(get_db)
):
    """Cria um novo voluntário"""
    try:
        return crud.create_volunteer(db, volunteer)
    except ValueError as e:
        if "Email já cadastrado" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/voluntarios/", response_model=List[schemas.Volunteer])
def read_volunteers(
    skip: int = Query(0, ge=0, description="Número de itens para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de resultados"),
    cargo_pretendido: Optional[str] = Query(None, description="Filtrar por cargo pretendido"),
    disponibilidade: Optional[models.Disponibilidade] = Query(None, description="Filtrar por disponibilidade"),
    status: Optional[models.StatusVoluntario] = Query(None, description="Filtrar por status"),
    db: database.FakeDatabase = Depends(get_db)
):
    """Lista voluntários com filtros"""
    filters = {
        "cargo_pretendido": cargo_pretendido,
        "disponibilidade": disponibilidade,
        "status": status,
    }
    
    # Remover filtros None
    filters = {k: v for k, v in filters.items() if v is not None}
    
    volunteers = crud.get_volunteers(db, skip=skip, limit=limit, **filters)
    return volunteers


@app.get("/voluntarios/{volunteer_id}", response_model=schemas.Volunteer)
def read_volunteer(
    volunteer_id: int,
    db: database.FakeDatabase = Depends(get_db)
):
    """Obtém um voluntário pelo ID"""
    volunteer = crud.get_volunteer(db, volunteer_id)
    if volunteer is None:
        raise HTTPException(status_code=404, detail="Voluntário não encontrado")
    return volunteer


@app.put("/voluntarios/{volunteer_id}", response_model=schemas.Volunteer)
def update_volunteer(
    volunteer_id: int,
    volunteer_update: schemas.VolunteerUpdate,
    db: database.FakeDatabase = Depends(get_db)
):
    """Atualiza um voluntário"""
    try:
        volunteer = crud.update_volunteer(db, volunteer_id, volunteer_update)
        if volunteer is None:
            raise HTTPException(status_code=404, detail="Voluntário não encontrado")
        return volunteer
    except ValueError as e:
        if "Email já cadastrado" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/voluntarios/{volunteer_id}")
def delete_volunteer(
    volunteer_id: int,
    db: database.FakeDatabase = Depends(get_db)
):
    """Exclui um voluntário (soft delete)"""
    success = crud.delete_volunteer(db, volunteer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Voluntário não encontrado")
    return {"message": "Voluntário excluído com sucesso"}


@app.post("/voluntarios/{volunteer_id}/restore", response_model=schemas.Volunteer)
def restore_volunteer(
    volunteer_id: int,
    db: database.FakeDatabase = Depends(get_db)
):
    """Restaura um voluntário excluído"""
    volunteer = crud.restore_volunteer(db, volunteer_id)
    if volunteer is None:
        raise HTTPException(status_code=404, detail="Voluntário não encontrado")
    return volunteer


def main():
    """Função principal para execução"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
