"""
Fake Database - Simulação de banco de dados em memória
"""
from datetime import date, datetime
from typing import Dict, List

from models import Certificate, CertificateStatus


class FakeDatabase:
    """Banco de dados fake em memória"""
    
    def __init__(self):
        self._certificates: Dict[int, Certificate] = {}
        self._next_id = 1
        self._initialize_data()
    
    def _initialize_data(self):
        """Inicializa com dados de exemplo"""
        initial_data = [
            {
                "id": self._get_next_id(),
                "user_id": 1,
                "username": "john_doe",
                "course_id": 101,
                "course_name": "Python Fundamentals",
                "issue_date": date(2023, 1, 15),
                "expiration_date": date(2024, 1, 15),
                "status": CertificateStatus.ACTIVE,
                "is_deleted": False
            },
            {
                "id": self._get_next_id(),
                "user_id": 2,
                "username": "jane_smith",
                "course_id": 102,
                "course_name": "Advanced Python",
                "issue_date": date(2023, 2, 20),
                "expiration_date": date(2024, 2, 20),
                "status": CertificateStatus.EXPIRED,
                "is_deleted": False
            },
            {
                "id": self._get_next_id(),
                "user_id": 3,
                "username": "bob_johnson",
                "course_id": 103,
                "course_name": "Data Science",
                "issue_date": date(2023, 3, 10),
                "expiration_date": date(2024, 3, 10),
                "status": CertificateStatus.REVOKED,
                "is_deleted": True  # Certificado excluído
            },
            {
                "id": self._get_next_id(),
                "user_id": 1,
                "username": "john_doe",
                "course_id": 104,
                "course_name": "Web Development",
                "issue_date": date(2023, 4, 5),
                "expiration_date": date(2024, 4, 5),
                "status": CertificateStatus.ACTIVE,
                "is_deleted": False
            },
            {
                "id": self._get_next_id(),
                "user_id": 4,
                "username": "alice_brown",
                "course_id": 105,
                "course_name": "Machine Learning",
                "issue_date": date(2023, 5, 12),
                "expiration_date": date(2024, 5, 12),
                "status": CertificateStatus.ACTIVE,
                "is_deleted": False
            }
        ]
        
        for data in initial_data:
            certificate = Certificate(**data)
            self._certificates[certificate.id] = certificate
    
    def _get_next_id(self) -> int:
        """Obtém o próximo ID disponível"""
        current_id = self._next_id
        self._next_id += 1
        return current_id
    
    def get_all_certificates(self) -> List[Certificate]:
        """Retorna todos os certificados"""
        return list(self._certificates.values())
    
    def get_certificate(self, certificate_id: int) -> Certificate:
        """Obtém um certificado pelo ID"""
        return self._certificates.get(certificate_id)
    
    def add_certificate(self, certificate: Certificate) -> Certificate:
        """Adiciona um novo certificado"""
        certificate.id = self._get_next_id()
        self._certificates[certificate.id] = certificate
        return certificate
    
    def update_certificate(self, certificate_id: int, **kwargs) -> Certificate:
        """Atualiza um certificado"""
        if certificate_id not in self._certificates:
            return None
        
        certificate = self._certificates[certificate_id]
        for key, value in kwargs.items():
            if hasattr(certificate, key) and value is not None:
                setattr(certificate, key, value)
        
        return certificate
    
    def delete_certificate(self, certificate_id: int) -> bool:
        """Marca um certificado como excluído"""
        if certificate_id not in self._certificates:
            return False
        
        certificate = self._certificates[certificate_id]
        certificate.is_deleted = True
        return True
    
    def restore_certificate(self, certificate_id: int) -> Certificate:
        """Restaura um certificado excluído"""
        if certificate_id not in self._certificates:
            return None
        
        certificate = self._certificates[certificate_id]
        certificate.is_deleted = False
        return certificate


# Instância global do banco de dados
db = FakeDatabase()