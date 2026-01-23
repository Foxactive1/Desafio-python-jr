"""
API Principal - Endpoints da aplicação para Voluntários
"""
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse  # Adicione esta importação
from fastapi.staticfiles import StaticFiles 
from typing import List, Optional
import os
import crud
import schemas
import models
import database
from dependencies import get_db

app = FastAPI(
    title="Volunteer Management API",
    description="API para gerenciamento de voluntários",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração CORS - Permitir todas as origens para desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/", tags=["Root"])
def read_root():
    """Endpoint raiz da API"""
    return {
        "message": "Bem-vindo à API de Gerenciamento de Voluntários",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "GET /voluntarios/": "Listar voluntários",
            "POST /voluntarios/": "Criar voluntário",
            "GET /voluntarios/{id}": "Obter voluntário por ID",
            "PUT /voluntarios/{id}": "Atualizar voluntário",
            "DELETE /voluntarios/{id}": "Excluir voluntário (soft delete)",
            "POST /voluntarios/{id}/restore": "Restaurar voluntário excluído"
        }
    }

@app.get("/index", tags=["Frontend"])
async def serve_index():
    """
    Serve o arquivo index.html da mesma pasta.
    
    Este endpoint retorna a interface web para gerenciamento de voluntários.
    """
    # Verifica se o arquivo index.html existe na mesma pasta
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    
    if not os.path.exists(index_path):
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Arquivo index.html não encontrado",
                "message": "O arquivo index.html não foi encontrado no diretório do servidor",
                "code": "INDEX_NOT_FOUND"
            }
        )
    
    return FileResponse(index_path, media_type="text/html")
    
@app.get("/health", tags=["Health"])
def health_check():
    """Endpoint de verificação de saúde da API"""
    return {"status": "healthy", "service": "volunteer-management-api"}


@app.post("/voluntarios/", 
          response_model=schemas.Volunteer, 
          status_code=201,
          tags=["Voluntários"],
          summary="Criar novo voluntário",
          description="Cria um novo registro de voluntário no sistema")
def create_volunteer(
    volunteer: schemas.VolunteerCreate,
    db: database.FakeDatabase = Depends(get_db)
):
    """
    Cria um novo voluntário com os dados fornecidos.
    
    - **nome**: Nome completo do voluntário
    - **email**: Email único do voluntário
    - **telefone**: Telefone para contato
    - **cargo_pretendido**: Cargo que o voluntário pretende ocupar
    - **disponibilidade**: Disponibilidade de horário (manha, tarde, noite, fim_de_semana, flexivel)
    - **status**: Status do voluntário (ativo, inativo, pendente)
    """
    try:
        return crud.create_volunteer(db, volunteer)
    except ValueError as e:
        if "Email já cadastrado" in str(e):
            raise HTTPException(
                status_code=409, 
                detail={
                    "error": "Conflito de email",
                    "message": str(e),
                    "code": "EMAIL_ALREADY_EXISTS"
                }
            )
        raise HTTPException(
            status_code=400, 
            detail={
                "error": "Dados inválidos",
                "message": str(e),
                "code": "VALIDATION_ERROR"
            }
        )


@app.get("/voluntarios/", 
         response_model=List[schemas.Volunteer],
         tags=["Voluntários"],
         summary="Listar voluntários",
         description="Retorna uma lista de voluntários com opções de filtro e paginação")

