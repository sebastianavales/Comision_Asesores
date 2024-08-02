import pandas as pd
import numpy as np

# Función para consolidar tablas y exportar
def consolidar_exportar(vida,provision,pago,dolares,desde_porc_pendientes,hasta_porc_pendientes,codigos_directos,retirados,asesores_formacion,mes_cierre,año_cierre):

    vida = vida.sort_values(by=['NMPOLIZA', 'NMRECIBO'], ascending=[True, True])
    vida.reset_index(drop=True, inplace=True)

    # Edición columna Observación para marcar polizas 99999999 y 999999 como revisión
    vida['OBSERVACION'] = np.where((vida['NMRECIBO'].fillna("") == "99999999") | (vida['NMRECIBO'].fillna("") == "999999"),"Revisar",vida['OBSERVACION'])

    # Columna Signo y asignación de valores positivos y negativos 
    vida['SIGNO'] = np.sign(vida['PTCOMISION'])
    vida['POSITIVO'] = np.where(vida['SIGNO'] == 1, vida['PTCOMISION'], 0).astype(float)
    vida['NEGATIVO'] = np.where(vida['SIGNO'] == -1, vida['PTCOMISION'], 0).astype(float)

    # Calculo de absoluto de la comisión
    vida['ABS'] = abs(vida['PTCOMISION'])

    # Contar la cantidad de cada póliza/recibo
    vida_cantidad = vida.groupby(['NMPOLIZA', 'NMRECIBO'])['PTCOMISION'].count().reset_index(name='CANTIDAD')
    vida = vida.merge(vida_cantidad, on=['NMPOLIZA', 'NMRECIBO'], how='left')

    # Asignarle un tipo a cada registro que no vaya a ser ajustado
    vida['TIPO'] = np.select(
        [vida['CDTIPO_FUENTE'].isin(provision),
        vida['CDTIPO_FUENTE'].isin(pago)],
        ["Provision",
        "Pago"],
        default="Ajuste"
    )

    # Agrupar por Poliza y contar las ocurrencias de cada valor en Tipo
    vida_tipo = vida[vida['TIPO'] != ""]
    vida_tipo = vida_tipo.groupby('NMPOLIZA')['TIPO'].unique().reset_index(name='UNICOS')
    vida_tipo['TIPO_UNICO'] = ""

    for index, row in vida_tipo.iterrows():
        if len(row['UNICOS']) == 1: 
            vida_tipo.at[index, 'TIPO_UNICO'] = f"Solo {row['UNICOS'][0]}"
        else:
            vida_tipo.at[index, 'TIPO_UNICO'] = ""

    vida_tipo = vida_tipo.drop('UNICOS', axis=1)

    # Cruce de tabla agrupada con la completa para identificar el tipo unico
    vida = vida.merge(vida_tipo, on='NMPOLIZA', how='left')

    ## Cruce de tabla vida con base de datos de pólizas en dolares
    vida =  vida.merge(dolares, left_on='NMPOLIZA', right_on='NMPOLIZA', how='left')

    ## Agrupar por póliza/recibo y sumar valores positivos y negativos para calcular el % pendiente
    porc_pendiente = vida.groupby(['NMPOLIZA', 'CDPROVISION']).agg({'NEGATIVO': 'sum','POSITIVO':'sum','PTCOMISION':'sum'}).reset_index()
    porc_pendiente['%PENDIENTE'] = np.select(
        [porc_pendiente['POSITIVO'] == 0],
        [1],
        default=porc_pendiente['PTCOMISION'] / porc_pendiente['POSITIVO']
    )
    porc_pendiente = porc_pendiente[['NMPOLIZA', 'CDPROVISION', '%PENDIENTE']]

    ## Cruce de tabla agrupada con la completa para identificar el % pendiente
    vida = vida.merge(porc_pendiente, on=['NMPOLIZA', 'CDPROVISION'], how='left')

    ## Marcar las pólizas en dólares que tienen porcentaje pendiente y son aptas para ajuste
    vida['AJUSTAR?'] = np.select(
        [(vida['DOLARES'] == "X") & (vida['%PENDIENTE'] !=0) & (vida['%PENDIENTE'].between(desde_porc_pendientes, hasta_porc_pendientes, inclusive='both'))],
        ["Ajustado Dólares"],
        default=vida['AJUSTAR?']
    )

    vida['OBSERVACION'] = vida['OBSERVACION'].fillna("")

    ## Observación para las pólizas no dólares que tienen porcentaje pendiente
    for index, row in vida.iterrows():
        if (row['DOLARES'] != "X") and (row['OBSERVACION'] != "") and (row['%PENDIENTE'] !=0) and (desde_porc_pendientes <= row['%PENDIENTE'] <= hasta_porc_pendientes):
            vida.at[index, 'OBSERVACION'] = f"{row['OBSERVACION']}, Porcentaje pendiente pequeño"
        elif (row['DOLARES'] != "X") and (row['OBSERVACION'] == "") and (row['%PENDIENTE'] !=0) and  (desde_porc_pendientes <= row['%PENDIENTE'] <= hasta_porc_pendientes):
            vida.at[index, 'OBSERVACION'] = f"Porcentaje pendiente pequeño"
        else:
            vida.at[index, 'OBSERVACION'] = row['OBSERVACION']

    # Tabla para identificar el valor Ajustes Financieros por póliza en dólares
    vida_ajustados6 = vida.loc[vida['AJUSTAR?'] == "Ajustado Dólares"]

    ## Cruce de tabla vida con base de datos de códigos directos
    vida =  vida.merge(codigos_directos, left_on='CDAGENTE', right_on='CDAGENTE', how='left')

    ## Cruce de tabla vida con base de datos de asesores retirados
    vida = vida.merge(retirados, left_on='CDAGENTE', right_on='CDAGENTE', how='left')
    vida['FEREGISTRO'] = pd.to_datetime(vida['FEREGISTRO'])

    ## Identificar si un asesor tiene registros luego de su fecha de retiro
    vida['POST_RETIRO'] = np.select(
        [(vida['RETIRADOS'] == "X") & (vida['FEREGISTRO'] > vida['FEBAJA'])],
        ["Registro Post-Retiro"],
        default=""
    )

    ## Calcular días entre la fecha de retiro del asesor y la fecha de registro de cada elemento
    vida['DIAS_RETIRO'] = (vida['FEBAJA'] - vida['FEREGISTRO']).dt.days

    vida['FEREGISTRO'] = vida['FEREGISTRO'].dt.strftime('%Y/%m/%d')
    vida['FEBAJA'] = vida['FEBAJA'].dt.strftime('%Y/%m/%d')

    ## Cruce de tabla vida con base de datos de asesores en FyD
    vida = vida.merge(asesores_formacion, left_on='CDAGENTE', right_on='CDAGENTE', how='left')

    vida['FECHA_INGRESO'] = vida['FECHA_INGRESO'].dt.strftime('%Y/%m/%d')

    ## Crear columna COMENTARIO si no existe
    if 'COMENTARIO' in vida.columns:
        columna_temporal = vida.pop('COMENTARIO')
        vida['COMENTARIO'] = columna_temporal
    else:
        vida['COMENTARIO'] = ""

    # Calcula el número total de filas en el DataFrame
    total_filas = len(vida)

    # Define el tamaño de la fracción
    tamano_fraccion = 500000

    # Calcula el número total de fracciones
    total_fracciones = total_filas // tamano_fraccion + (1 if total_filas % tamano_fraccion != 0 else 0)

    # Bucle para dividir y exportar en fracciones
    for i in range(total_fracciones):
        inicio = i * tamano_fraccion
        fin = min((i + 1) * tamano_fraccion, total_filas)
        
        # Obtén la fracción actual del DataFrame
        fraccion_df = vida.iloc[inicio:fin]
        
        # Exporta la fracción a un archivo CSV
        fraccion_df.to_excel(f'02. Output/Comisiones_Vida_{str(mes_cierre).zfill(2)}{año_cierre}_{i + 1}.xlsx', index=False)

    print("Archivo base exportado con transformaciones en la carpeta 02. Output.")