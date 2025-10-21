from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.db.database import get_db
from app.db.models.caja_mx import CajaMX
from app.db.models.tarima_mx import TarimaMX
from app.db.models.enums import PaqueteriaEnum, TipoEmbalajeEnum
from pydantic import BaseModel

router = APIRouter()

# ------------------------------------------------------------------
# ✅ GET: Obtener todos los registros (Cajas y Tarimas)
# ------------------------------------------------------------------
@router.get("/")
def obtener_registros(db: Session = Depends(get_db)):
    registros = []

    # 🔹 Obtener cajas
    cajas = db.query(CajaMX).all()
    for c in cajas:
        usuario = c.nombre_user_coordinador or c.nombre_user_practicante or "Desconocido"
        registros.append({
            "id": c.id,
            "nombre_usuario": usuario,
            "factura": c.n_facturas,
            "cantidad": c.cantidad_piezas,
            "tipo_embalaje": c.t_embalaje.value if c.t_embalaje else None,
            "paqueteria": c.paqueteria.value if c.paqueteria else None,
            "clave_producto": c.clave_producto,
            "tipo_pedido": "Caja",
            "fecha_creacion": c.fecha_hora,
            "largo": c.largo,
            "ancho": c.ancho,
            "alto": c.alto,
            "peso": c.peso,
            "peso_volumetrico": c.peso_volumetrico
        })

    # 🔹 Obtener tarimas
    tarimas = db.query(TarimaMX).all()
    for t in tarimas:
        usuario = t.nombre_user_coordinador or t.nombre_user_practicante or "Desconocido"
        registros.append({
            "id": t.id,
            "nombre_usuario": usuario,
            "factura": t.numero_facturas,
            "cantidad": t.cantidad_piezas,
            "tipo_embalaje": t.tipo_embalaje.value if t.tipo_embalaje else None,
            "paqueteria": t.paqueteria.value if t.paqueteria else None,
            "clave_producto": t.clave_producto,
            "tipo_pedido": "Tarima",
            "fecha_creacion": t.fecha_hora,
            "largo": t.largo,
            "ancho": t.ancho,
            "alto": t.alto,
            "peso": t.peso,
            "peso_volumetrico": t.peso_volumetrico
        })

    registros.sort(key=lambda x: x["fecha_creacion"], reverse=True)
    return registros


# ------------------------------------------------------------------
# 🗑️ DELETE: Eliminar Caja o Tarima
# ------------------------------------------------------------------
@router.delete("/caja/{caja_id}")
def eliminar_caja(caja_id: int, db: Session = Depends(get_db)):
    caja = db.query(CajaMX).filter(CajaMX.id == caja_id).first()
    if not caja:
        raise HTTPException(status_code=404, detail="Caja no encontrada")
    db.delete(caja)
    db.commit()
    return {"mensaje": "Caja eliminada correctamente"}


@router.delete("/tarima/{tarima_id}")
def eliminar_tarima(tarima_id: int, db: Session = Depends(get_db)):
    tarima = db.query(TarimaMX).filter(TarimaMX.id == tarima_id).first()
    if not tarima:
        raise HTTPException(status_code=404, detail="Tarima no encontrada")
    db.delete(tarima)
    db.commit()
    return {"mensaje": "Tarima eliminada correctamente"}


# ------------------------------------------------------------------
# ✏️ PUT: Modelos de actualización
# ------------------------------------------------------------------
class RegistroUpdate(BaseModel):
    numero_factura: Optional[str] = None
    paqueteria: Optional[str] = None
    cantidad_piezas: Optional[int] = None
    clave_producto: Optional[str] = None
    tipo_embalaje: Optional[int] = None
    largo: Optional[float] = None
    ancho: Optional[float] = None
    alto: Optional[float] = None
    peso: Optional[float] = None
    peso_volumetrico: Optional[float] = None
    numero_tarimas: Optional[int] = None  # Solo para Tarimas


# ------------------------------------------------------------------
# ✏️ PUT: Editar Caja
# ------------------------------------------------------------------
@router.put("/caja/{caja_id}")
def editar_caja(caja_id: int, data: RegistroUpdate, db: Session = Depends(get_db)):
    caja = db.query(CajaMX).filter(CajaMX.id == caja_id).first()
    if not caja:
        raise HTTPException(status_code=404, detail="Caja no encontrada")

    if data.paqueteria:
        caja.paqueteria = PaqueteriaEnum(data.paqueteria)
    if data.tipo_embalaje:
        caja.t_embalaje = TipoEmbalajeEnum(data.tipo_embalaje)

    for field, value in data.dict(exclude_unset=True).items():
        if field not in ["paqueteria", "tipo_embalaje"]:
            if hasattr(caja, field):
                setattr(caja, field, value)

    caja.fecha_hora = datetime.now()
    db.commit()
    db.refresh(caja)
    return {"mensaje": "Caja actualizada correctamente"}


# ------------------------------------------------------------------
# ✏️ PUT: Editar Tarima
# ------------------------------------------------------------------
@router.put("/tarima/{tarima_id}")
def editar_tarima(tarima_id: int, data: RegistroUpdate, db: Session = Depends(get_db)):
    tarima = db.query(TarimaMX).filter(TarimaMX.id == tarima_id).first()
    if not tarima:
        raise HTTPException(status_code=404, detail="Tarima no encontrada")

    if data.paqueteria:
        tarima.paqueteria = PaqueteriaEnum(data.paqueteria)
    if data.tipo_embalaje:
        tarima.tipo_embalaje = TipoEmbalajeEnum(data.tipo_embalaje)

    for field, value in data.dict(exclude_unset=True).items():
        if field not in ["paqueteria", "tipo_embalaje"]:
            if hasattr(tarima, field):
                setattr(tarima, field, value)

    tarima.fecha_hora = datetime.now()
    db.commit()
    db.refresh(tarima)
    return {"mensaje": "Tarima actualizada correctamente"}


# ------------------------------------------------------------------
# ✏️ PUT: Unificado - Editar Caja o Tarima según tipo
# ------------------------------------------------------------------
@router.put("/{tipo}/{registro_id}")
def editar_registro(tipo: str, registro_id: int, data: RegistroUpdate, db: Session = Depends(get_db)):
    tipo = tipo.lower()
    if tipo not in ["caja", "tarima"]:
        raise HTTPException(status_code=400, detail="Tipo inválido, debe ser 'caja' o 'tarima'")

    modelo = CajaMX if tipo == "caja" else TarimaMX
    registro = db.query(modelo).filter(modelo.id == registro_id).first()

    if not registro:
        raise HTTPException(status_code=404, detail=f"{tipo.capitalize()} no encontrada")

    # Enums
    if data.paqueteria:
        registro.paqueteria = PaqueteriaEnum(data.paqueteria)
    if data.tipo_embalaje:
        campo_enum = "t_embalaje" if tipo == "caja" else "tipo_embalaje"
        setattr(registro, campo_enum, TipoEmbalajeEnum(data.tipo_embalaje))

    # Campos comunes
    for field, value in data.dict(exclude_unset=True).items():
        if field not in ["paqueteria", "tipo_embalaje"]:
            if hasattr(registro, field):
                setattr(registro, field, value)

    registro.fecha_hora = datetime.now()
    db.commit()
    db.refresh(registro)

    return {"mensaje": f"{tipo.capitalize()} actualizada correctamente"}
