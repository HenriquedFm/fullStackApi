from fastapi import FastAPI
from database import Base, engine
from routes.user_routes import router as user_router
from routes.address_routes import router as address_router

app = FastAPI(title="API Usuários + Endereços (atualizada)")

Base.metadata.create_all(bind=engine)

app.include_router(user_router)
app.include_router(address_router)


@app.get("/")
def root():
    return {"mensagem": "API rodando. Use /docs para testar."}
