from fastapi import APIRouter
from pydantic import BaseModel, Field
import sys 
import json 
from typing import Literal

router = APIRouter() 

# --- MODELOS YA EXISTENTES ---
class LabelData(BaseModel):
    """Define el esquema de datos completo para una etiqueta."""
    paqueteria: str
    factura: str
    num_cajas: int = Field(..., gt=0)
    caja_actual: int = Field(..., gt=0) 
    piezas: int
    clave_producto: str = ""
    ancho: float = 0
    alto: float = 0
    largo: float = 0
    peso: float = 0
    peso_volumetrico: float = 0
    qr_data: str 
    is_tarima: bool = False 

# --- FUNCIÓN YA EXISTENTE (NO MODIFICADA) ---
def generate_zpl_final_label(data: LabelData) -> str:
    """
    Genera el código ZPL, usando el campo is_tarima para ajustar el texto del encabezado,
    y el campo paqueteria para decidir el contenido (completo o básico).
    """
    
    PAQUETERIAS_COMPLETAS = ["Estafeta", "Paquetexpress"]
    imprimir_completo = data.paqueteria in PAQUETERIAS_COMPLETAS
    

    title_type = "TARIMA" if data.is_tarima else "CAJA"
    
    print(f" 🔎 Generando ZPL ({title_type} | QR Condicional) para Factura: {data.factura} | Completo: {imprimir_completo}") 
    
    zpl = "^XA"
    
    zpl += "^MMT^PW606^LL606" 
    
    
    
    qr_data_list = []
    
 
    qr_data_list.append(f"PAQUETERIA:{data.paqueteria}")
    qr_data_list.append(f"FACTURA:{data.factura}")
    qr_data_list.append(f"{title_type.upper()}:{data.caja_actual}_de_{data.num_cajas}") 
    qr_data_list.append(f"PIEZAS:{data.piezas}")
    
    if imprimir_completo:
        
        qr_data_list.append(f"DIMENSIONES:{data.ancho}x{data.alto}x{data.largo}cm")
        qr_data_list.append(f"VOLUMETRICO:{data.peso_volumetrico:.2f}kg")
        qr_data_list.append(f"PESO:{data.peso:.2f}kg")
        
    qr_content = "-".join(qr_data_list) 
    

    qr_size = 4 if imprimir_completo else 5
    qr_y_position = 360 if imprimir_completo else 400
    qr_x_position = 360 
    
    
    zpl += "^CF0,50" 
    zpl += f"^FO23,20^FB560,1,0,C^FD{data.paqueteria.upper()}^FS"  
    
    zpl += "^FO10,80^GB586,2,2^FS" 


    zpl += "^CF0,80" 
    zpl += f"^FO23,100^FB560,1,0,C^FD{title_type}: {data.caja_actual} de {data.num_cajas}^FS" 
    
    
    
    zpl += "^CF0,40" 
    zpl += f"^FO20,230^FDFactura: {data.factura}^FS"
    

    y_current = 280
    
 
    zpl += "^CF0,40" 
    zpl += f"^FO20,{y_current}^FDPiezas: {data.piezas}^FS"
    y_current += 45 
    
    if imprimir_completo:
        
        zpl += "^CF0,35" 
        zpl += f"^FO20,{y_current}^FDDims: {data.ancho}x{data.alto}x{data.largo} cm^FS"
        y_current += 40 
        
        
        zpl += "^CF0,35" 
        zpl += f"^FO20,{y_current}^FDPeso Real: {data.peso:.2f} kg^FS"
        y_current += 40 
    
        zpl += "^CF0,35" 
        zpl += f"^FO20,{y_current}^FDPeso Vol.: {data.peso_volumetrico:.2f} kg^FS"
        y_current += 40 
 
    zpl += f"^FO{qr_x_position},{qr_y_position}^BQN,2,{qr_size}^FDQA,{qr_content}^FS"
    
 
    zpl += "^PQ1" 
    zpl += "^XZ" 
    
    return zpl


# --- ENDPOINTS YA EXISTENTES (NO MODIFICADOS) ---
@router.post("/generate_caja")
def generate_zpl_for_caja(data: list[LabelData]):
    """Genera el ZPL completo a partir de una lista de datos de Cajas."""
    
    for label in data:
        label.is_tarima = False
    
    return {"zpl_code": "".join(generate_zpl_final_label(label) for label in data)}


