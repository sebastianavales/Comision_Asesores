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

    archivo_mes_anterior = f'02. Output/Comisiones_Vida_{str(mes_cierre-1).zfill(2)}{año_cierre}_1.csv'

    if os.path.exists(archivo_mes_anterior):
        print(f"El archivo Comisiones_Vida_{str(mes_cierre-1).zfill(2)}{año_cierre}_1 existe.")

        # Mes anterior
        all_files_vida_anterior = glob.glob(f'02. Output/Comisiones_Vida_{str(mes_cierre-1).zfill(2)}{año_cierre}_*.csv')
        
        # Lista para almacenar los DataFrames de los archivos CSV anteriores
        dataframes_vida_anterior= []

        # Cargar cada archivo CSV en un DataFrame y agregarlo a la lista
        for file in all_files_vida_anterior:
            warnings.filterwarnings('ignore')
            df = pd.read_table(file, sep=';', dtype=cabecera_anterior_completo, encoding='latin1')
            # Crear un nuevo diccionario sin el elemento a omitir
            elemento_a_omitir = 'COMENTARIO'
            cabecera_anterior = {k: v for k, v in cabecera_anterior.items() if k != elemento_a_omitir}
            for col in list(cabecera_anterior.keys()):
                df= df.drop(col, axis=1)
            dataframes_vida_anterior.append(df)
        
        vida_anterior = pd.concat(dataframes_vida_anterior, ignore_index=True)

        print(f"Importados {len(all_files_vida_anterior)} archivos anteriores.")

        # Mes actual
        all_files_vida_actual = glob.glob(f'01. Input/02. Vida/*.txt')

        # Lista para almacenar los DataFrames de los archivos CSV actuales
        dataframes_vida_actual= []

        # Cargar cada archivo CSV en un DataFrame y agregarlo a la lista
        for file in all_files_vida_actual:
            warnings.filterwarnings('ignore')
            df = pd.read_table(file, sep=';', header=None, names=list(cabecera.keys()), dtype=cabecera)
            df = df.drop('VACIO', axis=1)
            df['COMENTARIO'] = ""
            dataframes_vida_actual.append(df)

        vida_actual = pd.concat(dataframes_vida_actual, ignore_index=True)

        print(f"Importados {len(all_files_vida_actual)} archivos actuales.")

        # Concatenación ambos meses
        vida = pd.concat([vida_anterior, vida_actual], ignore_index=True)

    else:
        print(f"El archivo Comisiones_Vida_{str(mes_cierre-1).zfill(2)}{año_cierre}_1.csv no existe.")

        # Mes actual
        all_files_vida_actual = glob.glob(f'01. Input/02. Vida/*.txt')

        # Lista para almacenar los DataFrames de los archivos CSV actuales
        dataframes_vida_actual= []

        # Cargar cada archivo CSV en un DataFrame y agregarlo a la lista
        for file in all_files_vida_actual:
            warnings.filterwarnings('ignore')
            df = pd.read_table(file, sep=';', header=None, names=list(cabecera.keys()), dtype=cabecera)
            df = df.drop('VACIO', axis=1)
            dataframes_vida_actual.append(df)

        vida = pd.concat(dataframes_vida_actual, ignore_index=True)

        print(f"Importados {len(all_files_vida_actual)} archivos actuales.")

    vida = vida.loc[vida['PTCOMISION'].notnull()]
    vida = vida.loc[~(vida['PTCOMISION'].between(desde_eliminacion_cero, hasta_eliminacion_cero, inclusive='both'))]
    vida = vida.fillna("")

    return vida

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
def validar_tipo_fuente(vida,cdtipo_fuente):
    cdtipo_fuente_validar = vida['CDTIPO_FUENTE'].unique()

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
def transformaciones_iniciales(vida,ajuste_pago,pago):
    # Ajustar NMPOLIZA para que tenga como mínimo 12 dígitos
    vida['NMPOLIZA'] = np.select(
        [vida['NMPOLIZA'].str.len() < 12],
        [vida['NMPOLIZA'].str.rjust(12, "0")],
        default=vida['NMPOLIZA']
    )

    # Ajustar CDRAMO para que tenga como mínimo 3 dígitos
    vida['CDRAMO'] = np.select(
        [vida['CDRAMO'].str.len() < 3],
        [vida['CDRAMO'].str.rjust(3, "0")],
        default=vida['CDRAMO']
    )

    # Quitar letras y caracteres especiales de NMRECIBO y convertir a número
    vida['NMRECIBO'] = vida['NMRECIBO'].apply(lambda x: re.sub(r'[^0-9]', '', x))
    vida['NMRECIBO'] = pd.to_numeric(vida['NMRECIBO'], errors='coerce')

    # Agregar tipo M a CDCOASEGURO
    vida['CDCOASEGURO'] = np.select(
        [vida['CDTIPO_FUENTE'].isin(ajuste_pago),
        (vida['CDCOASEGURO'] == "") & (vida['CDTIPO_FUENTE'].isin(pago))], 
        ["M",
        "M"],
        default=vida['CDCOASEGURO']
    )

    print("Transformaciones iniciales completadas.")

    return vida

# Función para leer archivo depurado para Ajustes Financieros
def lectura_ajustes(mes_cierre,año_cierre,cabecera_anterior_completo):
    archivo_ajustes = f'02. Output/Comisiones_Vida_{str(mes_cierre).zfill(2)}{año_cierre}_1.csv'

    if os.path.exists(archivo_ajustes):
        print(f"El archivo Comisiones_Vida_{str(mes_cierre).zfill(2)}{año_cierre}_1 existe.")
        
        # Leer archivo depurado
        all_files_vida_ajustes = glob.glob(f'02. Output/Comisiones_Vida_{str(mes_cierre).zfill(2)}{año_cierre}_*.csv')
        
        # Lista para almacenar los DataFrames de los archivos CSV ajustes
        dataframes_vida_ajustes= []
        # Cargar cada archivo CSV en un DataFrame y agregarlo a la lista
        for file in all_files_vida_ajustes:
            warnings.filterwarnings('ignore')
            df = pd.read_table(file, sep=';', dtype=cabecera_anterior_completo, encoding='latin1')
            dataframes_vida_ajustes.append(df)
        
        vida_ajustes = pd.concat(dataframes_vida_ajustes, ignore_index=True)
        print(f"Importados {len(all_files_vida_ajustes)} archivos para ajustes.")

        return vida_ajustes
    
    else:
        print(f"El archivo Comisiones_Vida_{str(mes_cierre).zfill(2)}{año_cierre}_1.csv no existe.")
        input("Presione Enter para salir...")
        exit()