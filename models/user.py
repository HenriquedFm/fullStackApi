from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    cpf = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)

    # 1 usuário -> 1 endereço (uselist=False) — mantemos unique no FK do Address
    endereco = relationship("Address", back_populates="usuario", uselist=False)
