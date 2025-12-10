"""
Schemas Pydantic para validação e serialização
"""
from pydantic import BaseModel, validator, Field
from typing import Optional
from datetime import date
from datetime import datetime

from models import CertificateStatus


class CertificateBase(BaseModel):
    """Schema base para certificado"""
    user_id: int = Field(..., gt=0, description="ID do usuário")
    username: str = Field(..., min_length=1, max_length=100, description="Nome do usuário")
    course_id: int = Field(..., gt=0, description="ID do curso")
    course_name: str = Field(..., min_length=1, max_length=200, description="Nome do curso")
    issue_date: date = Field(..., description="Data de emissão")
    expiration_date: date = Field(..., description="Data de expiração")
    status: CertificateStatus = Field(..., description="Status do certificado")
    
    @validator('expiration_date')
    def validate_expiration_date(cls, v, values):
        """Valida se a data de expiração é após a data de emissão"""
        if 'issue_date' in values and v <= values['issue_date']:
            raise ValueError('A data de expiração deve ser posterior à data de emissão')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        """Valida o nome de usuário"""
        if not v.strip():
            raise ValueError('O nome de usuário não pode estar vazio')
        return v.strip()


class CertificateCreate(CertificateBase):
    """Schema para criação de certificado"""
    pass


class CertificateUpdate(BaseModel):
    """Schema para atualização de certificado"""
    user_id: Optional[int] = Field(None, gt=0, description="ID do usuário")
    username: Optional[str] = Field(None, min_length=1, max_length=100, description="Nome do usuário")
    course_id: Optional[int] = Field(None, gt=0, description="ID do curso")
    course_name: Optional[str] = Field(None, min_length=1, max_length=200, description="Nome do curso")
    issue_date: Optional[date] = Field(None, description="Data de emissão")
    expiration_date: Optional[date] = Field(None, description="Data de expiração")
    status: Optional[CertificateStatus] = Field(None, description="Status do certificado")
    
    @validator('expiration_date')
    def validate_expiration_date(cls, v, values):
        """Valida se a data de expiração é após a data de emissão"""
        if v and 'issue_date' in values and values['issue_date']:
            if v <= values['issue_date']:
                raise ValueError('A data de expiração deve ser posterior à data de emissão')
        return v


class Certificate(CertificateBase):
    """Schema para resposta de certificado"""
    id: int
    is_deleted: bool
    
    class Config:
        """Configurações do Pydantic"""
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }