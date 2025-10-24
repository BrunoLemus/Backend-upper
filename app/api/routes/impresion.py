from fastapi import APIRouter
from pydantic import BaseModel, Field
import sys 
import json 
from typing import Literal

router = APIRouter() 

# --- MODELOS Y FUNCIONES EXISTENTES (SIN MODIFICAR) ---
class LabelData(BaseModel):
    # ... (El contenido de LabelData se mantiene intacto)
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

def generate_zpl_final_label(data: LabelData) -> str:
    # ... (El contenido de generate_zpl_final_label se mantiene intacto)
    
    PAQUETERIAS_COMPLETAS = ["Estafeta", "Paquetexpress"]
    imprimir_completo = data.paqueteria in PAQUETERIAS_COMPLETAS
    
    # ... (ZPL code generation remains the same)
    
    title_type = "TARIMA" if data.is_tarima else "CAJA"
    print(f" 🔎 Generando ZPL ({title_type} | QR Condicional) para Factura: {data.factura} | Completo: {imprimir_completo}") 
    zpl = "^XA^MMT^PW606^LL606" 
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
    zpl += "^PQ1^XZ" 
    return zpl


@router.post("/generate_caja")
def generate_zpl_for_caja(data: list[LabelData]):
    for label in data:
        label.is_tarima = False
    return {"zpl_code": "".join(generate_zpl_final_label(label) for label in data)}


@router.post("/generate_tarima") 
def generate_zpl_for_tarima(data: list[LabelData]):
    for label in data:
        label.is_tarima = True
    return {"zpl_code": "".join(generate_zpl_final_label(label) for label in data)}

# =====================================================================
# --- SOLUCIÓN FINAL: DIBUJO DEL PICTOGRAMA ISO 780 CON RECTÁNGULOS ZPL ---
# =====================================================================

class OtherLabelData(BaseModel):
    """Esquema para la impresión de etiquetas simples con imágenes."""
    tipo_etiqueta: Literal["fragil", "hacia_arriba"]
    cantidad: int = Field(..., gt=0)


def generate_other_label_zpl(tipo_etiqueta: str) -> str:
    """
    Genera el código ZPL para la etiqueta de símbolo seleccionada,
    dibujando el símbolo con la mayor fidelidad posible al pictograma ISO.
    """
    
    # Configuración base de la etiqueta
    zpl = "^XA"
    zpl += "^MMT^PW606^LL606" # Etiqueta de 4x6"
    zpl += "^FO10,10^GB586,586,3^FS" # Marco principal (como en la imagen)

    if tipo_etiqueta == "fragil":
        # Símbolo FRÁGIL (Mantenido para evitar errores de codificación)
        
        # Cuerpo del vaso (caja)
        zpl += "^FO150,150^GB300,250,5^FS" 
        # Base del vaso
        zpl += "^FO100,400^GB400,20,5^FS" 
        # Línea central divisoria (efecto de cristal)
        zpl += "^FO150,275^GB300,2,2^FS" 

        # Texto (sin acento)
        zpl += "^CF0,60" 
        zpl += "^FO50,450^FB500,1,0,C^FDFRAGIL^FS" 
        zpl += "^CF0,40"
        zpl += "^FO50,520^FB500,1,0,C^FDCUIDADO^FS" 

    elif tipo_etiqueta == "hacia_arriba":
        # 1. Dibuja la BASE HORIZONTAL gruesa (como en la imagen)
        zpl += "^FO50,400^GB500,40,40,B^FS" # X=50, Y=400, Ancho=500, Alto=40, Grosor=40, Relleno=B (sólido)
        
        # 2. Dibuja las DOS FLECHAS SÓLIDAS Y GRUESAS (usando rectángulos rellenos)
        
        # Parámetros para las flechas: Ancho del tallo=50, Altura del tallo=200
        TALLO_H = 200
        TALLO_W = 50
        PUNTA_W = 100
        PUNTA_H = 50
        
        # FLECHA IZQUIERDA
        # Tallo vertical
        zpl += "^FO140,200^GB50,200,50,B^FS" # X=140, Y=200, W=50, H=200 (sólido)
        # Punta de flecha (Rectángulo superior horizontal para la forma sólida)
        # ^GB ancho, alto, grosor, color, redondeo (solo se usa 'B' para relleno sólido)
        # Se necesita un triángulo. La forma más simple es usar ^GF o una fuente, pero usaremos el método más compatible: dibujar un RECTÁNGULO MUY ANCHO y luego ajustar la forma con un rectangulo horizontal encima.
        
        # Tallo
        zpl += "^FO150,150^GB50,250,50,B^FS" # X=150
        # Rectángulo para la punta ancha (simulando la base del triángulo)
        zpl += "^FO100,150^GB150,50,50,B^FS" # X=100 (Cubre 150 puntos de ancho)
        
        # FLECHA DERECHA
        # Tallo
        zpl += "^FO400,150^GB50,250,50,B^FS" # X=400
        # Rectángulo para la punta ancha
        zpl += "^FO350,150^GB150,50,50,B^FS" # X=350
        
        # NOTA: En ZPL, lograr un triángulo perfecto con ^GB es imposible. 
        # La solución de rectángulos anchos es el mejor compromiso para un gráfico sólido sin usar ^GFA.

        # 3. Texto
        zpl += "^CF0,60"
        zpl += "^FO50,450^FB500,1,0,C^FDESTELADO^FS"
        zpl += "^CF0,60"
        zpl += "^FO50,520^FB500,1,0,C^FDARRIBA^FS"
        
    else:
        return ""

    zpl += "^XZ"
    
    return zpl


@router.post("/generate_other_label")
def generate_zpl_for_other_labels(data: OtherLabelData):
    # ... (El contenido de este endpoint se mantiene intacto)
    
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