@router.post("/generate_tarima") 
def generate_zpl_for_tarima(data: list[LabelData]):

    for label in data:
        label.is_tarima = True
        
    return {"zpl_code": "".join(generate_zpl_final_label(label) for label in data)}

# =====================================================================
# --- NUEVA SOLUCIÓN PARA IMPRESIÓN DE SÍMBOLOS CON ZPL NATIVO ---
# =====================================================================

class OtherLabelData(BaseModel):
    """Esquema para la impresión de etiquetas simples con imágenes."""
    tipo_etiqueta: Literal["fragil", "hacia_arriba"]
    cantidad: int = Field(..., gt=0)


def generate_other_label_zpl(tipo_etiqueta: str) -> str:
    """
    Genera el código ZPL para la etiqueta de símbolo seleccionada,
    dibujando el símbolo con ZPL nativo (texto grande y líneas).
    """
    
    # 1. Configuración de etiqueta y caja
    zpl = "^XA"
    zpl += "^MMT^PW606^LL606" # Ancho 606 dots para una etiqueta estándar de 4x6"
    zpl += "^FO10,10^GB586,586,3^FS" # Dibuja un marco grande

    if tipo_etiqueta == "fragil":
        # Dibuja la palabra FRÁGIL en grande y simula un vaso de cristal (ISO 780)
        
        # 2. Dibujar la simulación del Vaso
        zpl += "^FO150,150^GB300,300,5^FS" # Caja grande (Cuerpo del vaso/símbolo)
        zpl += "^FO100,400^GB400,50,5^FS" # Base del vaso
        zpl += "^FO250,150^GB100,300,B,3^FS" # Parte interior/central (efecto de cristal)
        
        # 3. Texto
        zpl += "^CF0,40" # Fuente más pequeña para el texto
        zpl += "^FO50,500^FB500,1,0,C^FDFRÁGIL - MANEJAR CON CUIDADO^FS"

    elif tipo_etiqueta == "hacia_arriba":
        # Dibuja las dos flechas hacia arriba (ISO 780) con líneas ZPL
        
        # 2. Dibujar las dos flechas con líneas y triángulos
        # Flecha IZQUIERDA
        zpl += "^FO100,50^GB10,350,10^FS" # Línea vertical
        zpl += "^FO60,50^GBA,100,100^FS" # Triángulo superior
        zpl += "^FO140,50^GBA,100,100^FS" # Triángulo inferior

        # Flecha DERECHA (posición X 350)
        zpl += "^FO400,50^GB10,350,10^FS" # Línea vertical
        zpl += "^FO360,50^GBA,100,100^FS" # Triángulo superior
        zpl += "^FO440,50^GBA,100,100^FS" # Triángulo inferior
        
        # 3. Texto
        zpl += "^CF0,40"
        zpl += "^FO50,500^FB500,1,0,C^FDESTELADO ARRIBA^FS"
        
    else:
        return ""

    zpl += "^XZ"
    
    return zpl


@router.post("/generate_other_label")
def generate_zpl_for_other_labels(data: OtherLabelData):
    """
    Genera el ZPL para etiquetas Frágil o Hacia Arriba.
    El ZPL se genera con comandos de texto/gráficos ZPL NATIVOS, no con imágenes.
    """
    
    # Generar el bloque ZPL base para una sola etiqueta
    zpl_single_label = generate_other_label_zpl(data.tipo_etiqueta)
    
    # Reemplazar ^XZ (Fin de formato) con el comando ^PQ para la cantidad requerida
    if zpl_single_label:
        # Se asume que generate_other_label_zpl ya generó ^XZ al final.
        # Simplemente se cambia el ^XZ final por ^PQ{cantidad}^XZ
        final_zpl = zpl_single_label.replace("^XZ", f"^PQ{data.cantidad}^XZ")
    else:
        return {"zpl_code": "", "error": "Tipo de etiqueta no válido."}

    print(f"✅ Generado ZPL para {data.cantidad} etiquetas de tipo: {data.tipo_etiqueta}")
    
    return {"zpl_code": final_zpl}
