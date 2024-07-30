import pandas as pd
import logging
from scripts import import_transformar as fimptrans
from scripts import depuracion as fdepuracion
from scripts import identificacion_ajuste as fajustes
from scripts import consolidar_export as fconsexport

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

    #### 2) Definición de Párametros Iniciales

    # Rango de tolerancia para eliminación de registros con valor muy pequeño
    tolerancia_eliminacon_cero = 0.5
    desde_eliminacion_cero = -tolerancia_eliminacon_cero
    hasta_eliminacion_cero = tolerancia_eliminacon_cero

    # Rango de tolerancia para eliminación de pólizas cerradas
    tolerancia_filtros_iniciales = 10
    desde = -tolerancia_filtros_iniciales
    hasta = tolerancia_filtros_iniciales

    # Rango de tolerancia para ajustar pólizas en plantilla ajustes financieros
    tolerancia_ajustes_financieros_desde = 10
    tolerancia_ajustes_financieros_hasta = 1000
    desde_positivo = tolerancia_ajustes_financieros_desde
    desde_negativo = -tolerancia_ajustes_financieros_desde
    hasta_positivo = tolerancia_ajustes_financieros_hasta
    hasta_negativo = -tolerancia_ajustes_financieros_hasta

    valor_no_ajuste = 6000
    desde_no_ajuste = -valor_no_ajuste
    hasta_no_ajuste = valor_no_ajuste

    # Rango de tolerancia para ajustar pólizas en dólares
    tolerancia_porc_pendientes = 0.1
    desde_porc_pendientes = -tolerancia_porc_pendientes
    hasta_porc_pendientes = tolerancia_porc_pendientes

    #### 3) Importación tipos de fuente

    # Función para identificar tipos de fuente
    provision,pago,ajuste_provision,ajuste_pago,cdtipo_fuente = fimptrans.tipos_fuente_func()

    #### 4) Importación archivos necesarios

    # Esquema de datos
    cabecera = {"CDSOCIEDAD": "object",
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
                "VACIO": "object"}

    cabecera_anterior = {"OBSERVACION": "object",
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
                        "FYD": "object",
                        "COMENTARIO": "object"}

    cabecera_anterior_completo = cabecera | cabecera_anterior
    del cabecera_anterior_completo["VACIO"]

    # Función para importar archivo principal comisiones
    vida = fimptrans.importar_archivo_principal(mes_cierre,año_cierre,cabecera_anterior_completo,cabecera,cabecera_anterior,desde_eliminacion_cero, hasta_eliminacion_cero)

    # Función para importar insumos varios
    dolares,retirados,codigos_directos,asesores_formacion = fimptrans.importar_insumos_varios()

    #### 5) Validación CDTIPO_FUENTE

    # Función para válidar el tipo de fuente
    fimptrans.validar_tipo_fuente(vida,cdtipo_fuente)

    #### 6) Transformaciones iniciales

    # Función para transformaciones iniciales del dataframe principal
    vida = fimptrans.transformaciones_iniciales(vida,ajuste_pago,pago)

    #### 7) Depuración de Tablas

    # Función para depuración de tablas
    vida = fdepuracion.depuracion(vida,desde,hasta,provision)

    #### 8) Identificación Ajustes Financieros

    # Función para identificar registros que se deben ajustar
    vida_ajustados1,vida_ajustados2,vida_ajustados3,vida_ajustados4,vida_ajustados5,vida_revision1,vida_revision2,vida_revision3,vida_revision4,vida_revision5 = fajustes.identificacion_ajustes(vida,hasta,desde,hasta_negativo,desde_negativo,hasta_positivo,desde_positivo,provision,desde_no_ajuste,hasta_no_ajuste)

    #### 9) Consolidar Tablas y Exportar

    # Generación de tabla generales nuevamente con registros ajustados y registros a revisar
    vida = pd.concat([vida_revision5, vida_ajustados1, vida_ajustados2, vida_ajustados3, vida_ajustados4, vida_ajustados5])

    # Función para consolidar tablas y exportar
    fconsexport.consolidar_exportar(vida,provision,pago,dolares,desde_porc_pendientes,hasta_porc_pendientes,codigos_directos,retirados,asesores_formacion,mes_cierre,año_cierre)

except Exception as e:
    print("Ocurrió un error. Revisar el archivo Errores.txt")
    input("Presione Enter para salir...")
    logging.error("Ocurrió un error:", exc_info=True)