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

# --- FUNCIÓN YA EXISTENTE ---
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


# --- ENDPOINTS YA EXISTENTES ---
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
# --- NUEVA SOLUCIÓN PARA IMPRESIÓN DE IMÁGENES ---
# =====================================================================

class OtherLabelData(BaseModel):
    """Esquema para la impresión de etiquetas simples con imágenes."""
    tipo_etiqueta: Literal["fragil", "hacia_arriba"]
    cantidad: int = Field(..., gt=0)


# Placeholder para el código Hexadecimal ZPL de la imagen "frágil"
# NOTA: En una implementación real, esto sería el código HEX generado de fragil.png
ZPL_IMAGE_DATA_FRAGIL = "" 

# Placeholder para el código Hexadecimal ZPL de la imagen "hacia_arriba"
# NOTA: En una implementación real, esto sería el código HEX generado de arriba.png
ZPL_IMAGE_DATA_ARRIBA = "" 


def generate_image_label_zpl(tipo_etiqueta: str) -> str:
    """
    Genera el código ZPL para la etiqueta de imagen seleccionada.
    """
    
    # 1. Definir los datos de la imagen ZPL y el texto
    if tipo_etiqueta == "fragil":
        image_data = ZPL_IMAGE_DATA_FRAGIL
        title = "MANEJAR FRÁGIL"
        # Usar un tamaño de 300x300 puntos para la imagen de ejemplo
        graphic_field = "^FO100,100^GFA,11520,11520,240,ZPL_IMAGE_DATA_FRAGIL^FS" 

    elif tipo_etiqueta == "hacia_arriba":
        image_data = ZPL_IMAGE_DATA_ARRIBA
        title = "ESTE LADO HACIA ARRIBA"
        # Usar un tamaño de 300x300 puntos para la imagen de ejemplo
        graphic_field = "^FO100,100^GFA,11520,11520,240,ZPL_IMAGE_DATA_ARRIBA^FS"
    else:
        return ""

    # 2. Construir el código ZPL
    zpl = "^XA"
    zpl += "^MMT^PW606^LL606" # Configuración de ancho de impresión (606 dots)
    
    # Título (opcional, para referencia)
    zpl += "^CF0,40"
    zpl += f"^FO20,50^FD{title}^FS"

    # Marco de la etiqueta (opcional)
    zpl += "^FO10,10^GB586,586,2^FS"
    
    # Insertar el campo gráfico (imagen)
    # NOTA: 'graphic_field' debe contener el código hexadecimal real de la imagen.
    zpl += graphic_field.replace("ZPL_IMAGE_DATA_FRAGIL", image_data).replace("ZPL_IMAGE_DATA_ARRIBA", image_data)

    zpl += "^XZ"
    
    return zpl


@router.post("/generate_other_label")
def generate_zpl_for_other_labels(data: OtherLabelData):
    """
    Genera el ZPL para etiquetas Frágil o Hacia Arriba, incluyendo la imagen codificada.
    
    El Frontend llamará a este endpoint con:
    {
      "tipo_etiqueta": "fragil" (o "hacia_arriba"),
      "cantidad": 5
    }
    """
    
    # Generar el bloque ZPL base para una sola etiqueta
    zpl_single_label = generate_image_label_zpl(data.tipo_etiqueta)
    
    # Ajustar el comando PQ (Print Quantity) para la cantidad requerida
    # Es más eficiente cambiar el ^PQ del ZPL generado una vez.
    if zpl_single_label:
        # Reemplazar ^XZ (Fin de formato) con ^PQ{cantidad}^XZ
        final_zpl = zpl_single_label.replace("^XZ", f"^PQ{data.cantidad}^XZ")
    else:
        return {"zpl_code": "", "error": "Tipo de etiqueta no válido."}

    print(f"✅ Generado ZPL para {data.cantidad} etiquetas de tipo: {data.tipo_etiqueta}")
    
    return {"zpl_code": final_zpl}