def read_volunteers(
    skip: int = Query(0, ge=0, description="Número de registros para pular (página atual * limite)"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros por página"),
    cargo_pretendido: Optional[str] = Query(None, description="Filtrar por cargo pretendido"),
    disponibilidade: Optional[models.Disponibilidade] = Query(None, description="Filtrar por disponibilidade"),
    status: Optional[models.StatusVoluntario] = Query(None, description="Filtrar por status"),
    db: database.FakeDatabase = Depends(get_db)
):
    """
    Lista todos os voluntários com suporte a filtros e paginação.
    
    - **skip**: Número de registros para pager (padrão: 0)
    - **limit**: Limite de registros por página (padrão: 100, máximo: 1000)
    - **cargo_pretendido**: Filtra por cargo pretendido (ex: "Instrutor")
    - **disponibilidade**: Filtra por disponibilidade (manha, tarde, noite, fim_de_semana, flexivel)
    - **status**: Filtra por status (ativo, inativo, pendente)
    
    Retorna apenas voluntários não excluídos (is_deleted = False).
    """
    filters = {
        "cargo_pretendido": cargo_pretendido,
        "disponibilidade": disponibilidade,
        "status": status,
    }
    
    # Remover filtros None
    filters = {k: v for k, v in filters.items() if v is not None}
    
    volunteers = crud.get_volunteers(db, skip=skip, limit=limit, **filters)
    
    return volunteers


@app.get("/voluntarios/{volunteer_id}", 
         response_model=schemas.Volunteer,
         tags=["Voluntários"],
         summary="Obter voluntário por ID",
         description="Retorna os detalhes de um voluntário específico")
def read_volunteer(
    volunteer_id: int,
    db: database.FakeDatabase = Depends(get_db)
):
    """
    Obtém um voluntário pelo ID.
    
    - **volunteer_id**: ID do voluntário a ser recuperado
    
    Retorna 404 se o voluntário não for encontrado ou estiver excluído.
    """
    volunteer = crud.get_volunteer(db, volunteer_id)
    if volunteer is None:
        raise HTTPException(
            status_code=404, 
            detail={
                "error": "Voluntário não encontrado",
                "message": f"Voluntário com ID {volunteer_id} não existe ou foi excluído",
                "code": "VOLUNTEER_NOT_FOUND"
            }
        )
    return volunteer


@app.put("/voluntarios/{volunteer_id}", 
         response_model=schemas.Volunteer,
         tags=["Voluntários"],
         summary="Atualizar voluntário",
         description="Atualiza os dados de um voluntário existente")
def update_volunteer(
    volunteer_id: int,
    volunteer_update: schemas.VolunteerUpdate,
    db: database.FakeDatabase = Depends(get_db)
):
    """
    Atualiza um voluntário existente.
    
    - **volunteer_id**: ID do voluntário a ser atualizado
    - **volunteer_update**: Objeto com os campos a serem atualizados
    
    Todos os campos são opcionais. Apenas os campos fornecidos serão atualizados.
    """
    try:
        volunteer = crud.update_volunteer(db, volunteer_id, volunteer_update)
        if volunteer is None:
            raise HTTPException(
                status_code=404, 
                detail={
                    "error": "Voluntário não encontrado",
                    "message": f"Voluntário com ID {volunteer_id} não existe ou foi excluído",
                    "code": "VOLUNTEER_NOT_FOUND"
                }
            )
        return volunteer
    except ValueError as e:
        if "Email já cadastrado" in str(e):
            raise HTTPException(
                status_code=409, 
                detail={
                    "error": "Conflito de email",
                    "message": str(e),
                    "code": "EMAIL_ALREADY_EXISTS"
                }
            )
        raise HTTPException(
            status_code=400, 
            detail={
                "error": "Dados inválidos",
                "message": str(e),
                "code": "VALIDATION_ERROR"
            }
        )


@app.delete("/voluntarios/{volunteer_id}", 
            tags=["Voluntários"],
            summary="Excluir voluntário",
            description="Realiza a exclusão lógica (soft delete) de um voluntário")
def delete_volunteer(
    volunteer_id: int,
    db: database.FakeDatabase = Depends(get_db)
):
    """
    Exclui um voluntário (soft delete).
    
    - **volunteer_id**: ID do voluntário a ser excluído
    
    Esta operação marca o voluntário como excluído (is_deleted = True),
    mas mantém o registro no banco de dados para possível recuperação.
    """
    success = crud.delete_volunteer(db, volunteer_id)
    if not success:
        raise HTTPException(
            status_code=404, 
            detail={
                "error": "Voluntário não encontrado",
                "message": f"Voluntário com ID {volunteer_id} não existe ou já foi excluído",
                "code": "VOLUNTEER_NOT_FOUND"
            }
        )
    return {
        "message": "Voluntário excluído com sucesso",
        "volunteer_id": volunteer_id,
        "can_restore": True
    }


@app.post("/voluntarios/{volunteer_id}/restore", 
          response_model=schemas.Volunteer,
          tags=["Voluntários"],
          summary="Restaurar voluntário",
          description="Restaura um voluntário previamente excluído")
def restore_volunteer(
    volunteer_id: int,
    db: database.FakeDatabase = Depends(get_db)
):
    """
    Restaura um voluntário excluído.
    
    - **volunteer_id**: ID do voluntário a ser restaurado
    
    Remove a marcação de exclusão (is_deleted = False) do voluntário.
    """
    volunteer = crud.restore_volunteer(db, volunteer_id)
    if volunteer is None:
        raise HTTPException(
            status_code=404, 
            detail={
                "error": "Voluntário não encontrado",
                "message": f"Voluntário com ID {volunteer_id} não existe",
                "code": "VOLUNTEER_NOT_FOUND"
            }
        )
    return volunteer


# Handler de erros personalizado
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": exc.detail.get("error", "Erro desconhecido") if isinstance(exc.detail, dict) else "Erro",
        "message": exc.detail.get("message", str(exc.detail)) if isinstance(exc.detail, dict) else str(exc.detail),
        "code": exc.detail.get("code", f"HTTP_{exc.status_code}") if isinstance(exc.detail, dict) else f"HTTP_{exc.status_code}",
        "path": request.url.path,
        "method": request.method
    }


