from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.schemas.tarima_mx import TarimaMXCreate, TarimaMXRead
from app.services.tarima_mx_service import (
    create_tarima_mx, 
    get_tarimas_mx, 
    get_tarima_mx_by_id, 
    update_tarima_mx, 
    delete_tarima_mx
)
from app.core.security import get_current_user  

router = APIRouter()

# ✅ Crear tarima MX
@router.post("/", response_model=TarimaMXRead)
def create_tarima_mx_endpoint(
    payload: TarimaMXCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return create_tarima_mx(db, payload, current_user)

# ✅ Listar tarimas MX con filtros opcionales
@router.get("/", response_model=List[TarimaMXRead])
def list_tarimas_mx(
    skip: int = 0,
    limit: int = 100,
    paqueteria: Optional[str] = None,
    numero_facturas: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return get_tarimas_mx(
        db, skip=skip, limit=limit, paqueteria=paqueteria,
        numero_facturas=numero_facturas, current_user=current_user
    )

# ✅ Obtener tarima MX por ID
@router.get("/{tarima_id}", response_model=TarimaMXRead)
def get_tarima_mx(tarima_id: int, db: Session = Depends(get_db)):
    db_tarima = get_tarima_mx_by_id(db, tarima_id)
    if not db_tarima:
        raise HTTPException(status_code=404, detail="Tarima MX no encontrada")
    return db_tarima

# ✅ Actualizar tarima MX
@router.put("/{tarima_id}", response_model=TarimaMXRead)
def update_tarima_mx_endpoint(tarima_id: int, payload: TarimaMXCreate, db: Session = Depends(get_db)):
    db_tarima = update_tarima_mx(db, tarima_id, payload.dict())
    if not db_tarima:
        raise HTTPException(status_code=404, detail="Tarima MX no encontrada")
    return db_tarima

# ✅ Eliminar tarima MX
@router.delete("/{tarima_id}")
def delete_tarima_mx(tarima_id: int, db: Session = Depends(get_db)):
    deleted = delete_tarima_mx(db, tarima_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Tarima MX no encontrada")
    return {"detail": "Tarima MX eliminada exitosamente"}
