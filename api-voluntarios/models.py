"""
Modelos de dados e Enums para Voluntários com suporte a Pydantic V2
"""
from enum import Enum
from datetime import date
from typing import Dict, Any
from pydantic import BaseModel, ConfigDict, Field


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


class VolunteerBaseModel(BaseModel):
    """Modelo base Pydantic para voluntário"""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    
    nome: str
    email: str
    telefone: str
    cargo_pretendido: str
    disponibilidade: Disponibilidade
    status: StatusVoluntario = StatusVoluntario.PENDENTE
    data_inscricao: date = Field(default_factory=date.today)
    is_deleted: bool = False


class VolunteerModel(VolunteerBaseModel):
    """Modelo completo de voluntário com ID"""
    id: int


class VolunteerInDB:
    """Classe de domínio para armazenamento no banco de dados"""
    
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário com serialização apropriada"""
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "telefone": self.telefone,
            "cargo_pretendido": self.cargo_pretendido,
            "disponibilidade": self.disponibilidade.value,
            "status": self.status.value,
            "data_inscricao": self.data_inscricao.isoformat(),
            "is_deleted": self.is_deleted
        }
    
    def to_model(self) -> VolunteerModel:
        """Converte para Pydantic model"""
        return VolunteerModel(
            id=self.id,
            nome=self.nome,
            email=self.email,
            telefone=self.telefone,
            cargo_pretendido=self.cargo_pretendido,
            disponibilidade=self.disponibilidade,
            status=self.status,
            data_inscricao=self.data_inscricao,
            is_deleted=self.is_deleted
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VolunteerInDB':
        """Cria a partir de dicionário"""
        # Converte strings de volta para Enums se necessário
        if isinstance(data.get('disponibilidade'), str):
            data['disponibilidade'] = Disponibilidade(data['disponibilidade'])
        if isinstance(data.get('status'), str):
            data['status'] = StatusVoluntario(data['status'])
        
        # Converte string ISO para date se necessário
        if isinstance(data.get('data_inscricao'), str):
            data['data_inscricao'] = date.fromisoformat(data['data_inscricao'])
        
        return cls(**data)
    
    @classmethod
    def from_model(cls, model: VolunteerModel) -> 'VolunteerInDB':
        """Cria a partir de Pydantic model"""
        return cls(
            id=model.id,
            nome=model.nome,
            email=model.email,
            telefone=model.telefone,
            cargo_pretendido=model.cargo_pretendido,
            disponibilidade=model.disponibilidade,
            status=model.status,
            data_inscricao=model.data_inscricao,
            is_deleted=model.is_deleted
        )


# Alias para manter compatibilidade com código existente
Volunteer = VolunteerInDB