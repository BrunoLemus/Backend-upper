from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.caja_mx import CajaMXCreate, CajaMXRead
from typing import Optional, List
from app.services import caja_mx_service
from app.db.database import get_db
from app.core.security import get_current_user  

router = APIRouter()

# ✅ Crear caja MX
@router.post("/", response_model=CajaMXRead)
def create_caja_mx_endpoint(
    payload: CajaMXCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  
):
    return caja_mx_service.create_caja_mx(db, payload, current_user)


# ✅ Listar cajas MX con filtros opcionales
@router.get("/", response_model=List[CajaMXRead])
def list_cajas_mx(
    skip: int = 0,
    limit: int = 100,
    paqueteria: Optional[str] = None,
    n_facturas: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return caja_mx_service.get_cajas_mx(
        db, skip=skip, limit=limit, paqueteria=paqueteria,
        n_facturas=n_facturas, current_user=current_user
    )


# ✅ Obtener caja MX por ID
@router.get("/{caja_id}", response_model=CajaMXRead)
def get_caja_mx(caja_id: int, db: Session = Depends(get_db)):
    db_caja = caja_mx_service.get_caja_mx_by_id(db, caja_id)
    if not db_caja:
        raise HTTPException(status_code=404, detail="Caja MX no encontrada")
    return db_caja


# ✅ Actualizar caja MX
@router.put("/{caja_id}", response_model=CajaMXRead)
def update_caja_mx(caja_id: int, payload: CajaMXCreate, db: Session = Depends(get_db)):
    db_caja = caja_mx_service.update_caja_mx(db, caja_id, payload.dict())
    if not db_caja:
        raise HTTPException(status_code=404, detail="Caja MX no encontrada")
    return db_caja


# ✅ Eliminar caja MX
@router.delete("/{caja_id}")
def delete_caja_mx(caja_id: int, db: Session = Depends(get_db)):
    deleted = caja_mx_service.delete_caja_mx(db, caja_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Caja MX no encontrada")
    return {"detail": "Caja MX eliminada correctamente"}
