from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
import requests

class AddressBase(BaseModel):
    cep: str
    rua: str
    bairro: str

class AddressCreate(AddressBase):
    usuario_id: int

    @field_validator('cep')
    def validar_cep(cls, v):
        cep_limpo = v.replace("-", "").replace(".", "")
        if len(cep_limpo) != 8:
            raise ValueError('CEP deve ter 8 digitos')
        return cep_limpo

# --- ESSA ERA A CLASSE QUE FALTAVA ---
class AddressUpdate(BaseModel):
    cep: Optional[str] = None
    rua: Optional[str] = None
    bairro: Optional[str] = None

class AddressOut(AddressBase):
    id: int
    usuario_id: int
    model_config = ConfigDict(from_attributes=True)