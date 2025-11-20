from pydantic import BaseModel

class AddressBase(BaseModel):
    cep: str
    rua: str
    bairro: str

class AddressCreate(AddressBase):
    usuario_id: int

class AddressUpdate(AddressBase):
    usuario_id: int

class AddressOut(AddressBase):
    id: int
    usuario_id: int

    class Config:
        orm_mode = True
