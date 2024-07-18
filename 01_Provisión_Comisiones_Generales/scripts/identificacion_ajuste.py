import numpy as np

# Función para identificar registros que se deben ajustar
def identificacion_ajustes(generales,hasta,desde,hasta_negativo,desde_negativo,hasta_positivo,desde_positivo,provision,desde_no_ajuste,hasta_no_ajuste):

    ## Identificación de registros para ajustes financieros por póliza

    # Agrupar por póliza para determinar su valor y marcar las que tienen valor apto para ajuste
    generales_ajustes1_temp = generales.groupby(['NMPOLIZA'])['PTCOMISION'].sum().reset_index()
    generales_ajustes1_temp['AJUSTAR?'] = np.select(
        [((generales_ajustes1_temp['PTCOMISION'].between(hasta_negativo, desde_negativo, inclusive='both')) | 
        (generales_ajustes1_temp['PTCOMISION'].between(desde_positivo, hasta_positivo, inclusive='both')))],
        ["Ajustado Póliza"],
        default=""
    )
    generales_ajustes1_temp = generales_ajustes1_temp.drop('PTCOMISION', axis=1)

    # Cruce de tabla agrupada con la completa para identificar registros que se deben ajustar
    generales_ajustes1 = generales.merge(generales_ajustes1_temp, on=['NMPOLIZA'], how='left')

    # Identificar cuales registros que se marcaron como Ajuste no aplican realmente
    generales_ajustes1['REV_AJUSTE'] = np.select(
        [(generales_ajustes1['AJUSTAR?'] == "Ajustado Póliza") & (generales_ajustes1['CDTIPO_FUENTE'].isin(provision)) & (generales_ajustes1['PTCOMISION'].between(desde_no_ajuste, hasta_no_ajuste, inclusive='both'))], 
        ["NO"],
        default="SI"
    )
    generales_rev_ajustes1 = generales_ajustes1.loc[generales_ajustes1['REV_AJUSTE'] == "NO"]
    generales_rev_ajustes1 = generales_rev_ajustes1.groupby(['NMPOLIZA', 'REV_AJUSTE'])['REV_AJUSTE'].count().reset_index(name='CUENTA_REV_AJUSTE')
    generales_rev_ajustes1 = generales_rev_ajustes1.drop('CUENTA_REV_AJUSTE', axis=1)
    generales_ajustes1 = generales_ajustes1.drop('REV_AJUSTE', axis=1)
    generales_ajustes1 = generales_ajustes1.merge(generales_rev_ajustes1, on=['NMPOLIZA'], how='left')

    # Quitar marca de ajuste a las pólizas que tienen registros con valores "pequeños"
    generales_ajustes1['AJUSTAR?'] = np.select(
        [(generales_ajustes1['AJUSTAR?'] == "Ajustado Póliza") & (generales_ajustes1['REV_AJUSTE'] == "NO")],
        [""],
        default=generales_ajustes1['AJUSTAR?']
    )
    generales_ajustes1 = generales_ajustes1.drop('REV_AJUSTE', axis=1)

    # Separación de registros que se ajustan y los que quedan para revisión
    generales_ajustados1 = generales_ajustes1.loc[generales_ajustes1['AJUSTAR?'] == "Ajustado Póliza"]
    generales_revision1 = generales_ajustes1.loc[generales_ajustes1['AJUSTAR?'] != "Ajustado Póliza"]

    ## Identificación de registros para ajustes financieros por póliza/recibo

    generales_revision1 = generales_revision1.drop('AJUSTAR?', axis=1)

    # Agrupar por póliza/recibo para determinar su valor y marcar las que tienen valor apto para ajuste
    generales_ajustes2_temp = generales_revision1.groupby(['NMPOLIZA', 'NMRECIBO'])['PTCOMISION'].sum().reset_index()
    generales_ajustes2_temp['AJUSTAR?'] = np.select(
        [((generales_ajustes2_temp['PTCOMISION'].between(hasta_negativo, desde_negativo, inclusive='both')) | 
        (generales_ajustes2_temp['PTCOMISION'].between(desde_positivo, hasta_positivo, inclusive='both')))],
        ["Ajustado Póliza/Recibo"],
        default=""
    )
    generales_ajustes2_temp = generales_ajustes2_temp.drop('PTCOMISION', axis=1)

    # Cruce de tabla agrupada con la completa para identificar registros que se deben ajustar
    generales_ajustes2 = generales_revision1.merge(generales_ajustes2_temp, on=['NMPOLIZA', 'NMRECIBO'], how='left')

    # Identificar cuales registros que se marcaron como Ajuste no aplican realmente
    generales_ajustes2['REV_AJUSTE'] = np.select(
        [(generales_ajustes2['AJUSTAR?'] == "Ajustado Póliza/Recibo") & (generales_ajustes2['PTCOMISION'].between(desde_no_ajuste, hasta_no_ajuste, inclusive='both'))], 
        ["NO"],
        default="SI"
    )
    generales_rev_ajustes2 = generales_ajustes2.loc[generales_ajustes2['REV_AJUSTE'] == "NO"]
    generales_rev_ajustes2 = generales_rev_ajustes2.groupby(['NMPOLIZA', 'NMRECIBO', 'REV_AJUSTE'])['REV_AJUSTE'].count().reset_index(name='CUENTA_REV_AJUSTE')
    generales_rev_ajustes2 = generales_rev_ajustes2.drop('CUENTA_REV_AJUSTE', axis=1)
    generales_ajustes2 = generales_ajustes2.drop('REV_AJUSTE', axis=1)
    generales_ajustes2 = generales_ajustes2.merge(generales_rev_ajustes2, on=['NMPOLIZA', 'NMRECIBO'], how='left')

    # Quitar marca de ajuste a las pólizas que tienen registros con valores "pequeños"
    generales_ajustes2['AJUSTAR?'] = np.select(
        [(generales_ajustes2['AJUSTAR?'] == "Ajustado Póliza/Recibo") & (generales_ajustes2['REV_AJUSTE'] == "NO")],
        [""],
        default=generales_ajustes2['AJUSTAR?']
    )
    generales_ajustes2 = generales_ajustes2.drop('REV_AJUSTE', axis=1)

    # Separación de registros que se ajustan y los que quedan para revisión
    generales_ajustados2 = generales_ajustes2.loc[generales_ajustes2['AJUSTAR?'] == "Ajustado Póliza/Recibo"]
    generales_revision2 = generales_ajustes2.loc[generales_ajustes2['AJUSTAR?'] != "Ajustado Póliza/Recibo"]

    ## Identificación de registros para ajustes financieros por póliza/agente

    generales_revision2 = generales_revision2.drop('AJUSTAR?', axis=1)

    # Agrupar por póliza/agente para determinar su valor y marcar las que tienen valor apto para ajuste
    generales_ajustes3_temp = generales_revision2.groupby(['NMPOLIZA', 'CDAGENTE'])['PTCOMISION'].sum().reset_index()
    generales_ajustes3_temp['AJUSTAR?'] = np.select(
        [((generales_ajustes3_temp['PTCOMISION'].between(hasta_negativo, desde_negativo, inclusive='both')) | 
        (generales_ajustes3_temp['PTCOMISION'].between(desde_positivo, hasta_positivo, inclusive='both')))],
        ["Ajustado Póliza/Agente"],
        default=""
    )
    generales_ajustes3_temp = generales_ajustes3_temp.drop('PTCOMISION', axis=1)

    # Cruce de tabla agrupada con la completa para identificar registros que se deben ajustar
    generales_ajustes3 = generales_revision2.merge(generales_ajustes3_temp, on=['NMPOLIZA', 'CDAGENTE'], how='left')

    # Identificar cuales registros que se marcaron como Ajuste no aplican realmente
    generales_ajustes3['REV_AJUSTE'] = np.select(
        [(generales_ajustes3['AJUSTAR?'] == "Ajustado Póliza/Agente") & (generales_ajustes3['PTCOMISION'].between(desde_no_ajuste, hasta_no_ajuste, inclusive='both'))], 
        ["NO"],
        default="SI"
    )
    generales_rev_ajustes3 = generales_ajustes3.loc[generales_ajustes3['REV_AJUSTE'] == "NO"]
    generales_rev_ajustes3 = generales_rev_ajustes3.groupby(['NMPOLIZA', 'CDAGENTE', 'REV_AJUSTE'])['REV_AJUSTE'].count().reset_index(name='CUENTA_REV_AJUSTE')
    generales_rev_ajustes3 = generales_rev_ajustes3.drop('CUENTA_REV_AJUSTE', axis=1)
    generales_ajustes3 = generales_ajustes3.drop('REV_AJUSTE', axis=1)
    generales_ajustes3 = generales_ajustes3.merge(generales_rev_ajustes3, on=['NMPOLIZA', 'CDAGENTE'], how='left')

    # Quitar marca de ajuste a las pólizas que tienen registros con valores "pequeños"
    generales_ajustes3['AJUSTAR?'] = np.select(
        [(generales_ajustes3['AJUSTAR?'] == "Ajustado Póliza/Agente") & (generales_ajustes3['REV_AJUSTE'] == "NO")],
        [""],
        default=generales_ajustes3['AJUSTAR?']
    )
    generales_ajustes3 = generales_ajustes3.drop('REV_AJUSTE', axis=1)

    # Separación de registros que se ajustan y los que quedan para revisión
    generales_ajustados3 = generales_ajustes3.loc[generales_ajustes3['AJUSTAR?'] == "Ajustado Póliza/Agente"]
    generales_revision3 = generales_ajustes3.loc[generales_ajustes3['AJUSTAR?'] != "Ajustado Póliza/Agente"]

    ## Identificación de registros para ajustes por recibo duplicado

    # Identificar los recibos que se encuentran en pólizas distintas
    recibos_duplicados = generales_revision3.groupby(['NMPOLIZA', 'NMRECIBO'])['PTCOMISION'].sum().reset_index()
    recibos_duplicados['NMRECIBO_DUPLICADO'] = recibos_duplicados.duplicated(subset=['NMRECIBO'], keep=False)
    recibos_duplicados = recibos_duplicados.sort_values(by=['NMRECIBO'], ascending=[True])
    recibos_duplicados['OBSERVACION'] = np.select(
        [recibos_duplicados['NMRECIBO_DUPLICADO'] == True],
        ["Recibo Duplicado"],
        default=""
    )
    recibos_duplicados = recibos_duplicados.loc[recibos_duplicados['OBSERVACION'] == "Recibo Duplicado"]

    # Agrupar por recibos duplicados para determinar su valor y marcar las que tienen valor apto para ajuste (Tolerancia definida en parametros iniciales)
    generales_revision3 = generales_revision3.drop('AJUSTAR?', axis=1)

    generales_ajustes4_temp = recibos_duplicados.groupby(['NMRECIBO', 'OBSERVACION'])['PTCOMISION'].sum().reset_index()
    generales_ajustes4_temp['AJUSTAR?'] = np.select(
        [generales_ajustes4_temp['PTCOMISION'].between(desde, hasta, inclusive='both')],
        ["Ajustado Recibo Duplicado"],
        default=""
    )
    generales_ajustes4_temp = generales_ajustes4_temp.drop('PTCOMISION', axis=1)

    # Cruce de tabla agrupada con la completa para identificar registros que se deben ajustar
    generales_ajustes4 = generales_revision3.merge(generales_ajustes4_temp, on=['NMRECIBO'], how='left')

    # Separación de registros que se ajustan y los que quedan para revisión
    generales_ajustados4 = generales_ajustes4.loc[generales_ajustes4['AJUSTAR?'] == "Ajustado Recibo Duplicado"]
    generales_revision4 = generales_ajustes4.loc[generales_ajustes4['AJUSTAR?'] != "Ajustado Recibo Duplicado"]

    print("Ajustes financieros identificados.")

    return generales_ajustados1,generales_ajustados2,generales_ajustados3,generales_ajustados4,generales_revision1,generales_revision2,generales_revision3,generales_revision4