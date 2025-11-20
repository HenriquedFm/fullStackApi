from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Address(Base):
    __tablename__ = "enderecos"

    id = Column(Integer, primary_key=True, index=True)
    cep = Column(String, nullable=False)
    rua = Column(String, nullable=False)
    bairro = Column(String, nullable=False)

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True)
    usuario = relationship("User", back_populates="endereco")
