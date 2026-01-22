"""
Dependências da aplicação
"""
import database


def get_db() -> database.FakeDatabase:
    """Dependency para obter instância do banco de dados"""
    return database.db 