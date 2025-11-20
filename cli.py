import json
from models.user import User
from models.address import Address
from schemas.user_schema import UserCreate
from schemas.address_schema import AddressCreate
from database import SessionLocal, engine, Base
from sqlalchemy.orm import Session

# garante tabelas criadas
Base.metadata.create_all(bind=engine)

def criar_usuario_terminal():
    nome = input("Nome: ")
    cpf = input("CPF: ")
    email = input("Email: ")

    cep = input("CEP: ")
    rua = input("Rua: ")
    bairro = input("Bairro: ")

    db: Session = SessionLocal()
    try:
        if db.query(User).filter(User.cpf == cpf).first():
            print("CPF já cadastrado.")
            return

        novo = User(nome=nome, cpf=cpf, email=email)
        db.add(novo)
        db.commit()
        db.refresh(novo)

        addr = Address(cep=cep, rua=rua, bairro=bairro, usuario_id=novo.id)
        db.add(addr)
        db.commit()
        print(f"Usuário criado (id={novo.id}) com endereço (id={addr.id}).")
    finally:
        db.close()


def listar_usuarios_terminal():
    db = SessionLocal()
    try:
        usuarios = db.query(User).all()
        for u in usuarios:
            print({
                "id": u.id,
                "nome": u.nome,
                "cpf": u.cpf,
                "email": u.email,
                "endereco": None if not u.endereco else {
                    "id": u.endereco.id,
                    "cep": u.endereco.cep,
                    "rua": u.endereco.rua,
                    "bairro": u.endereco.bairro
                }
            })
    finally:
        db.close()


def buscar_por_id_terminal():
    idu = int(input("ID do usuário: "))
    db = SessionLocal()
    try:
        u = db.query(User).filter(User.id == idu).first()
        if not u:
            print("Usuário não encontrado.")
            return
        print({
            "id": u.id,
            "nome": u.nome,
            "cpf": u.cpf,
            "email": u.email,
            "endereco": None if not u.endereco else {
                "id": u.endereco.id,
                "cep": u.endereco.cep,
                "rua": u.endereco.rua,
                "bairro": u.endereco.bairro
            }
        })
    finally:
        db.close()


def atualizar_usuario_terminal():
    idu = int(input("ID para atualizar: "))
    db = SessionLocal()
    try:
        u = db.query(User).filter(User.id == idu).first()
        if not u:
            print("Usuário não encontrado.")
            return

        nome = input(f"Nome [{u.nome}]: ") or u.nome
        cpf = input(f"CPF [{u.cpf}]: ") or u.cpf
        email = input(f"Email [{u.email}]: ") or u.email

        # atualizar usuário
        u.nome = nome
        u.cpf = cpf
        u.email = email
        db.commit()

        # atualizar/mostrar endereço
        if u.endereco:
            print("Atualizando endereço existente.")
            cep = input(f"CEP [{u.endereco.cep}]: ") or u.endereco.cep
            rua = input(f"Rua [{u.endereco.rua}]: ") or u.endereco.rua
            bairro = input(f"Bairro [{u.endereco.bairro}]: ") or u.endereco.bairro

            u.endereco.cep = cep
            u.endereco.rua = rua
            u.endereco.bairro = bairro
            db.commit()
        else:
            escolha = input("Usuário não tem endereço. Criar? (s/n): ")
            if escolha.lower().startswith("s"):
                cep = input("CEP: ")
                rua = input("Rua: ")
                bairro = input("Bairro: ")
                addr = Address(cep=cep, rua=rua, bairro=bairro, usuario_id=u.id)
                db.add(addr)
                db.commit()

        print("Atualizado com sucesso.")
    finally:
        db.close()


def remover_usuario_terminal():
    idu = int(input("ID para remover: "))
    db = SessionLocal()
    try:
        u = db.query(User).filter(User.id == idu).first()
        if not u:
            print("Usuário não encontrado.")
            return
        if u.endereco:
            db.delete(u.endereco)
        db.delete(u)
        db.commit()
        print("Removido.")
    finally:
        db.close()


def menu():
    while True:
        print("\n=== MENU ===")
        print("1 - Criar usuário + endereço")
        print("2 - Listar usuários")
        print("3 - Buscar por ID")
        print("4 - Atualizar usuário")
        print("5 - Remover usuário")
        print("6 - Sair")
        op = input("Escolha: ")
        if op == "1":
            criar_usuario_terminal()
        elif op == "2":
            listar_usuarios_terminal()
        elif op == "3":
            buscar_por_id_terminal()
        elif op == "4":
            atualizar_usuario_terminal()
        elif op == "5":
            remover_usuario_terminal()
        elif op == "6":
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    menu()