def main():
    """Função principal para execução da API"""
    import uvicorn
    
    print("=" * 50)
    print("API de Gerenciamento de Voluntários")
    print("Versão: 1.0.0")
    print("Desenvolvido com FastAPI")
    print("=" * 50)
    print("\nEndpoints disponíveis:")
    print("  • GET  /          - Página inicial da API")
    print("  • GET  /index     - Interface web (index.html)")
    print("  • GET  /health    - Verificação de saúde")
    print("  • GET  /docs      - Documentação Swagger")
    print("  • GET  /redoc     - Documentação ReDoc")
    print("  • GET  /voluntarios/ - Listar voluntários")
    print("  • POST /voluntarios/ - Criar voluntário")
    print("  • GET  /voluntarios/{id} - Obter voluntário")
    print("  • PUT  /voluntarios/{id} - Atualizar voluntário")
    print("  • DELETE /voluntarios/{id} - Excluir voluntário")
    print("  • POST /voluntarios/{id}/restore - Restaurar voluntário")
    print("\nServidor iniciando...")
    print("=" * 50)
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()                "error": "Dados inválidos",
                "message": str(e),
                "code": "VALIDATION_ERROR"
            }
        )


@app.get("/voluntarios/", 
         response_model=List[schemas.Volunteer],
         tags=["Voluntários"],
         summary="Listar voluntários",
         description="Retorna uma lista de voluntários com opções de filtro e paginação")
