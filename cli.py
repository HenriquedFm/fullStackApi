import re
import requests
from pydantic import ValidationError
from models.user import User
from models.address import Address
from schemas.user_schema import UserCreate
from schemas.address_schema import AddressCreate
from database import SessionLocal, engine, Base
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)

def limpar_cpf(cpf_str):
    return re.sub(r'\D', '', cpf_str)

def criar_usuario_terminal():
    print("\n--- Novo Cadastro ---")
    
    nome = input("Nome: ").strip()
    if not nome:
        print("Erro: Nome obrigatorio.")
        return

    # --- CPF ---
    cpf_input = input("CPF: ").strip()
    cpf_limpo = limpar_cpf(cpf_input)
    
    if not cpf_limpo:
        print("Erro: CPF obrigatorio.")
        return

    db = SessionLocal()
    usuario_existe = db.query(User).filter(User.cpf == cpf_limpo).first()
    db.close()

    if usuario_existe:
        print(f"ERRO FATAL: O CPF {cpf_limpo} ja existe no banco. Cadastro cancelado.")
        return 

    try:
        UserCreate(nome=nome, cpf=cpf_limpo, email="a@a.com", password="123")
    except ValidationError as e:
        erros = [err['msg'] for err in e.errors() if 'cpf' in str(err['loc'])]
        if erros:
            print(f"Erro no formato do CPF: {erros[0]}")
            return

    email = input("Email: ").strip()
    try:
        UserCreate(nome=nome, cpf=cpf_limpo, email=email, password="123")
    except ValidationError as e:
        print(f"Erro no Email: {e.errors()[0]['msg']}")
        return

    cep = input("CEP: ").strip()
    cep_limpo = cep.replace("-", "").replace(".", "")
    
    if len(cep_limpo) != 8:
        print("Erro no CEP: Tamanho invalido.")
        return
    try:
        req = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5)
        dados = req.json()
        if "erro" in dados:
            print("ERRO FATAL: CEP nao encontrado na base dos Correios.")
            return
    except:
        print("Erro: Falha ao consultar ViaCEP.")
        return

    rua = input("Rua: ").strip()
    if not rua:
        print("Erro: Rua obrigatoria.")
        return

    bairro = input("Bairro: ").strip()
    if not bairro:
        print("Erro: Bairro obrigatorio.")
        return

    db = SessionLocal()
    try:
        novo_user = User(nome=nome, cpf=cpf_limpo, email=email)
        db.add(novo_user)
        db.commit()
        db.refresh(novo_user)

        novo_end = Address(cep=cep, rua=rua, bairro=bairro, usuario_id=novo_user.id)
        db.add(novo_end)
        db.commit()
        print(f"\nSUCESSO! Usuario criado ID: {novo_user.id}")
    except Exception as e:
        print(f"Erro ao salvar: {e}")
    finally:
        db.close()

def listar_usuarios_terminal():
    db = SessionLocal()
    users = db.query(User).all()
    print(f"\n--- Lista ({len(users)}) ---")
    for u in users:
        print(f"ID: {u.id} | Nome: {u.nome} | CPF: {u.cpf} | Endereco: {u.endereco.rua if u.endereco else 'Sem endereco'}")
    db.close()

def buscar_por_id_terminal():
    try:
        id_busca = int(input("ID: "))
    except:
        return
    db = SessionLocal()
    u = db.query(User).filter(User.id == id_busca).first()
    if u:
        print(f"Achou: {u.nome}, CPF: {u.cpf}, Rua: {u.endereco.rua if u.endereco else ''}")
    else:
        print("Nao encontrado.")
    db.close()

def atualizar_usuario_terminal():
    try:
        id_busca = int(input("ID para atualizar: "))
    except:
        return
    
    db = SessionLocal()
    u = db.query(User).filter(User.id == id_busca).first()
    if not u:
        print("Nao encontrado.")
        db.close()
        return
    
    novo_nome = input(f"Nome ({u.nome}): ") or u.nome
    novo_cpf = input(f"CPF ({u.cpf}): ") or u.cpf
    novo_email = input(f"Email ({u.email}): ") or u.email
    
    # Atualiza user
    u.nome = novo_nome
    u.cpf = limpar_cpf(novo_cpf)
    u.email = novo_email
    
    if u.endereco:
        novo_cep = input(f"CEP ({u.endereco.cep}): ") or u.endereco.cep
        
        # Se mudou CEP, valida
        if novo_cep != u.endereco.cep:
            clean_cep = novo_cep.replace("-", "").replace(".", "")
            r = requests.get(f"https://viacep.com.br/ws/{clean_cep}/json/")
            if "erro" in r.json():
                print("Erro: Novo CEP invalido.")
                db.close()
                return
        
        nova_rua = input(f"Rua ({u.endereco.rua}): ") or u.endereco.rua
        novo_bairro = input(f"Bairro ({u.endereco.bairro}): ") or u.endereco.bairro
        
        u.endereco.cep = novo_cep
        u.endereco.rua = nova_rua
        u.endereco.bairro = novo_bairro

    db.commit()
    print("Atualizado.")
    db.close()

def remover_usuario_terminal():
    try:
        id_busca = int(input("ID para remover: "))
    except:
        return
    db = SessionLocal()
    u = db.query(User).filter(User.id == id_busca).first()
    if u:
        if u.endereco:
            db.delete(u.endereco)
        db.delete(u)
        db.commit()
        print("Removido.")
    else:
        print("Nao encontrado.")
    db.close()

def menu():
    while True:
        print("\n1-Criar 2-Listar 3-Buscar 4-Atualizar 5-Remover 6-Sair")
        op = input("Opcao: ")
        if op == '1': criar_usuario_terminal()
        elif op == '2': listar_usuarios_terminal()
        elif op == '3': buscar_por_id_terminal()
        elif op == '4': atualizar_usuario_terminal()
        elif op == '5': remover_usuario_terminal()
        elif op == '6': break

if __name__ == "__main__":
    menu()