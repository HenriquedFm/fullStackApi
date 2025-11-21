# fullStackApi
API para matéria de Full Stack 

Estrutura das Pastas e Arquivos do Projeto:
│── main.py
│── database.py
├── models/
│   ├── user.py
│   └── address.py
├── schemas/
│   ├── user_schema.py
│   └── address_schema.py
├── routes/
│   ├── user_routes.py
│   └── address_routes.py
└── cli.py

Passo a Passo para rodar o projeto pelo Terminal do VS CODE:
├── Rodar a API:
│   └── python -m uvicorn main:app --reload
└── Rodar menu/CLI (VS Code terminal):
    └── python cli.py

Para ver as alterações no "database.db": 
└── Instalar e extensão "DB Viewer" ou semelhante no VS CODE