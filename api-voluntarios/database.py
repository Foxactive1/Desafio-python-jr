"""
Fake Database - Simulação de banco de dados em memória para Voluntários
"""
from datetime import date
from typing import Dict, List

from models import VolunteerInDB, Disponibilidade, StatusVoluntario


class FakeDatabase:
    """Banco de dados fake em memória para voluntários"""
    
    def __init__(self):
        self._volunteers: Dict[int, VolunteerInDB] = {}
        self._next_id = 1
        self._initialize_data()
    
    def _initialize_data(self):
        """Inicializa com dados de exemplo"""
        initial_data = [
            {
                "id": self._get_next_id(),
                "nome": "João Silva",
                "email": "joao@email.com",
                "telefone": "(11) 99999-9999",
                "cargo_pretendido": "Instrutor",
                "disponibilidade": Disponibilidade.MANHA,
                "status": StatusVoluntario.ATIVO,
                "data_inscricao": date(2023, 1, 15),
                "is_deleted": False
            },
            {
                "id": self._get_next_id(),
                "nome": "Maria Santos",
                "email": "maria@email.com",
                "telefone": "(11) 98888-8888",
                "cargo_pretendido": "Organizador",
                "disponibilidade": Disponibilidade.TARDE,
                "status": StatusVoluntario.ATIVO,
                "data_inscricao": date(2023, 2, 20),
                "is_deleted": False
            },
            {
                "id": self._get_next_id(),
                "nome": "Carlos Oliveira",
                "email": "carlos@email.com",
                "telefone": "(11) 97777-7777",
                "cargo_pretendido": "Suporte",
                "disponibilidade": Disponibilidade.NOITE,
                "status": StatusVoluntario.INATIVO,
                "data_inscricao": date(2023, 3, 10),
                "is_deleted": False
            },
            {
                "id": self._get_next_id(),
                "nome": "Ana Costa",
                "email": "ana@email.com",
                "telefone": "(11) 96666-6666",
                "cargo_pretendido": "Instrutor",
                "disponibilidade": Disponibilidade.FIM_SEMANA,
                "status": StatusVoluntario.PENDENTE,
                "data_inscricao": date(2023, 4, 5),
                "is_deleted": False
            },
            {
                "id": self._get_next_id(),
                "nome": "Pedro Rocha",
                "email": "pedro@email.com",
                "telefone": "(11) 95555-5555",
                "cargo_pretendido": "Coordenador",
                "disponibilidade": Disponibilidade.FLEXIVEL,
                "status": StatusVoluntario.ATIVO,
                "data_inscricao": date(2023, 5, 12),
                "is_deleted": True  # Voluntário excluído
            }
        ]
        
        for data in initial_data:
            volunteer = VolunteerInDB(**data)
            self._volunteers[volunteer.id] = volunteer
    
    def _get_next_id(self) -> int:
        """Obtém o próximo ID disponível"""
        current_id = self._next_id
        self._next_id += 1
        return current_id
    
    def get_all_volunteers(self) -> List[VolunteerInDB]:
        """Retorna todos os voluntários"""
        return list(self._volunteers.values())
    
    def get_volunteer(self, volunteer_id: int) -> VolunteerInDB:
        """Obtém um voluntário pelo ID"""
        return self._volunteers.get(volunteer_id)
    
    def add_volunteer(self, volunteer: VolunteerInDB) -> VolunteerInDB:
        """Adiciona um novo voluntário"""
        volunteer.id = self._get_next_id()
        self._volunteers[volunteer.id] = volunteer
        return volunteer
    
    def update_volunteer(self, volunteer_id: int, **kwargs) -> VolunteerInDB:
        """Atualiza um voluntário"""
        if volunteer_id not in self._volunteers:
            return None
        
        volunteer = self._volunteers[volunteer_id]
        for key, value in kwargs.items():
            if hasattr(volunteer, key) and value is not None:
                setattr(volunteer, key, value)
        
        return volunteer
    
    def delete_volunteer(self, volunteer_id: int) -> bool:
        """Marca um voluntário como excluído"""
        if volunteer_id not in self._volunteers:
            return False
        
        volunteer = self._volunteers[volunteer_id]
        volunteer.is_deleted = True
        return True
    
    def restore_volunteer(self, volunteer_id: int) -> VolunteerInDB:
        """Restaura um voluntário excluído"""
        if volunteer_id not in self._volunteers:
            return None
        
        volunteer = self._volunteers[volunteer_id]
        volunteer.is_deleted = False
        return volunteer
    
    def email_exists(self, email: str, exclude_id: int = None) -> bool:
        """Verifica se um email já existe no banco de dados"""
        for volunteer in self._volunteers.values():
            if volunteer.email == email and not volunteer.is_deleted:
                if exclude_id is None or volunteer.id != exclude_id:
                    return True
        return False


# Instância global do banco de dados
db = FakeDatabase()