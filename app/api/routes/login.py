from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.db.database import get_db
from app.db.models.user_coordinador_mx import UserCoordinadorMX
from app.db.models.user_practicante_mx import UserPracticanteMX
from app.db.models.user_coordinador import UserCoordinador
from app.db.models.user_practicante import UserPracticante
from app.core.security import create_access_token, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES
import logging

router = APIRouter()

# --------------------------------
# CONFIGURACIÓN
# --------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("login")


# --------------------------------
# LOGIN DINÁMICO
# --------------------------------
@router.post("/login/{sede}/{tipo}/")
def login(
    sede: str,
    tipo: str,
    nombre: str = Form(...),
    contrasena: str = Form(...),
    
    db: Session = Depends(get_db)
):
    sede = sede.lower()
    tipo = tipo.lower()

    logger.info(f"🔹 Intento de login → sede={sede}, tipo={tipo}, usuario={nombre}")

    # Determinar modelo según sede y tipo
    if sede == "mexico":
        model = UserCoordinadorMX if tipo == "coordinador" else UserPracticanteMX
    elif sede == "guadalajara":
        model = UserCoordinador if tipo == "coordinador" else UserPracticante
    else:
        raise HTTPException(status_code=400, detail="Sede inválida")

    # Buscar usuario
    user = db.query(model).filter(model.nombre == nombre).first()
    if not user:
        logger.warning(f"❌ Usuario no encontrado: {nombre}")
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    if not verify_password(contrasena, user.contrasena):
        logger.warning(f"❌ Contraseña incorrecta para: {nombre}")
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    # Crear token con datos completos
    token_data = {
        "id": user.id,
        "nombre": user.nombre,
        "tipo": tipo,
        "sede": sede
    }

    token = create_access_token(token_data)

    logger.info(f"✅ Login exitoso: {user.nombre} ({tipo} - {sede})")

    return {
        "nombre": user.nombre,
        "token": token,
        "sede": sede,
        "tipo": tipo,
        "expira_en_minutos": ACCESS_TOKEN_EXPIRE_MINUTES
    }
