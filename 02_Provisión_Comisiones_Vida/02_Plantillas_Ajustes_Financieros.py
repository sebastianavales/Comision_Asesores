import logging
from scripts import import_transformar as fimptrans
from scripts import plantillas_ajustes as fplantajust
from scripts import plantillas_ajustes_usd as fplantajustusd

# Arhivo para almacenar errores de ejecución
class UnderscoreLineFormatter(logging.Formatter):
    def format(self, record):
        result = super().format(record)
        return result + "\n" + "_" * 220 + "\n"

logging.basicConfig(
    filename='Errores.txt',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger()
for handler in logger.handlers:
    handler.setFormatter(UnderscoreLineFormatter(handler.formatter._fmt))

try:
    #### 1) Inputs para Ejecución del Proceso

    # Funcion para generar la fecha con el ultimo dia del mes de cierre
    mes_cierre,año_cierre,ultimo_dia_del_mes = fimptrans.ultimo_dia_del_mes()

    #### 2) Importación archivos necesarios

    # Esquema de datos
    cabecera_anterior_completo = {"CDSOCIEDAD": "object",
                "CDRAMO": "object",
                "NMPOLIZA": "object",
                "NMRECIBO": "object",
                "CDCONCEPTO": "object",
                "CDCOASEGURO": "object",
                "CDAGENTE": "object",
                "CDDELEGACION": "object",
                "PTPRIMA": "float",
                "PTCOMISION": "float",
                "POCOMISION": "float",
                "CDTIPO_FUENTE": "object",
                "FEDOCUMENTO": "object",
                "FEREGISTRO": "object",
                "FEINI_VIGENCIA": "object",
                "FEFIN_FIGENCIA": "object",
                "CDLIBRO": "object",
                "OBSERVACION": "object",
                "AJUSTAR?": "object",
                "SIGNO": "float64",
                "POSITIVO": "float64",
                "NEGATIVO": "float64",
                "ABS": "float64",
                "CANTIDAD": "float64",
                "TIPO": "object",
                "TIPO_UNICO": "object",
                "DOLARES": "object",
                "%PENDIENTE": "float64",
                "CDDIR": "object",
                "RETIRADOS": "object",
                "FEBAJA": "object",
                "POST_RETIRO": "object",
                "DIAS_RETIRO": "float64",
                "FECHA_INGRESO" : "object",
                "FYD": "object",
                "COMENTARIO": "object"}

    # Función para leer archivo depurado para Ajustes Financieros
    vida_ajustes = fimptrans.lectura_ajustes(mes_cierre,año_cierre,cabecera_anterior_completo)

    #### 3) Generar Plantillas de Ajustes Financieros

    # Función para generar plantillas de ajustes financieros
    fplantajust.plantillas_ajustes(vida_ajustes,ultimo_dia_del_mes,mes_cierre,año_cierre)

    #### 4) Generar Plantillas de Ajustes Financieros USD

    # Función para generar plantillas de ajustes financieros en USD
    fplantajustusd.plantillas_ajustes_usd(vida_ajustes,ultimo_dia_del_mes,mes_cierre,año_cierre)

except Exception as e:
    print("Ocurrió un error. Revisar el archivo Errores.txt")
    input("Presione Enter para salir...")
    logging.error("Ocurrió un error:", exc_info=True)