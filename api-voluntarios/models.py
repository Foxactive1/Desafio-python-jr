"""
Modelos de dados e Enums
"""
from enum import Enum
from datetime import date


class CertificateStatus(str, Enum):
    """Enum para status do certificado"""
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class Certificate:
    """Modelo de certificado"""
    
    def __init__(
        self,
        id: int,
        user_id: int,
        username: str,
        course_id: int,
        course_name: str,
        issue_date: date,
        expiration_date: date,
        status: CertificateStatus,
        is_deleted: bool = False
    ):
        self.id = id
        self.user_id = user_id
        self.username = username
        self.course_id = course_id
        self.course_name = course_name
        self.issue_date = issue_date
        self.expiration_date = expiration_date
        self.status = status
        self.is_deleted = is_deleted
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "course_id": self.course_id,
            "course_name": self.course_name,
            "issue_date": self.issue_date,
            "expiration_date": self.expiration_date,
            "status": self.status,
            "is_deleted": self.is_deleted
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Cria a partir de dicionário"""
        return cls(**data)