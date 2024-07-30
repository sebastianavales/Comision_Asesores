import datetime
import calendar
import os
import re
import warnings
import glob
import pandas as pd
import numpy as np

# Función para generar la fecha con el ultimo dia del mes de cierre
def ultimo_dia_del_mes():
    while True:
        try:
            mes_cierre = int(input("Indique el mes de cierre (MM): "))
            if mes_cierre < 1 or mes_cierre > 12:
                raise ValueError("El mes debe estar entre 1 y 12.")
            break
        except ValueError as e:
            print(f"Entrada inválida: {e}. Por favor, ingrese un número válido para el mes.")

    while True:
        try:
            año_cierre = int(input("Indique el año de cierre (AAAA): "))
            if año_cierre < 1000 or año_cierre > 9999:
                raise ValueError("El año debe tener cuatro dígitos.")
            break
        except ValueError as e:
            print(f"Entrada inválida: {e}. Por favor, ingrese un número válido para el año.")

    ultimo_dia = calendar.monthrange(año_cierre, mes_cierre)[1]
    fecha = datetime.date(año_cierre, mes_cierre, ultimo_dia)

    print(f"La fecha de cierre es: {fecha.strftime('%d%m%Y')}.")

    return mes_cierre,año_cierre,fecha.strftime("%d%m%Y")

# Función para identificar tipos de fuente
def tipos_fuente_func():

    tipos_fuente = pd.read_excel('01. Input/Tipos Texto.xlsx')

    # Lista de frases para identificar las provisiones
    provision = tipos_fuente.loc[tipos_fuente['TIPO'] == "Provision"]['TEXTO'].tolist()

    # Lista de frases para identificar los pagos
    pago = tipos_fuente.loc[tipos_fuente['TIPO'] == "Pago"]['TEXTO'].tolist()

    # Lista de frases para identificar los ajustes de provision
    ajuste_provision = tipos_fuente.loc[tipos_fuente['TIPO'] == "Ajuste_Provision"]['TEXTO'].tolist()

    # Lista de frases para identificar los ajustes de pago
    ajuste_pago = tipos_fuente.loc[tipos_fuente['TIPO'] == "Ajuste_Pago"]['TEXTO'].tolist()

    # Lista CDTIPO_FUENTE completa
    cdtipo_fuente = tipos_fuente['TEXTO'].tolist()

    print("Parámetros iniciales definidos.")

    return provision,pago,ajuste_provision,ajuste_pago,cdtipo_fuente

# Función para importar archivo principal comisiones
def importar_archivo_principal(mes_cierre,año_cierre,cabecera_anterior_completo,cabecera,cabecera_anterior,desde_eliminacion_cero, hasta_eliminacion_cero):
    
    print("Importación de archivos:")

    archivo_mes_anterior = f'02. Output/Comisiones_Generales_{str(mes_cierre-1).zfill(2)}{año_cierre}_1.csv'

    if os.path.exists(archivo_mes_anterior):
        print(f"El archivo Comisiones_Generales_{str(mes_cierre-1).zfill(2)}{año_cierre}_1 existe.")

        # Mes anterior
        all_files_generales_anterior = glob.glob(f'02. Output/Comisiones_Generales_{str(mes_cierre-1).zfill(2)}{año_cierre}_*.csv')
        
        # Lista para almacenar los DataFrames de los archivos CSV anteriores
        dataframes_generales_anterior= []

        # Cargar cada archivo CSV en un DataFrame y agregarlo a la lista
        for file in all_files_generales_anterior:
            warnings.filterwarnings('ignore')
            df = pd.read_table(file, sep=';', dtype=cabecera_anterior_completo, encoding='latin1')
            # Crear un nuevo diccionario sin el elemento a omitir
            elemento_a_omitir = 'COMENTARIO'
            cabecera_anterior = {k: v for k, v in cabecera_anterior.items() if k != elemento_a_omitir}
            for col in list(cabecera_anterior.keys()):
                df= df.drop(col, axis=1)
            dataframes_generales_anterior.append(df)
        
        generales_anterior = pd.concat(dataframes_generales_anterior, ignore_index=True)

        print(f"Importados {len(all_files_generales_anterior)} archivos anteriores.")

        # Mes actual
        all_files_generales_actual = glob.glob(f'01. Input/01. Generales/*.txt')

        # Lista para almacenar los DataFrames de los archivos CSV actuales
        dataframes_generales_actual= []

        # Cargar cada archivo CSV en un DataFrame y agregarlo a la lista
        for file in all_files_generales_actual:
            warnings.filterwarnings('ignore')
            df = pd.read_table(file, sep=';', header=None, names=list(cabecera.keys()), dtype=cabecera)
            df = df.drop('VACIO', axis=1)
            df['COMENTARIO'] = ""
            dataframes_generales_actual.append(df)

        generales_actual = pd.concat(dataframes_generales_actual, ignore_index=True)

        print(f"Importados {len(all_files_generales_actual)} archivos actuales.")

        # Concatenación ambos meses
        generales = pd.concat([generales_anterior, generales_actual], ignore_index=True)

    else:
        print(f"El archivo Comisiones_Generales_{str(mes_cierre-1).zfill(2)}{año_cierre}_1.csv no existe.")

        # Mes actual
        all_files_generales_actual = glob.glob(f'01. Input/01. Generales/*.txt')

        # Lista para almacenar los DataFrames de los archivos CSV actuales
        dataframes_generales_actual= []

        # Cargar cada archivo CSV en un DataFrame y agregarlo a la lista
        for file in all_files_generales_actual:
            warnings.filterwarnings('ignore')
            df = pd.read_table(file, sep=';', header=None, names=list(cabecera.keys()), dtype=cabecera)
            df = df.drop('VACIO', axis=1)
            dataframes_generales_actual.append(df)

        generales = pd.concat(dataframes_generales_actual, ignore_index=True)

        print(f"Importados {len(all_files_generales_actual)} archivos actuales.")

    generales = generales.loc[generales['PTCOMISION'].notnull()]
    generales = generales.loc[~(generales['PTCOMISION'].between(desde_eliminacion_cero, hasta_eliminacion_cero, inclusive='both'))]
    generales = generales.fillna("")

    return generales

