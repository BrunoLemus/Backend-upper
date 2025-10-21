from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta
import logging
from passlib.context import CryptContext
from app.db.database import get_db
from app.db.models.user_coordinador_mx import UserCoordinadorMX
from app.db.models.user_practicante_mx import UserPracticanteMX
from app.db.models.user_coordinador import UserCoordinador
from app.db.models.user_practicante import UserPracticante

# --------------------------------
# CONFIGURACIÓN
# --------------------------------
SECRET_KEY = "SUPER_SECRET_KEY_GLOBAL"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 720  # 12 horas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("security")


# --------------------------------
# FUNCIONES AUXILIARES
# --------------------------------
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: int = None):
    """Crea un token JWT con todos los datos necesarios."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta or ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    logger.info(f"🟢 Token generado para {data.get('nombre')} ({data.get('tipo')} - {data.get('sede')})")
    return token


# --------------------------------
# VALIDACIÓN DEL TOKEN
# --------------------------------
def get_current_user(sede: str, role: str, token: str = Header(...), db: Session = Depends(get_db)):
    """Valida el token JWT y devuelve el usuario autenticado."""

    if not token:
        raise HTTPException(status_code=401, detail="Token requerido")

    try:
        # 🔍 Intentamos decodificar el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        logger.error("❌ El token ha expirado")
        raise HTTPException(status_code=401, detail="Token expirado")
    except JWTError as e:
        logger.error(f"❌ Error al decodificar token: {e}")
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    # Extraer los datos
    user_id = payload.get("id")
    nombre = payload.get("nombre")
    token_role = payload.get("tipo")
    token_sede = payload.get("sede")

    logger.info(f"📦 Token decodificado correctamente → id={user_id}, nombre={nombre}, rol={token_role}, sede={token_sede}")

    # Validar datos dentro del token
    if not user_id or not token_role or not token_sede:
        raise HTTPException(status_code=401, detail="Token incompleto o corrupto")

    # ⚠️ Convertimos todo a minúsculas para evitar errores de comparación
    if token_role.lower() != role.lower() or token_sede.lower() != sede.lower():
        raise HTTPException(status_code=401, detail=f"Token no autorizado para esta sede o rol")

    # Seleccionar modelo según la sede y tipo de usuario
    if token_sede.lower() == "mexico":
        model = UserCoordinadorMX if token_role.lower() == "coordinador" else UserPracticanteMX
    elif token_sede.lower() == "guadalajara":
        model = UserCoordinador if token_role.lower() == "coordinador" else UserPracticante
    else:
        raise HTTPException(status_code=400, detail="Sede inválida")

    # Buscar el usuario en la base de datos
    user = db.query(model).filter(model.id == user_id).first()
    if not user:
        logger.warning(f"⚠ Usuario con id={user_id} no encontrado en {token_sede}")
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    logger.info(f"🟩 Usuario autenticado correctamente: {user.nombre} ({token_role} - {token_sede})")
    return user
