from fastapi import APIRouter
from pydantic import BaseModel, Field
import sys 
import json 
from typing import Literal

router = APIRouter() 

# --- MODELOS YA EXISTENTES (SIN MODIFICAR) ---
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

# --- FUNCIÓN YA EXISTENTE (SIN MODIFICAR) ---
def generate_zpl_final_label(data: LabelData) -> str:
    # ... (El contenido de generate_zpl_final_label se mantiene intacto)
    
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


# --- ENDPOINTS YA EXISTENTES (SIN MODIFICAR) ---
@router.post("/generate_caja")
def generate_zpl_for_caja(data: list[LabelData]):
    # ...
    for label in data:
        label.is_tarima = False
    return {"zpl_code": "".join(generate_zpl_final_label(label) for label in data)}


@router.post("/generate_tarima") 
def generate_zpl_for_tarima(data: list[LabelData]):
    # ...
    for label in data:
        label.is_tarima = True
    return {"zpl_code": "".join(generate_zpl_final_label(label) for label in data)}

# =====================================================================
# --- SOLUCIÓN AJUSTADA PARA FLECHAS CLARAS ---
# =====================================================================

class OtherLabelData(BaseModel):
    """Esquema para la impresión de etiquetas simples con imágenes."""
    tipo_etiqueta: Literal["fragil", "hacia_arriba"]
    cantidad: int = Field(..., gt=0)


def generate_other_label_zpl(tipo_etiqueta: str) -> str:
    """
    Genera el código ZPL para la etiqueta de símbolo seleccionada,
    usando texto simple (sin acentos) y comandos de dibujo claros.
    """
    
    # Configuración base de la etiqueta
    zpl = "^XA"
    zpl += "^MMT^PW606^LL606" # Etiqueta de 4x6"
    zpl += "^FO10,10^GB586,586,3^FS" # Marco principal

    if tipo_etiqueta == "fragil":
        # Símbolo FRÁGIL (Se mantiene la última versión funcional)
        
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
        # 1. Dibuja las dos flechas hacia arriba (This Way Up)
        
        # Comando de Triángulo (Graphic Diagonal) con relleno sólido: ^GDw,h,t,c,s
        # ^GD se comporta como un comando de dibujo de línea diagonal.
        # Para triángulos sólidos, usamos ^GD con el ancho y alto igual, y un relleno.
        # Es más fiable usar el comando ^GFA con datos, pero ^GD es más simple para geometrías básicas.
        
        # Usaremos el comando ^GFA para dibujar un triángulo sólido que es más reconocido como flecha.
        # Esta es la forma más profesional de enviar un gráfico sin depender de fuentes de símbolos.
        
        # ----------------------------------------------------
        # DIBUJA 2 TRIÁNGULOS SÓLIDOS (MÉTODO ZPL SIMPLE)
        # ----------------------------------------------------

        # Parámetros para un triángulo apuntando hacia arriba (una flecha grande)
        # FOx,y (Posición de inicio)
        # GDw,h,t,B (Ancho, Alto, Grosor, B=Negro/Relleno)
        
        # Flecha IZQUIERDA (Triángulo sólido que apunta hacia arriba)
        # X: 150, Y: 100
        zpl += "^FO150,100^GD150,150,10,B,R^FS" # Triángulo rellenado (La 'R' indica apuntar hacia arriba, aunque la implementación varía)
        # Rectángulo vertical debajo (la base de la flecha)
        zpl += "^FO200,250^GB50,150,5,B^FS"
        
        # Flecha DERECHA (Triángulo sólido que apunta hacia arriba)
        # X: 350, Y: 100
        zpl += "^FO350,100^GD150,150,10,B,R^FS" 
        # Rectángulo vertical debajo (la base de la flecha)
        zpl += "^FO400,250^GB50,150,5,B^FS"
        
        # 2. Texto
        zpl += "^CF0,60"
        zpl += "^FO50,450^FB500,1,0,C^FDESTE LADO^FS"
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
