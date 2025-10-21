# app/routers/tarima_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.tarima import TarimaCreate, TarimaRead
from app.services.tarima_services import create_tarima, get_tarimas, get_tarima_by_id
from app.core.security import get_current_user  
from typing import Optional, List
from app.services import tarima_services


router = APIRouter()

# ✅ Crear tarima
@router.post("/", response_model=TarimaRead)
def create_tarima_endpoint(
    payload: TarimaCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # <-- current_user ya es un objeto
):
    return create_tarima(db, payload, current_user)

# ✅ Listar tarimas con filtros opcionales
@router.get("/", response_model=List[TarimaRead])
def list_tarimas(
    skip: int = 0,
    limit: int = 100,
    paqueteria: Optional[str] = None,
    numero_facturas: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # <-- current_user ya es un objeto
):
    return get_tarimas(
        db, skip=skip, limit=limit, paqueteria=paqueteria,
        numero_facturas=numero_facturas, current_user=current_user
    )

# ✅ Obtener tarima por ID
@router.get("/{tarima_id}", response_model=TarimaRead)
def get_tarima(tarima_id: int, db: Session = Depends(get_db)):
    db_tarima = get_tarima_by_id(db, tarima_id)
    if not db_tarima:
        raise HTTPException(status_code=404, detail="Tarima no encontrada")
    return db_tarima


# ✅ Actualizar tarima
@router.put("/{tarima_id}", response_model=TarimaRead)
def update_tarima_endpoint(tarima_id: int, payload: TarimaCreate, db: Session = Depends(get_db)):
    db_tarima = tarima_services.update_tarima(db, tarima_id, payload.dict())
    if not db_tarima:
        raise HTTPException(status_code=404, detail="Tarima no encontrada")
    return db_tarima

# ✅ Eliminar tarima
@router.delete("/{tarima_id}")
def delete_tarima(tarima_id: int, db: Session = Depends(get_db)):
    deleted = tarima_services.delete_tarima(db, tarima_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Tarima no encontrada")
    return {"detail": "Tarima eliminada exitosamente"}