def read_volunteers(
    skip: int = Query(0, ge=0, description="Número de registros para pular (página atual * limite)"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros por página"),
    cargo_pretendido: Optional[str] = Query(None, description="Filtrar por cargo pretendido"),
    disponibilidade: Optional[models.Disponibilidade] = Query(None, description="Filtrar por disponibilidade"),
    status: Optional[models.StatusVoluntario] = Query(None, description="Filtrar por status"),
    db: database.FakeDatabase = Depends(get_db)
):
    """
    Lista todos os voluntários com suporte a filtros e paginação.
    
    - **skip**: Número de registros para pager (padrão: 0)
    - **limit**: Limite de registros por página (padrão: 100, máximo: 1000)
    - **cargo_pretendido**: Filtra por cargo pretendido (ex: "Instrutor")
    - **disponibilidade**: Filtra por disponibilidade (manha, tarde, noite, fim_de_semana, flexivel)
    - **status**: Filtra por status (ativo, inativo, pendente)
    
    Retorna apenas voluntários não excluídos (is_deleted = False).
    """
    filters = {
        "cargo_pretendido": cargo_pretendido,
        "disponibilidade": disponibilidade,
        "status": status,
    }
    
    # Remover filtros None
    filters = {k: v for k, v in filters.items() if v is not None}
    
    volunteers = crud.get_volunteers(db, skip=skip, limit=limit, **filters)
    
    return volunteers


@app.get("/voluntarios/{volunteer_id}", 
         response_model=schemas.Volunteer,
         tags=["Voluntários"],
         summary="Obter voluntário por ID",
         description="Retorna os detalhes de um voluntário específico")
def read_volunteer(
    volunteer_id: int,
    db: database.FakeDatabase = Depends(get_db)
):
    """
    Obtém um voluntário pelo ID.
    
    - **volunteer_id**: ID do voluntário a ser recuperado
    
    Retorna 404 se o voluntário não for encontrado ou estiver excluído.
    """
    volunteer = crud.get_volunteer(db, volunteer_id)
    if volunteer is None:
        raise HTTPException(
            status_code=404, 
            detail={
                "error": "Voluntário não encontrado",
                "message": f"Voluntário com ID {volunteer_id} não existe ou foi excluído",
                "code": "VOLUNTEER_NOT_FOUND"
            }
        )
    return volunteer


@app.put("/voluntarios/{volunteer_id}", 
         response_model=schemas.Volunteer,
         tags=["Voluntários"],
         summary="Atualizar voluntário",
         description="Atualiza os dados de um voluntário existente")
def update_volunteer(
    volunteer_id: int,
    volunteer_update: schemas.VolunteerUpdate,
    db: database.FakeDatabase = Depends(get_db)
):
    """
    Atualiza um voluntário existente.
    
    - **volunteer_id**: ID do voluntário a ser atualizado
    - **volunteer_update**: Objeto com os campos a serem atualizados
    
    Todos os campos são opcionais. Apenas os campos fornecidos serão atualizados.
    """
    try:
        volunteer = crud.update_volunteer(db, volunteer_id, volunteer_update)
        if volunteer is None:
            raise HTTPException(
                status_code=404, 
                detail={
                    "error": "Voluntário não encontrado",
                    "message": f"Voluntário com ID {volunteer_id} não existe ou foi excluído",
                    "code": "VOLUNTEER_NOT_FOUND"
                }
            )
        return volunteer
    except ValueError as e:
        if "Email já cadastrado" in str(e):
            raise HTTPException(
                status_code=409, 
                detail={
                    "error": "Conflito de email",
                    "message": str(e),
                    "code": "EMAIL_ALREADY_EXISTS"
                }
            )
        raise HTTPException(
            status_code=400, 
            detail={
                "error": "Dados inválidos",
                "message": str(e),
                "code": "VALIDATION_ERROR"
            }
        )


@app.delete("/voluntarios/{volunteer_id}", 
            tags=["Voluntários"],
            summary="Excluir voluntário",
            description="Realiza a exclusão lógica (soft delete) de um voluntário")
def delete_volunteer(
    volunteer_id: int,
    db: database.FakeDatabase = Depends(get_db)
):
    """
    Exclui um voluntário (soft delete).
    
    - **volunteer_id**: ID do voluntário a ser excluído
    
    Esta operação marca o voluntário como excluído (is_deleted = True),
    mas mantém o registro no banco de dados para possível recuperação.
    """
    success = crud.delete_volunteer(db, volunteer_id)
    if not success:
        raise HTTPException(
            status_code=404, 
            detail={
                "error": "Voluntário não encontrado",
                "message": f"Voluntário com ID {volunteer_id} não existe ou já foi excluído",
                "code": "VOLUNTEER_NOT_FOUND"
            }
        )
    return {
        "message": "Voluntário excluído com sucesso",
        "volunteer_id": volunteer_id,
        "can_restore": True
    }


@app.post("/voluntarios/{volunteer_id}/restore", 
          response_model=schemas.Volunteer,
          tags=["Voluntários"],
          summary="Restaurar voluntário",
          description="Restaura um voluntário previamente excluído")
def restore_volunteer(
    volunteer_id: int,
    db: database.FakeDatabase = Depends(get_db)
):
    """
    Restaura um voluntário excluído.
    
    - **volunteer_id**: ID do voluntário a ser restaurado
    
    Remove a marcação de exclusão (is_deleted = False) do voluntário.
    """
    volunteer = crud.restore_volunteer(db, volunteer_id)
    if volunteer is None:
        raise HTTPException(
            status_code=404, 
            detail={
                "error": "Voluntário não encontrado",
                "message": f"Voluntário com ID {volunteer_id} não existe",
                "code": "VOLUNTEER_NOT_FOUND"
            }
        )
    return volunteer


# Handler de erros personalizado
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": exc.detail.get("error", "Erro desconhecido") if isinstance(exc.detail, dict) else "Erro",
        "message": exc.detail.get("message", str(exc.detail)) if isinstance(exc.detail, dict) else str(exc.detail),
        "code": exc.detail.get("code", f"HTTP_{exc.status_code}") if isinstance(exc.detail, dict) else f"HTTP_{exc.status_code}",
        "path": request.url.path,
        "method": request.method
    }


def main():
    """Função principal para execução da API"""
    import uvicorn
    
    print("=" * 50)
    print("API de Gerenciamento de Voluntários")
    print("Versão: 1.0.0")
    print("Desenvolvido com FastAPI")
    print("=" * 50)
    print("\nEndpoints disponíveis:")
    print("  • GET  /          - Página inicial da API")
    print("  • GET  /health    - Verificação de saúde")
    print("  • GET  /docs      - Documentação Swagger")
    print("  • GET  /redoc     - Documentação ReDoc")
    print("  • GET  /voluntarios/ - Listar voluntários")
    print("  • POST /voluntarios/ - Criar voluntário")
    print("  • GET  /voluntarios/{id} - Obter voluntário")
    print("  • PUT  /voluntarios/{id} - Atualizar voluntário")
    print("  • DELETE /voluntarios/{id} - Excluir voluntário")
    print("  • POST /voluntarios/{id}/restore - Restaurar voluntário")
    print("\nServidor iniciando...")
    print("=" * 50)
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()
