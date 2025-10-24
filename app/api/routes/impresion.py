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
# --- NUEVA SOLUCIÓN PARA IMPRESIÓN DE SÍMBOLOS CON ZPL NATIVO ---
# =====================================================================

class OtherLabelData(BaseModel):
    """Esquema para la impresión de etiquetas simples con imágenes."""
    tipo_etiqueta: Literal["fragil", "hacia_arriba"]
    cantidad: int = Field(..., gt=0)


def generate_other_label_zpl(tipo_etiqueta: str) -> str:
    """
    Genera el código ZPL para la etiqueta de símbolo seleccionada,
    dibujando el símbolo con ZPL nativo (texto grande y líneas), NO imágenes.
    """
    
    # 1. Configuración de etiqueta y caja
    zpl = "^XA"
    zpl += "^MMT^PW606^LL606" # Ancho 606 dots para una etiqueta estándar de 4x6"
    zpl += "^FO10,10^GB586,586,3^FS" # Dibuja un marco grande

    if tipo_etiqueta == "fragil":
        # Dibuja la palabra FRÁGIL en grande y un borde para simular un símbolo.
        zpl += "^FO20,100^GB550,450,5^FS" # Caja interior
        zpl += "^CF0,100" # Usa la fuente 'A' (Zebra Default) con altura de 100
        zpl += "^FO50,150^FB500,1,0,C^FDFRÁGIL^FS"
        zpl += "^CF0,40"
        zpl += "^FO50,300^FB500,1,0,C^FDManejar con Cuidado^FS"

    elif tipo_etiqueta == "hacia_arriba":
        # Dibuja dos flechas grandes usando gráficos de caja (simulación) o texto grande.
        # Opción 1: Flechas con texto (más simple y compatible)
        # Usamos fuente ZPL 'D' que a veces incluye flechas o un carácter que simula flechas.
        # Si la fuente 'D' no funciona, se usa un texto simple.
        
        # Símbolo de flecha (usando la fuente 0/A grande para texto)
        zpl += "^CF0,200" # Fuente grande
        zpl += "^FO50,50^FB500,1,0,C^FD^FS" # Línea vacía para centrar
        
        # Intenta usar la fuente 0,150 (Arial/Swiss) para simular una flecha (requiere fuente cargada)
        # Opción más segura: usar solo texto y un borde
        zpl += "^FO50,100^A0N,200,200^FD⬆️^FS" # Esto solo funciona si el font soporta Unicode, mejor usar texto.

        # Mejor Opción: usar texto muy grande y simple
        zpl += "^CF0,150"
        zpl += "^FO50,50^FB500,1,0,C^FDESTELADO^FS"
        zpl += "^FO50,220^FB500,1,0,C^FDD^FS" # D de "Down" invertido
        zpl += "^CF0,120"
        zpl += "^FO50,400^FB500,1,0,C^FDARRIBA^FS"
        
        # Dibuja las flechas usando líneas (más parecido a una imagen)
        zpl += "^FO150,50^GB20,300,5^FS" # Línea vertical izquierda
        zpl += "^FO400,50^GB20,300,5^FS" # Línea vertical derecha
        
        # Dibuja puntas de flecha simples con cajas
        zpl += "^FO140,50^GB40,20,5^FS" # Punta izquierda 1
        zpl += "^FO140,330^GB40,20,5^FS" # Punta izquierda 2
        zpl += "^FO390,50^GB40,20,5^FS" # Punta derecha 1
        zpl += "^FO390,330^GB40,20,5^FS" # Punta derecha 2


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
    
    # **NOTA IMPORTANTE:** En una implementación real, aquí tendrías que enviar
    # el 'final_zpl' a la impresora Zebra (e.g., por socket TCP/IP).
    
    return {"zpl_code": final_zpl}
