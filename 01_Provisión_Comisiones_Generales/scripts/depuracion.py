import numpy as np

# Función para depuración de tablas
def depuracion(generales,desde,hasta):
    ## Eliminación de Pólizas con valor 0 (Tolerancia definida en parametros iniciales)

    # Agrupar por póliza para determinar su valor y marcar las que tienen valor 0
    generales_depurada1 = generales.groupby('NMPOLIZA')['PTCOMISION'].sum().reset_index()
    generales_depurada1['ELIMINAR?'] = np.select(
        [generales_depurada1['PTCOMISION'].between(desde, hasta, inclusive='both')],
        ["X"],
        default=""
    )
    generales_depurada1 = generales_depurada1.drop('PTCOMISION', axis=1)

    # Cruce de tabla agrupada con la completa para eliminar los registros de las pólizas con valor 0
    generales = generales.merge(generales_depurada1, on='NMPOLIZA', how='left')
    generales = generales.loc[generales['ELIMINAR?'] != "X"]
    generales = generales.drop('ELIMINAR?', axis=1)

    ## Eliminación de Pólizas/Recibo con valor 0 (Tolerancia definida en parametros iniciales)

    # Agrupar por póliza/recibo para determinar su valor y marcar las que tienen valor 0
    generales_depurada2 = generales[(generales['NMRECIBO'] != "99999999") | (generales['NMRECIBO'] != "9999999") | (generales['NMRECIBO'] != "999999") | (generales['CDCOASEGURO']) != "M"]
    generales_depurada2 = generales_depurada2.groupby(['NMPOLIZA','NMRECIBO'])['PTCOMISION'].sum().reset_index()
    generales_depurada2['ELIMINAR?'] = np.select(
        [generales_depurada2['PTCOMISION'].between(desde, hasta, inclusive='both')],
        ["X"],
        default=""
    )
    generales_depurada2 = generales_depurada2.drop('PTCOMISION', axis=1)

    # Cruce de tabla agrupada con la completa para eliminar los registros de las pólizas/recibo con valor 0
    generales = generales.merge(generales_depurada2, on=['NMPOLIZA','NMRECIBO'], how='left')
    generales = generales.loc[generales['ELIMINAR?'] != "X"]
    generales = generales.drop('ELIMINAR?', axis=1)

    ## Eliminación de Pólizas/Agente con valor 0 (Tolerancia definida en parametros iniciales)

    # Agrupar por póliza/agente para determinar su valor y marcar las que tienen valor 0
    generales_depurada3 = generales[(generales['NMRECIBO'] != "99999999") | (generales['NMRECIBO'] != "9999999") | (generales['NMRECIBO'] != "999999") | (generales['CDCOASEGURO']) != "M"]
    generales_depurada3 = generales_depurada3.groupby(['NMPOLIZA','CDAGENTE'])['PTCOMISION'].sum().reset_index()
    generales_depurada3['ELIMINAR?'] = np.select(
        [generales_depurada3['PTCOMISION'].between(desde, hasta, inclusive='both')],
        ["X"],
        default=""
    )
    generales_depurada3 = generales_depurada3.drop('PTCOMISION', axis=1)

    # Cruce de tabla agrupada con la completa para eliminar los registros de las pólizas/agente con valor 0
    generales = generales.merge(generales_depurada3, on=['NMPOLIZA','CDAGENTE'], how='left')
    generales = generales.loc[generales['ELIMINAR?'] != "X"]
    generales = generales.drop('ELIMINAR?', axis=1)

    ## Eliminación de Pólizas por código coaseguro con valor 0 (Tolerancia definida en parametros iniciales)

    # Agrupar por código coaseguro para determinar su valor y marcar las que tienen valor 0
    generales_depurada4 = generales.loc[generales['CDCOASEGURO'] == "M"]
    generales_depurada4 = generales_depurada4.groupby(['NMPOLIZA','CDCOASEGURO','FEREGISTRO'])['PTCOMISION'].sum().reset_index()
    generales_depurada4['ELIMINAR?'] = np.select(
        [generales_depurada4['PTCOMISION'].between(desde, hasta, inclusive='both')],
        ["X"],
        default=""
    )
    generales_depurada4 = generales_depurada4.drop('PTCOMISION', axis=1)

    # Cruce de tabla agrupada con la completa para eliminar los registros de las pólizas/agente con valor 0
    generales = generales.merge(generales_depurada4, on=['NMPOLIZA','CDCOASEGURO','FEREGISTRO'], how='left')
    generales = generales.loc[generales['ELIMINAR?'] != "X"]
    generales = generales.drop('ELIMINAR?', axis=1)

    ## Eliminación de Pólizas/Recibo con valor 0 (Tolerancia definida en parametros iniciales)

    # Agrupar por póliza/recibo para determinar su valor y marcar las que tienen valor 0
    generales_depurada5 = generales[(generales['NMRECIBO'] != "99999999") | (generales['NMRECIBO'] != "9999999") | (generales['NMRECIBO'] != "999999") | (generales['CDCOASEGURO']) != "M"]
    generales_depurada5 = generales_depurada5.groupby(['NMPOLIZA','NMRECIBO'])['PTCOMISION'].sum().reset_index()
    generales_depurada5['ELIMINAR?'] = np.select(
        [generales_depurada5['PTCOMISION'].between(desde, hasta, inclusive='both')],
        ["X"],
        default=""
    )
    generales_depurada5 = generales_depurada5.drop('PTCOMISION', axis=1)

    # Cruce de tabla agrupada con la completa para eliminar los registros de las pólizas/recibo con valor 0
    generales = generales.merge(generales_depurada5, on=['NMPOLIZA','NMRECIBO'], how='left')
    generales = generales.loc[generales['ELIMINAR?'] != "X"]
    generales = generales.drop('ELIMINAR?', axis=1)

    ## Eliminación de Pólizas con valor 0 (Tolerancia definida en parametros iniciales)

    # Agrupar por póliza para determinar su valor y marcar las que tienen valor 0
    generales_depurada6 = generales.groupby('NMPOLIZA')['PTCOMISION'].sum().reset_index()
    generales_depurada6['ELIMINAR?'] = np.select(
        [generales_depurada6['PTCOMISION'].between(desde, hasta, inclusive='both')],
        ["X"],
        default=""
    )
    generales_depurada6 = generales_depurada6.drop('PTCOMISION', axis=1)

    # Cruce de tabla agrupada con la completa para eliminar los registros de las pólizas con valor 0
    generales = generales.merge(generales_depurada6, on='NMPOLIZA', how='left')
    generales = generales.loc[generales['ELIMINAR?'] != "X"]
    generales = generales.drop('ELIMINAR?', axis=1)

    print("Depuraciones realizadas.")

    return generales