# Función para importar insumos varios
def importar_insumos_varios():

    insumos_varios = '01. Input/Insumos Comisiones.xlsx'

    dolares = pd.read_excel(insumos_varios, sheet_name='Dolares', dtype=str)
    retirados = pd.read_excel(insumos_varios, sheet_name='Retirados', dtype={'CDAGENTE':'str'})
    codigos_directos = pd.read_excel(insumos_varios, sheet_name='Codigos directos', dtype=str)
    asesores_formacion = pd.read_excel(insumos_varios, sheet_name='FyD', dtype={'CDAGENTE':'str'})

    # Transformación Insumos
    dolares['DOLARES'] = "X"
    retirados['RETIRADOS'] = "X"
    codigos_directos['CDDIR'] = "X"
    asesores_formacion['FYD'] = "X"

    # Ajustar NMPOLIZA en el archivo dolares para que tenga como mínimo 12 dígitos
    dolares['NMPOLIZA'] = np.select(
        [dolares['NMPOLIZA'].str.len() < 12],
        [dolares['NMPOLIZA'].str.rjust(12, "0")],
        default=dolares['NMPOLIZA']
    )

    # Seleccionar columnas necesarias en el archivo retirados
    retirados = retirados[['CDAGENTE', 'RETIRADOS', 'FEBAJA']]

    print("Importados insumos adicionales.")

    return dolares,retirados,codigos_directos,asesores_formacion

# Función para válidar el tipo de fuente
def validar_tipo_fuente(generales,cdtipo_fuente):
    cdtipo_fuente_validar = generales['CDTIPO_FUENTE'].unique()

    # Crear una lista de elementos que están en cdtipo_fuente_validar pero no en cdtipo_fuente
    elementos_no_encontrados = [elemento for elemento in cdtipo_fuente_validar if elemento not in cdtipo_fuente]

    # Verificar si hay elementos no encontrados
    if elementos_no_encontrados:
        print("Los siguientes elementos no se encuentran en cdtipo_fuente:")
        for elemento in elementos_no_encontrados:
            print(elemento)
        input("Presione Enter para salir...")
        exit()
    else:
        print("Todos los elementos de cdtipo_fuente están identificados.")

# Función para transformaciones iniciales del dataframe principal
def transformaciones_iniciales(generales,ajuste_pago,pago):
    # Ajustar NMPOLIZA para que tenga como mínimo 12 dígitos
    generales['NMPOLIZA'] = np.select(
        [generales['NMPOLIZA'].str.len() < 12],
        [generales['NMPOLIZA'].str.rjust(12, "0")],
        default=generales['NMPOLIZA']
    )

    # Ajustar CDRAMO para que tenga como mínimo 3 dígitos
    generales['CDRAMO'] = np.select(
        [generales['CDRAMO'].str.len() < 3],
        [generales['CDRAMO'].str.rjust(3, "0")],
        default=generales['CDRAMO']
    )

    # Quitar letras y caracteres especiales de NMRECIBO y convertir a número
    generales['NMRECIBO'] = generales['NMRECIBO'].apply(lambda x: re.sub(r'[^0-9]', '', x))
    #generales['NMRECIBO'] = pd.to_numeric(generales['NMRECIBO'], errors='coerce')

    # Agregar tipo M a CDCOASEGURO
    generales['CDCOASEGURO'] = np.select(
        [generales['CDTIPO_FUENTE'].isin(ajuste_pago),
        (generales['CDCOASEGURO'] == "") & (generales['CDTIPO_FUENTE'].isin(pago))], 
        ["M",
        "M"],
        default=generales['CDCOASEGURO']
    )

    print("Transformaciones iniciales completadas.")

    return generales

# Función para leer archivo depurado para Ajustes Financieros
def lectura_ajustes(mes_cierre,año_cierre,cabecera_anterior_completo):
    archivo_ajustes = f'02. Output/Comisiones_Generales_{str(mes_cierre).zfill(2)}{año_cierre}_1.csv'

    if os.path.exists(archivo_ajustes):
        print(f"El archivo Comisiones_Generales_{str(mes_cierre).zfill(2)}{año_cierre}_1 existe.")
        
        # Leer archivo depurado
        all_files_generales_ajustes = glob.glob(f'02. Output/Comisiones_Generales_{str(mes_cierre).zfill(2)}{año_cierre}_*.csv')
        
        # Lista para almacenar los DataFrames de los archivos CSV ajustes
        dataframes_generales_ajustes= []
        # Cargar cada archivo CSV en un DataFrame y agregarlo a la lista
        for file in all_files_generales_ajustes:
            warnings.filterwarnings('ignore')
            df = pd.read_table(file, sep=';', dtype=cabecera_anterior_completo, encoding='latin1')
            dataframes_generales_ajustes.append(df)
        
        generales_ajustes = pd.concat(dataframes_generales_ajustes, ignore_index=True)
        print(f"Importados {len(all_files_generales_ajustes)} archivos para ajustes.")

        return generales_ajustes
    
    else:
        print(f"El archivo Comisiones_Generales_{str(mes_cierre).zfill(2)}{año_cierre}_1.csv no existe.")
        input("Presione Enter para salir...")
        exit()