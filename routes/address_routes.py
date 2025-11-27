from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.address import Address
from models.user import User
from schemas.address_schema import AddressCreate, AddressOut, AddressUpdate

router = APIRouter(prefix="/enderecos", tags=["Endereços"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=AddressOut)
def criar_endereco(dados: AddressCreate, db: Session = Depends(get_db)):
    usuario = db.query(User).filter(User.id == dados.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Garantir 1:1
    if usuario.endereco:
        raise HTTPException(status_code=400, detail="Usuário já possui endereço cadastrado")

    #o usuario tem que digitar apenas o cep, fazer uma integracao com o viacep para compos as informacoes de rua e

    novo = Address(cep=dados.cep, rua=dados.rua, bairro=dados.bairro, usuario_id=dados.usuario_id)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.get("/", response_model=list[AddressOut])
def listar_enderecos(db: Session = Depends(get_db)):
    return db.query(Address).all()


@router.get("/{endereco_id}", response_model=AddressOut)
def obter_endereco(endereco_id: int, db: Session = Depends(get_db)):
    end = db.query(Address).filter(Address.id == endereco_id).first()
    if not end:
        raise HTTPException(status_code=404, detail="Endereço não encontrado")
    return end


@router.put("/{endereco_id}", response_model=AddressOut)
def atualizar_endereco(endereco_id: int, dados: AddressUpdate, db: Session = Depends(get_db)):
    end = db.query(Address).filter(Address.id == endereco_id).first()
    if not end:
        raise HTTPException(status_code=404, detail="Endereço não encontrado")

    usuario = db.query(User).filter(User.id == dados.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário informado não existe")

    # Se estiver trocando de usuário, checar se o novo usuário já tem endereço
    if usuario.endereco and usuario.endereco.id != endereco_id:
        raise HTTPException(status_code=400, detail="Usuário já possui outro endereço cadastrado")

    end.cep = dados.cep
    end.rua = dados.rua
    end.bairro = dados.bairro
    end.usuario_id = dados.usuario_id

    db.commit()
    db.refresh(end)
    return end


@router.delete("/{endereco_id}")
def deletar_endereco(endereco_id: int, db: Session = Depends(get_db)):
    end = db.query(Address).filter(Address.id == endereco_id).first()
    if not end:
        raise HTTPException(status_code=404, detail="Endereço não encontrado")
    db.delete(end)
    db.commit()
    return {"msg": "Endereço deletado com sucesso"}
