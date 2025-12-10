"""
Modelos de dados e Enums para Voluntários
"""
from enum import Enum
from datetime import date


class Disponibilidade(str, Enum):
    """Enum para disponibilidade do voluntário"""
    MANHA = "manha"
    TARDE = "tarde"
    NOITE = "noite"
    FIM_SEMANA = "fim_de_semana"
    FLEXIVEL = "flexivel"


class StatusVoluntario(str, Enum):
    """Enum para status do voluntário"""
    ATIVO = "ativo"
    INATIVO = "inativo"
    PENDENTE = "pendente"


class Volunteer:
    """Modelo de voluntário"""
    
    def __init__(
        self,
        id: int,
        nome: str,
        email: str,
        telefone: str,
        cargo_pretendido: str,
        disponibilidade: Disponibilidade,
        status: StatusVoluntario,
        data_inscricao: date,
        is_deleted: bool = False
    ):
        self.id = id
        self.nome = nome
        self.email = email
        self.telefone = telefone
        self.cargo_pretendido = cargo_pretendido
        self.disponibilidade = disponibilidade
        self.status = status
        self.data_inscricao = data_inscricao
        self.is_deleted = is_deleted
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "telefone": self.telefone,
            "cargo_pretendido": self.cargo_pretendido,
            "disponibilidade": self.disponibilidade,
            "status": self.status,
            "data_inscricao": self.data_inscricao,
            "is_deleted": self.is_deleted
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Cria a partir de dicionário"""
        return cls(**data)