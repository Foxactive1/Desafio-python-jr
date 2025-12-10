"""
Schemas Pydantic para validação e serialização de Voluntários
"""
from pydantic import BaseModel, validator, Field
from typing import Optional
from datetime import date

from models import Disponibilidade, StatusVoluntario


class VolunteerBase(BaseModel):
    """Schema base para voluntário"""
    nome: str = Field(..., min_length=1, max_length=100, description="Nome do voluntário")
    email: str = Field(..., min_length=3, max_length=100, description="Email do voluntário")
    telefone: str = Field(..., min_length=10, max_length=20, description="Telefone do voluntário")
    cargo_pretendido: str = Field(..., min_length=1, max_length=100, description="Cargo pretendido")
    disponibilidade: Disponibilidade = Field(..., description="Disponibilidade do voluntário")
    status: StatusVoluntario = Field(default=StatusVoluntario.PENDENTE, description="Status do voluntário")
    
    @validator('email')
    def validate_email(cls, v):
        """Valida o formato do email"""
        if '@' not in v:
            raise ValueError('Email inválido')
        return v.strip().lower()
    
    @validator('nome')
    def validate_nome(cls, v):
        """Valida o nome"""
        if not v.strip():
            raise ValueError('O nome não pode estar vazio')
        return v.strip()


class VolunteerCreate(VolunteerBase):
    """Schema para criação de voluntário"""
    pass


class VolunteerUpdate(BaseModel):
    """Schema para atualização de voluntário"""
    nome: Optional[str] = Field(None, min_length=1, max_length=100, description="Nome do voluntário")
    email: Optional[str] = Field(None, min_length=3, max_length=100, description="Email do voluntário")
    telefone: Optional[str] = Field(None, min_length=10, max_length=20, description="Telefone do voluntário")
    cargo_pretendido: Optional[str] = Field(None, min_length=1, max_length=100, description="Cargo pretendido")
    disponibilidade: Optional[Disponibilidade] = Field(None, description="Disponibilidade do voluntário")
    status: Optional[StatusVoluntario] = Field(None, description="Status do voluntário")
    
    @validator('email')
    def validate_email(cls, v):
        """Valida o formato do email"""
        if v is not None:
            if '@' not in v:
                raise ValueError('Email inválido')
            return v.strip().lower()
        return v


class Volunteer(VolunteerBase):
    """Schema para resposta de voluntário"""
    id: int
    data_inscricao: date
    is_deleted: bool
    
    class Config:
        """Configurações do Pydantic"""
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat(),
        }