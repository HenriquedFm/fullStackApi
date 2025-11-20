from pydantic import BaseModel
from typing import Optional
from .address_schema import AddressOut

class UserBase(BaseModel):
    nome: str
    cpf: str
    email: str

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    pass

class UserOut(UserBase):
    id: int
    endereco: Optional[AddressOut] = None

    class Config:
        orm_mode = True
