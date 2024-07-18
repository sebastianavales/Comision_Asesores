import numpy as np

# Función para identificar registros que se deben ajustar
def identificacion_ajustes(vida,hasta,desde,hasta_negativo,desde_negativo,hasta_positivo,desde_positivo,provision,desde_no_ajuste,hasta_no_ajuste):

    ## Identificación de registros para ajustes financieros por póliza

    # Agrupar por póliza para determinar su valor y marcar las que tienen valor apto para ajuste
    vida_ajustes1_temp = vida.groupby(['NMPOLIZA'])['PTCOMISION'].sum().reset_index()
    vida_ajustes1_temp['AJUSTAR?'] = np.select(
        [((vida_ajustes1_temp['PTCOMISION'].between(hasta_negativo, desde_negativo, inclusive='both')) | 
        (vida_ajustes1_temp['PTCOMISION'].between(desde_positivo, hasta_positivo, inclusive='both')))],
        ["Ajustado Póliza"],
        default=""
    )
    vida_ajustes1_temp = vida_ajustes1_temp.drop('PTCOMISION', axis=1)

    # Cruce de tabla agrupada con la completa para identificar registros que se deben ajustar
    vida_ajustes1 = vida.merge(vida_ajustes1_temp, on=['NMPOLIZA'], how='left')

    # Identificar cuales registros que se marcaron como Ajuste no aplican realmente
    vida_ajustes1['REV_AJUSTE'] = np.select(
        [(vida_ajustes1['AJUSTAR?'] == "Ajustado Póliza") & (vida_ajustes1['CDTIPO_FUENTE'].isin(provision)) & (vida_ajustes1['PTCOMISION'].between(desde_no_ajuste, hasta_no_ajuste, inclusive='both'))], 
        ["NO"],
        default="SI"
    )
    vida_rev_ajustes1 = vida_ajustes1.loc[vida_ajustes1['REV_AJUSTE'] == "NO"]
    vida_rev_ajustes1 = vida_rev_ajustes1.groupby(['NMPOLIZA', 'REV_AJUSTE'])['REV_AJUSTE'].count().reset_index(name='CUENTA_REV_AJUSTE')
    vida_rev_ajustes1 = vida_rev_ajustes1.drop('CUENTA_REV_AJUSTE', axis=1)
    vida_ajustes1 = vida_ajustes1.drop('REV_AJUSTE', axis=1)
    vida_ajustes1 = vida_ajustes1.merge(vida_rev_ajustes1, on=['NMPOLIZA'], how='left')

    # Quitar marca de ajuste a las pólizas que tienen registros con valores "pequeños"
    vida_ajustes1['AJUSTAR?'] = np.select(
        [(vida_ajustes1['AJUSTAR?'] == "Ajustado Póliza") & (vida_ajustes1['REV_AJUSTE'] == "NO")],
        [""],
        default=vida_ajustes1['AJUSTAR?']
    )
    vida_ajustes1 = vida_ajustes1.drop('REV_AJUSTE', axis=1)

    # Separación de registros que se ajustan y los que quedan para revisión
    vida_ajustados1 = vida_ajustes1.loc[vida_ajustes1['AJUSTAR?'] == "Ajustado Póliza"]
    vida_revision1 = vida_ajustes1.loc[vida_ajustes1['AJUSTAR?'] != "Ajustado Póliza"]

    ## Identificación de registros para ajustes financieros por póliza/recibo

    vida_revision1 = vida_revision1.drop('AJUSTAR?', axis=1)

    # Agrupar por póliza/recibo para determinar su valor y marcar las que tienen valor apto para ajuste
    vida_ajustes2_temp = vida_revision1.groupby(['NMPOLIZA', 'NMRECIBO'])['PTCOMISION'].sum().reset_index()
    vida_ajustes2_temp['AJUSTAR?'] = np.select(
        [((vida_ajustes2_temp['PTCOMISION'].between(hasta_negativo, desde_negativo, inclusive='both')) | 
        (vida_ajustes2_temp['PTCOMISION'].between(desde_positivo, hasta_positivo, inclusive='both')))],
        ["Ajustado Póliza/Recibo"],
        default=""
    )
    vida_ajustes2_temp = vida_ajustes2_temp.drop('PTCOMISION', axis=1)

    # Cruce de tabla agrupada con la completa para identificar registros que se deben ajustar
    vida_ajustes2 = vida_revision1.merge(vida_ajustes2_temp, on=['NMPOLIZA', 'NMRECIBO'], how='left')

    # Identificar cuales registros que se marcaron como Ajuste no aplican realmente
    vida_ajustes2['REV_AJUSTE'] = np.select(
        [(vida_ajustes2['AJUSTAR?'] == "Ajustado Póliza/Recibo") & (vida_ajustes2['PTCOMISION'].between(desde_no_ajuste, hasta_no_ajuste, inclusive='both'))], 
        ["NO"],
        default="SI"
    )
    vida_rev_ajustes2 = vida_ajustes2.loc[vida_ajustes2['REV_AJUSTE'] == "NO"]
    vida_rev_ajustes2 = vida_rev_ajustes2.groupby(['NMPOLIZA', 'NMRECIBO', 'REV_AJUSTE'])['REV_AJUSTE'].count().reset_index(name='CUENTA_REV_AJUSTE')
    vida_rev_ajustes2 = vida_rev_ajustes2.drop('CUENTA_REV_AJUSTE', axis=1)
    vida_ajustes2 = vida_ajustes2.drop('REV_AJUSTE', axis=1)
    vida_ajustes2 = vida_ajustes2.merge(vida_rev_ajustes2, on=['NMPOLIZA', 'NMRECIBO'], how='left')

    # Quitar marca de ajuste a las pólizas que tienen registros con valores "pequeños"
    vida_ajustes2['AJUSTAR?'] = np.select(
        [(vida_ajustes2['AJUSTAR?'] == "Ajustado Póliza/Recibo") & (vida_ajustes2['REV_AJUSTE'] == "NO")],
        [""],
        default=vida_ajustes2['AJUSTAR?']
    )
    vida_ajustes2 = vida_ajustes2.drop('REV_AJUSTE', axis=1)

    # Separación de registros que se ajustan y los que quedan para revisión
    vida_ajustados2 = vida_ajustes2.loc[vida_ajustes2['AJUSTAR?'] == "Ajustado Póliza/Recibo"]
    vida_revision2 = vida_ajustes2.loc[vida_ajustes2['AJUSTAR?'] != "Ajustado Póliza/Recibo"]

    ## Identificación de registros para ajustes financieros por póliza/agente

    vida_revision2 = vida_revision2.drop('AJUSTAR?', axis=1)

    # Agrupar por póliza/agente para determinar su valor y marcar las que tienen valor apto para ajuste
    vida_ajustes3_temp = vida_revision2.groupby(['NMPOLIZA', 'CDAGENTE'])['PTCOMISION'].sum().reset_index()
    vida_ajustes3_temp['AJUSTAR?'] = np.select(
        [((vida_ajustes3_temp['PTCOMISION'].between(hasta_negativo, desde_negativo, inclusive='both')) | 
        (vida_ajustes3_temp['PTCOMISION'].between(desde_positivo, hasta_positivo, inclusive='both')))],
        ["Ajustado Póliza/Agente"],
        default=""
    )
    vida_ajustes3_temp = vida_ajustes3_temp.drop('PTCOMISION', axis=1)

    # Cruce de tabla agrupada con la completa para identificar registros que se deben ajustar
    vida_ajustes3 = vida_revision2.merge(vida_ajustes3_temp, on=['NMPOLIZA', 'CDAGENTE'], how='left')

    # Identificar cuales registros que se marcaron como Ajuste no aplican realmente
    vida_ajustes3['REV_AJUSTE'] = np.select(
        [(vida_ajustes3['AJUSTAR?'] == "Ajustado Póliza/Agente") & (vida_ajustes3['PTCOMISION'].between(desde_no_ajuste, hasta_no_ajuste, inclusive='both'))], 
        ["NO"],
        default="SI"
    )
    vida_rev_ajustes3 = vida_ajustes3.loc[vida_ajustes3['REV_AJUSTE'] == "NO"]
    vida_rev_ajustes3 = vida_rev_ajustes3.groupby(['NMPOLIZA', 'CDAGENTE', 'REV_AJUSTE'])['REV_AJUSTE'].count().reset_index(name='CUENTA_REV_AJUSTE')
    vida_rev_ajustes3 = vida_rev_ajustes3.drop('CUENTA_REV_AJUSTE', axis=1)
    vida_ajustes3 = vida_ajustes3.drop('REV_AJUSTE', axis=1)
    vida_ajustes3 = vida_ajustes3.merge(vida_rev_ajustes3, on=['NMPOLIZA', 'CDAGENTE'], how='left')

    # Quitar marca de ajuste a las pólizas que tienen registros con valores "pequeños"
    vida_ajustes3['AJUSTAR?'] = np.select(
        [(vida_ajustes3['AJUSTAR?'] == "Ajustado Póliza/Agente") & (vida_ajustes3['REV_AJUSTE'] == "NO")],
        [""],
        default=vida_ajustes3['AJUSTAR?']
    )
    vida_ajustes3 = vida_ajustes3.drop('REV_AJUSTE', axis=1)

    # Separación de registros que se ajustan y los que quedan para revisión
    vida_ajustados3 = vida_ajustes3.loc[vida_ajustes3['AJUSTAR?'] == "Ajustado Póliza/Agente"]
    vida_revision3 = vida_ajustes3.loc[vida_ajustes3['AJUSTAR?'] != "Ajustado Póliza/Agente"]

    ## Identificación de registros para ajustes financieros por código de agrupación

    vida_revision3 = vida_revision3.drop('AJUSTAR?', axis=1)

    # Agrupar por código de agrupación para determinar su valor y marcar las que tienen valor apto para ajuste
    vida_ajustes4_temp = vida_revision3.groupby(['NMPOLIZA', 'CDPROVISION'])['PTCOMISION'].sum().reset_index()
    vida_ajustes4_temp['AJUSTAR?'] = np.select(
        [((vida_ajustes4_temp['PTCOMISION'].between(hasta_negativo, desde_negativo, inclusive='both')) | 
        (vida_ajustes4_temp['PTCOMISION'].between(desde_positivo, hasta_positivo, inclusive='both')))],
        ["Ajustado código agrupación"],
        default=""
    )
    vida_ajustes4_temp = vida_ajustes4_temp.drop('PTCOMISION', axis=1)

    # Cruce de tabla agrupada con la completa para identificar registros que se deben ajustar
    vida_ajustes4 = vida_revision3.merge(vida_ajustes4_temp, on=['NMPOLIZA', 'CDPROVISION'], how='left')

    # Identificar cuales registros que se marcaron como Ajuste no aplican realmente
    vida_ajustes4['REV_AJUSTE'] = np.select(
        [(vida_ajustes4['AJUSTAR?'] == "Ajustado código agrupación") & (vida_ajustes4['PTCOMISION'].between(desde_no_ajuste, hasta_no_ajuste, inclusive='both'))], 
        ["NO"],
        default="SI"
    )
    vida_rev_ajustes4 = vida_ajustes4.loc[vida_ajustes4['REV_AJUSTE'] == "NO"]
    vida_rev_ajustes4 = vida_rev_ajustes4.groupby(['NMPOLIZA', 'CDPROVISION', 'REV_AJUSTE'])['REV_AJUSTE'].count().reset_index(name='CUENTA_REV_AJUSTE')
    vida_rev_ajustes4 = vida_rev_ajustes4.drop('CUENTA_REV_AJUSTE', axis=1)
    vida_ajustes4 = vida_ajustes4.drop('REV_AJUSTE', axis=1)
    vida_ajustes4 = vida_ajustes4.merge(vida_rev_ajustes4, on=['NMPOLIZA', 'CDPROVISION'], how='left')

    # Quitar marca de ajuste a las pólizas que tienen registros con valores "pequeños"
    vida_ajustes4['AJUSTAR?'] = np.select(
        [(vida_ajustes4['AJUSTAR?'] == "Ajustado código agrupación") & (vida_ajustes4['REV_AJUSTE'] == "NO")],
        [""],
        default=vida_ajustes4['AJUSTAR?']
    )
    vida_ajustes4 = vida_ajustes4.drop('REV_AJUSTE', axis=1)

    # Separación de registros que se ajustan y los que quedan para revisión
    vida_ajustados4 = vida_ajustes4.loc[vida_ajustes4['AJUSTAR?'] == "Ajustado código agrupación"]
    vida_revision4 = vida_ajustes4.loc[vida_ajustes4['AJUSTAR?'] != "Ajustado código agrupación"]

    ## Identificación de registros para ajustes por recibo duplicado

    # Identificar los recibos que se encuentran en pólizas distintas
    recibos_duplicados = vida_revision4.groupby(['NMPOLIZA', 'NMRECIBO'])['PTCOMISION'].sum().reset_index()
    recibos_duplicados['VALIDACION_DUPLICADO'] = recibos_duplicados.duplicated(subset=['NMRECIBO'], keep=False)
    recibos_duplicados = recibos_duplicados.sort_values(by=['NMRECIBO'], ascending=[True])
    recibos_duplicados['NMRECIBO_DUPLICADO'] = np.select(
        [recibos_duplicados['VALIDACION_DUPLICADO'] == True],
        ["Recibo Duplicado"],
        default=""
    )
    recibos_duplicados = recibos_duplicados.loc[recibos_duplicados['NMRECIBO_DUPLICADO'] == "Recibo Duplicado"]

    # Agrupar por recibos duplicados para determinar su valor y marcar las que tienen valor apto para ajuste (Tolerancia definida en parametros iniciales)
    vida_revision4 = vida_revision4.drop('AJUSTAR?', axis=1)

    vida_ajustes5_temp = recibos_duplicados.groupby(['NMRECIBO', 'NMRECIBO_DUPLICADO'])['PTCOMISION'].sum().reset_index()
    vida_ajustes5_temp['AJUSTAR?'] = np.select(
        [vida_ajustes5_temp['PTCOMISION'].between(desde, hasta, inclusive='both')],
        ["Ajustado Recibo Duplicado"],
        default=""
    )
    vida_ajustes5_temp = vida_ajustes5_temp.drop('PTCOMISION', axis=1)

    # Cruce de tabla agrupada con la completa para identificar registros que se deben ajustar
    vida_ajustes5 = vida_revision4.merge(vida_ajustes5_temp, on=['NMRECIBO'], how='left')
    vida_ajustes5['OBSERVACION'] = np.select(
        [vida_ajustes5['NMRECIBO_DUPLICADO'] == "Recibo Duplicado"],
        ["Recibo Duplicado"],
        default=vida_ajustes5['OBSERVACION']
    )
    vida_ajustes5 = vida_ajustes5.drop('NMRECIBO_DUPLICADO', axis=1)

    # Separación de registros que se ajustan y los que quedan para revisión
    vida_ajustados5 = vida_ajustes5.loc[vida_ajustes5['AJUSTAR?'] == "Ajustado Recibo Duplicado"]
    vida_revision5 = vida_ajustes5.loc[vida_ajustes5['AJUSTAR?'] != "Ajustado Recibo Duplicado"]

    print("Ajustes financieros identificados.")

    return vida_ajustados1,vida_ajustados2,vida_ajustados3,vida_ajustados4,vida_ajustados5,vida_revision1,vida_revision2,vida_revision3,vida_revision4,vida_revision5