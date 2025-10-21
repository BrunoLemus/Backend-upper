# app/db/models/enums.py
from enum import Enum

class PaqueteriaEnum(str, Enum):
    PAQUETEXPRESS = "Paquetexpress"
    ESTAFETA = "Estafeta"
    DHL = "DHL"
    FEDEX = "FedEx"
    UPS = "UPS"
    MERCADO_LIBRE = "Mercado Libre"

class TipoEmbalajeEnum(int, Enum):
    TIPO1 = 1
    TIPO2 = 2
    TIPO3 = 3
    TIPO4 = 4
    TIPO5 = 5

class UserRoleEnum(str, Enum):
    Practicante = "Practicante"
    Coordinador = "Coordinador"
    
class mesaTrabajoEnum(str, Enum):
    MESA1 = "MESA1"
    MESA2 = "MESA2"
    MESA3 = "MESA3"
    MESA4 = "MESA4"
    MESA5 = "MESA5"
    MESA6 = "MESA6"
    MESA7 = "MESA7"
    MESA8 = "MESA8"
    MESA9 = "MESA9"
    MESA10 = "MESA10"
    
    


