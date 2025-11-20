from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.user import User
from models.address import Address
from schemas.user_schema import UserCreate, UserOut, UserUpdate
from schemas.address_schema import AddressCreate

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# POST - criar usuário apenas (sem endereço)
@router.post("/", response_model=UserOut)
def criar_usuario(usuario: UserCreate, db: Session = Depends(get_db)):
    # valida CPF único
    if db.query(User).filter(User.cpf == usuario.cpf).first():
        raise HTTPException(status_code=400, detail="CPF já cadastrado")
    if db.query(User).filter(User.email == usuario.email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    novo = User(nome=usuario.nome, cpf=usuario.cpf, email=usuario.email)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


# POST - criar usuário + endereço juntos
@router.post("/completo", response_model=UserOut)
def criar_usuario_com_endereco(dados: UserCreate, db: Session = Depends(get_db)):
    # dados pode conter um campo 'endereco' se for um modelo composto — caso queremos usar o AddressCreate pattern,
    # aqui vamos assumir que payload tem "endereco" (cep, rua, bairro). Se não, esse endpoint pode ser usado para criar apenas usuário.
    # Para entregar exatamente o que conversamos: aceitar payload com 'endereco' chave.
    payload = dados.dict()
    endereco_data = payload.pop("endereco", None)

    # criar usuário
    if db.query(User).filter(User.cpf == dados.cpf).first():
        raise HTTPException(status_code=400, detail="CPF já cadastrado")
    novo = User(nome=dados.nome, cpf=dados.cpf, email=dados.email)
    db.add(novo)
    db.commit()
    db.refresh(novo)

    # criar endereço se fornecido
    if endereco_data:
        # garantir que usuário ainda não possui endereço (uselist=False garante 1:1)
        if novo.endereco:
            raise HTTPException(status_code=400, detail="Usuário já possui endereço")
        addr = Address(
            cep=endereco_data["cep"],
            rua=endereco_data["rua"],
            bairro=endereco_data["bairro"],
            usuario_id=novo.id
        )
        db.add(addr)
        db.commit()
        db.refresh(novo)  # para popular relação
    return novo


# GET - listar todos
@router.get("/", response_model=list[UserOut])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(User).all()


# GET - obter por id (com endereço)
@router.get("/{usuario_id}", response_model=UserOut)
def obter_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(User).filter(User.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


# PUT - atualizar usuário (sem alterar endereço aqui, endpoint separado)
@router.put("/{usuario_id}", response_model=UserOut)
def atualizar_usuario(usuario_id: int, dados: UserUpdate, db: Session = Depends(get_db)):
    usuario = db.query(User).filter(User.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # checar uniqueness de cpf/email (se alterar)
    if dados.cpf != usuario.cpf and db.query(User).filter(User.cpf == dados.cpf).first():
        raise HTTPException(status_code=400, detail="CPF já cadastrado")
    if dados.email != usuario.email and db.query(User).filter(User.email == dados.email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    usuario.nome = dados.nome
    usuario.cpf = dados.cpf
    usuario.email = dados.email

    db.commit()
    db.refresh(usuario)
    return usuario


# DELETE - excluir usuário + endereço (se existir)
@router.delete("/{usuario_id}")
def deletar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(User).filter(User.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # cascade manual: deletar endereço associado (se houver)
    if usuario.endereco:
        db.delete(usuario.endereco)
    db.delete(usuario)
    db.commit()
    return {"msg": "Usuário deletado com sucesso"}
