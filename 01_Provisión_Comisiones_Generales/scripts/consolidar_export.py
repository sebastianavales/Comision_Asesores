import pandas as pd
import numpy as np

# Función para consolidar tablas y exportar
def consolidar_exportar(generales,provision,pago,dolares,desde_porc_pendientes,hasta_porc_pendientes,codigos_directos,retirados,asesores_formacion,mes_cierre,año_cierre):

    generales = generales.sort_values(by=['NMPOLIZA', 'NMRECIBO'], ascending=[True, True])
    generales.reset_index(drop=True, inplace=True)
    
    # Edición columna Observación para marcar polizas 99999999 y 999999 como revisión
    generales['OBSERVACION'] = np.where((generales['AJUSTAR?'] == "") & ((generales['NMRECIBO'].fillna("") == "99999999") | (generales['NMRECIBO'].fillna("") == "999999")),"Revisar",generales['OBSERVACION'])

    # Columna Signo y asignación de valores positivos y negativos 
    generales['SIGNO'] = np.sign(generales['PTCOMISION'])
    generales['POSITIVO'] = np.where(generales['SIGNO'] == 1, generales['PTCOMISION'], 0).astype(float)
    generales['NEGATIVO'] = np.where(generales['SIGNO'] == -1, generales['PTCOMISION'], 0).astype(float)

    # Calculo de absoluto de la comisión
    generales['ABS'] = abs(generales['PTCOMISION'])

    # Contar la cantidad de cada póliza/recibo
    generales_cantidad = generales.groupby(['NMPOLIZA', 'NMRECIBO'])['PTCOMISION'].count().reset_index(name='CANTIDAD')
    generales = generales.merge(generales_cantidad, on=['NMPOLIZA', 'NMRECIBO'], how='left')

    # Asignarle un tipo a cada registro
    generales['TIPO'] = np.select(
        [generales['CDTIPO_FUENTE'].isin(provision),
        generales['CDTIPO_FUENTE'].isin(pago)],
        ["Provision",
        "Pago"],
        default="Ajuste"
    )

    # Agrupar por Poliza y contar las ocurrencias de cada valor en Tipo
    generales_tipo = generales[generales['TIPO'] != ""]
    generales_tipo = generales_tipo.groupby('NMPOLIZA')['TIPO'].unique().reset_index(name='UNICOS')
    generales_tipo['TIPO_UNICO'] = ""

    for index, row in generales_tipo.iterrows():
        if len(row['UNICOS']) == 1: 
            generales_tipo.at[index, 'TIPO_UNICO'] = f"Solo {row['UNICOS'][0]}"
        else:
            generales_tipo.at[index, 'TIPO_UNICO'] = ""

    generales_tipo = generales_tipo.drop('UNICOS', axis=1)

    # Cruce de tabla agrupada con la completa para identificar el tipo unico
    generales = generales.merge(generales_tipo, on='NMPOLIZA', how='left')

    ## Cruce de tabla generales con base de datos de pólizas en dolares
    generales =  generales.merge(dolares, left_on='NMPOLIZA', right_on='NMPOLIZA', how='left')

    ## Agrupar por póliza/recibo y sumar valores positivos y negativos para calcular el % pendiente
    porc_pendiente = generales.groupby(['NMPOLIZA', 'NMRECIBO']).agg({'NEGATIVO': 'sum','POSITIVO':'sum','PTCOMISION':'sum'}).reset_index()
    porc_pendiente['%PENDIENTE'] = np.select(
        [porc_pendiente['POSITIVO'] == 0],
        [1],
        default=porc_pendiente['PTCOMISION'] / porc_pendiente['POSITIVO']
    )
    porc_pendiente = porc_pendiente[['NMPOLIZA', 'NMRECIBO', '%PENDIENTE']]

    ## Cruce de tabla agrupada con la completa para identificar el % pendiente
    generales = generales.merge(porc_pendiente, on=['NMPOLIZA', 'NMRECIBO'], how='left')

    ## Marcar las pólizas en dólares que tienen porcentaje pendiente y son aptas para ajuste
    generales['AJUSTAR?'] = np.select(
        [(generales['DOLARES'] == "X") & (generales['%PENDIENTE'] !=0) & (generales['%PENDIENTE'].between(desde_porc_pendientes, hasta_porc_pendientes, inclusive='both'))],
        ["Ajustado Dólares"],
        default=generales['AJUSTAR?']
    )

    generales['OBSERVACION'] = generales['OBSERVACION'].fillna("")

    ## Observación para las pólizas no dólares que tienen porcentaje pendiente
    for index, row in generales.iterrows():
        if (row['DOLARES'] != "X") and (row['OBSERVACION'] != "") and (row['%PENDIENTE'] !=0) and (desde_porc_pendientes <= row['%PENDIENTE'] <= hasta_porc_pendientes):
            generales.at[index, 'OBSERVACION'] = f"{row['OBSERVACION']}, Porcentaje pendiente pequeño"
        elif (row['DOLARES'] != "X") and (row['OBSERVACION'] == "") and (row['%PENDIENTE'] !=0) and (desde_porc_pendientes <= row['%PENDIENTE'] <= hasta_porc_pendientes):
            generales.at[index, 'OBSERVACION'] = f"Porcentaje pendiente pequeño"
        else:
            generales.at[index, 'OBSERVACION'] = row['OBSERVACION']

    # Tabla para identificar el valor Ajustes Financieros por póliza en dólares
    generales_ajustados5 = generales.loc[generales['AJUSTAR?'] == "Ajustado Dólares"]

    ## Cruce de tabla generales con base de datos de códigos directos
    generales =  generales.merge(codigos_directos, left_on='CDAGENTE', right_on='CDAGENTE', how='left')

    ## Cruce de tabla generales con base de datos de asesores retirados
    generales = generales.merge(retirados, left_on='CDAGENTE', right_on='CDAGENTE', how='left')
    generales['FEREGISTRO'] = pd.to_datetime(generales['FEREGISTRO'])

    ## Identificar si un asesor tiene registros luego de su fecha de retiro
    generales['POST_RETIRO'] = np.select(
        [(generales['RETIRADOS'] == "X") & (generales['FEREGISTRO'] > generales['FEBAJA'])],
        ["Registro Post-Retiro"],
        default=""
    )

    ## Calcular días entre la fecha de retiro del asesor y la fecha de registro de cada elemento
    generales['DIAS_RETIRO'] = (generales['FEBAJA'] - generales['FEREGISTRO']).dt.days

    generales['FEREGISTRO'] = generales['FEREGISTRO'].dt.strftime('%Y/%m/%d')

    ## Cruce de tabla generales con base de datos de asesores en FyD
    generales = generales.merge(asesores_formacion, left_on='CDAGENTE', right_on='CDAGENTE', how='left')
    
    ## Crear columna COMENTARIO si no existe
    if 'COMENTARIO' in generales.columns:
        columna_temporal = generales.pop('COMENTARIO')
        generales['COMENTARIO'] = columna_temporal
    else:
        generales['COMENTARIO'] = ""

    # Calcula el número total de filas en el DataFrame
    total_filas = len(generales)

    # Define el tamaño de la fracción
    tamano_fraccion = 500000

    # Calcula el número total de fracciones
    total_fracciones = total_filas // tamano_fraccion + (1 if total_filas % tamano_fraccion != 0 else 0)

    # Bucle para dividir y exportar en fracciones
    for i in range(total_fracciones):
        inicio = i * tamano_fraccion
        fin = min((i + 1) * tamano_fraccion, total_filas)
        
        # Obtén la fracción actual del DataFrame
        fraccion_df = generales.iloc[inicio:fin]
        
        # Exporta la fracción a un archivo CSV
        fraccion_df.to_csv(f'02. Output/Comisiones_Generales_{str(mes_cierre).zfill(2)}{año_cierre}_{i + 1}.csv', index=False, sep=';', encoding="latin1")

    print("Archivo base exportado con transformaciones en la carpeta 02. Output.")