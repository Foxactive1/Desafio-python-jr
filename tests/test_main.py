"""
Testes para a API de Voluntários
"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_criar_voluntario_valido():
    """Deve criar voluntário com dados válidos"""
    response = client.post(
        "/voluntarios/",
        json={
            "nome": "Novo Voluntário",
            "email": "novo@email.com",
            "telefone": "(11) 94444-4444",
            "cargo_pretendido": "Testador",
            "disponibilidade": "manha",
            "status": "pendente"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == "Novo Voluntário"
    assert data["email"] == "novo@email.com"
    assert data["cargo_pretendido"] == "Testador"
    assert "id" in data


def test_nao_permitir_email_duplicado():
    """Não deve permitir cadastro com email duplicado"""
    # Primeiro cadastro
    client.post(
        "/voluntarios/",
        json={
            "nome": "Voluntário Teste",
            "email": "teste@email.com",
            "telefone": "(11) 93333-3333",
            "cargo_pretendido": "Testador",
            "disponibilidade": "tarde",
            "status": "ativo"
        }
    )
    # Segundo cadastro com mesmo email
    response = client.post(
        "/voluntarios/",
        json={
            "nome": "Outro Voluntário",
            "email": "teste@email.com",
            "telefone": "(11) 92222-2222",
            "cargo_pretendido": "Instrutor",
            "disponibilidade": "noite",
            "status": "ativo"
        }
    )
    assert response.status_code == 409
    assert "Email já cadastrado" in response.json()["detail"]


def test_listar_voluntarios():
    """Deve listar voluntários com sucesso"""
    response = client.get("/voluntarios/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_buscar_voluntario_por_id():
    """Deve buscar voluntário por ID"""
    # Primeiro cria um voluntário
    create_response = client.post(
        "/voluntarios/",
        json={
            "nome": "Para Buscar",
            "email": "buscar@email.com",
            "telefone": "(11) 91111-1111",
            "cargo_pretendido": "Buscador",
            "disponibilidade": "flexivel",
            "status": "ativo"
        }
    )
    volunteer_id = create_response.json()["id"]
    
    # Busca pelo ID
    response = client.get(f"/voluntarios/{volunteer_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == volunteer_id


def test_buscar_voluntario_inexistente():
    """Deve retornar 404 para voluntário inexistente"""
    response = client.get("/voluntarios/999")
    assert response.status_code == 404


def test_atualizar_voluntario():
    """Deve atualizar voluntário com sucesso"""
    # Cria um voluntário
    create_response = client.post(
        "/voluntarios/",
        json={
            "nome": "Para Atualizar",
            "email": "atualizar@email.com",
            "telefone": "(11) 92222-2222",
            "cargo_pretendido": "Original",
            "disponibilidade": "manha",
            "status": "pendente"
        }
    )
    volunteer_id = create_response.json()["id"]
    
    # Atualiza o voluntário
    update_response = client.put(
        f"/voluntarios/{volunteer_id}",
        json={
            "nome": "Nome Atualizado",
            "cargo_pretendido": "Atualizado"
        }
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["nome"] == "Nome Atualizado"
    assert data["cargo_pretendido"] == "Atualizado"


def test_deletar_voluntario():
    """Deve deletar voluntário (soft delete)"""
    # Cria um voluntário
    create_response = client.post(
        "/voluntarios/",
        json={
            "nome": "Para Deletar",
            "email": "deletar@email.com",
            "telefone": "(11) 93333-3333",
            "cargo_pretendido": "Deletável",
            "disponibilidade": "tarde",
            "status": "ativo"
        }
    )
    volunteer_id = create_response.json()["id"]
    
    # Deleta o voluntário
    delete_response = client.delete(f"/voluntarios/{volunteer_id}")
    assert delete_response.status_code == 200
    
    # Tenta buscar o voluntário deletado
    get_response = client.get(f"/voluntarios/{volunteer_id}")
    assert get_response.status_code == 404


def test_filtrar_por_status():
    """Deve filtrar voluntários por status"""
    response = client.get("/voluntarios/?status=ativo")
    assert response.status_code == 200
    data = response.json()
    # Verifica que todos retornados têm status ativo
    for volunteer in data:
        assert volunteer["status"] == "ativo"


def test_filtrar_por_disponibilidade():
    """Deve filtrar voluntários por disponibilidade"""
    response = client.get("/voluntarios/?disponibilidade=manha")
    assert response.status_code == 200
    data = response.json()
    # Verifica que todos retornados têm disponibilidade manhã
    for volunteer in data:
        assert volunteer["disponibilidade"] == "manha"


def test_filtrar_por_cargo():
    """Deve filtrar voluntários por cargo pretendido"""
    response = client.get("/voluntarios/?cargo_pretendido=Instrutor")
    assert response.status_code == 200
    data = response.json()
    # Verifica que todos retornados têm cargo Instrutor
    for volunteer in data:
        assert volunteer["cargo_pretendido"] == "Instrutor"


def test_paginacao():
    """Deve aplicar paginação corretamente"""
    response = client.get("/voluntarios/?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 2


if __name__ == "__main__":
    # Executa os testes
    import pytest
    pytest.main([__file__, "-v"])
