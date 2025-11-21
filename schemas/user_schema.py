from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional
from validate_docbr import CPF
import re
from schemas.address_schema import AddressOut

class UserBase(BaseModel):
    nome: str
    email: EmailStr
    cpf: str

class UserCreate(UserBase):
    password: str

    @field_validator('cpf')
    def validar_cpf(cls, v):
        clean = re.sub(r'\D', '', v)
        if len(clean) != 11:
            raise ValueError('CPF deve ter 11 digitos')
        
        validator = CPF()
        if not validator.validate(clean):
            raise ValueError('CPF invalido')
        
        return clean

class UserUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserOut(UserBase):
    id: int
    endereco: Optional[AddressOut] = None
    model_config = ConfigDict(from_attributes=True)