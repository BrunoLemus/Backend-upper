
from app.db import database
from app.api.routes import caja as caja  # para registrar tablas
from app.api.routes import tarima
from app.api.routes import user_practicante
from app.api.routes import user_coordinador
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.api.routes import caja
from app.api.routes import registro
from app.api.routes import impresion

from app.api.routes import login


#RUTAS DE LOS ENDPOINTS DE MEXICO
from app.api.routes import registro_mx
from app.api.routes import tarima_mx
from app.api.routes import user_practicante_mx
from app.api.routes import user_coordinador_mx
from app.api.routes import caja_mx

import win32print
import win32ui

app = FastAPI(title="API de Etiquetas - Cajas")

origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080"
]

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear tablas (ejecuta esto al inicio, solo para desarrollo)
database.Base.metadata.create_all(bind=database.engine)

# Routers
app.include_router(caja.router, prefix="/cajas", tags=["Cajas GDL"])
app.include_router(tarima.router, prefix="/tarimas", tags=["Tarimas GDL"])
app.include_router(user_practicante.router, prefix="/user_practicantes", tags=["Usuarios Practicantes GDL"])
app.include_router(user_coordinador.router, prefix="/user_coordinadors", tags=["Usuarios Coordinadores GDL"])
app.include_router(registro.router, prefix="/historial", tags=["Registros GDL"])

app.include_router(registro_mx.router, prefix="/registros_mx", tags=["Registros Mexico"])
app.include_router(tarima_mx.router, prefix="/tarimas_mx", tags=["Tarimas Mexico"])
app.include_router(user_practicante_mx.router, prefix="/user_practicantes_mx", tags=["Usuarios Practicantes Mexico"])
app.include_router(user_coordinador_mx.router, prefix="/user_coordinadors_mx", tags=["Usuarios Coordinadores Mexico"])
app.include_router(caja_mx.router, prefix="/cajas_mx", tags=["Cajas Mexico"])
app.include_router(impresion.router, prefix="/imprimir", tags=["Imprimir por USB"])


#login
app.include_router(login.router, tags=["Login"])


# ========= Servidor de impresión integrado =========
class PrintPayload(BaseModel):
    content: str
    use_zpl: bool = False  # Si es True, envía ZPL directo a Zebra


# ========= Root =========
@app.get("/")
def root():
    return {"message": "API lista. Revisa /docs para interactuar."}
