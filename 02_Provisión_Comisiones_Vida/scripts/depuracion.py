import numpy as np

# Función para depuración de tablas
def depuracion(vida,desde,hasta,provision):
    ## Eliminación de Pólizas con valor 0 (Tolerancia definida en parametros iniciales)

    # Agrupar por póliza para determinar su valor y marcar las que tienen valor 0
    vida_depurada1 = vida.groupby('NMPOLIZA')['PTCOMISION'].sum().reset_index()
    vida_depurada1['ELIMINAR?'] = np.select(
        [vida_depurada1['PTCOMISION'].between(desde, hasta, inclusive='both')],
        ["X"],
        default=""
    )
    vida_depurada1 = vida_depurada1.drop('PTCOMISION', axis=1)

    # Cruce de tabla agrupada con la completa para eliminar los registros de las pólizas con valor 0
    vida = vida.merge(vida_depurada1, on='NMPOLIZA', how='left')
    vida = vida.loc[vida['ELIMINAR?'] != "X"]
    vida = vida.drop('ELIMINAR?', axis=1)

    ## Eliminación de Pólizas/Recibo con valor 0 (Tolerancia definida en parametros iniciales)

    # Agrupar por póliza/recibo para determinar su valor y marcar las que tienen valor 0
    vida_depurada2 = vida[(vida['NMRECIBO'] != "99999999") | (vida['NMRECIBO'] != "9999999") | (vida['NMRECIBO'] != "999999") | (vida['CDCOASEGURO']) != "M"]
    vida_depurada2 = vida_depurada2.groupby(['NMPOLIZA','NMRECIBO'])['PTCOMISION'].sum().reset_index()
    vida_depurada2['ELIMINAR?'] = np.select(
        [vida_depurada2['PTCOMISION'].between(desde, hasta, inclusive='both')],
        ["X"],
        default=""
    )
    vida_depurada2 = vida_depurada2.drop('PTCOMISION', axis=1)

    # Cruce de tabla agrupada con la completa para eliminar los registros de las pólizas/recibo con valor 0
    vida = vida.merge(vida_depurada2, on=['NMPOLIZA','NMRECIBO'], how='left')
    vida = vida.loc[vida['ELIMINAR?'] != "X"]
    vida = vida.drop('ELIMINAR?', axis=1)

    ## Eliminación de Pólizas/Agente con valor 0 (Tolerancia definida en parametros iniciales)

    # Agrupar por póliza/agente para determinar su valor y marcar las que tienen valor 0
    vida_depurada3 = vida[(vida['NMRECIBO'] != "99999999") | (vida['NMRECIBO'] != "9999999") | (vida['NMRECIBO'] != "999999") | (vida['CDCOASEGURO']) != "M"]
    vida_depurada3 = vida_depurada3.groupby(['NMPOLIZA','CDAGENTE'])['PTCOMISION'].sum().reset_index()
    vida_depurada3['ELIMINAR?'] = np.select(
        [vida_depurada3['PTCOMISION'].between(desde, hasta, inclusive='both')],
        ["X"],
        default=""
    )
    vida_depurada3 = vida_depurada3.drop('PTCOMISION', axis=1)

    # Cruce de tabla agrupada con la completa para eliminar los registros de las pólizas/agente con valor 0
    vida = vida.merge(vida_depurada3, on=['NMPOLIZA','CDAGENTE'], how='left')
    vida = vida.loc[vida['ELIMINAR?'] != "X"]
    vida = vida.drop('ELIMINAR?', axis=1)

    ## Identificación de registros "Provisión" para agruparlos con sus respectivos "Pagos" y eliminar si su valor es 0 (Tolerancia definida en parametros iniciales)
                                                 
    # Marcar los registros que estén dentro de la lista de opciones de provisión
    vida['TIPO'] = np.select(
        [vida['CDTIPO_FUENTE'].isin(provision)],
        ["Provision"],
        default="Pago"
    )

    vida['OBSERVACION'] = ""

    # Se ordena el dataset por póliza y recibo 
    vida.sort_values(by=['NMPOLIZA', 'NMRECIBO', 'TIPO'], ascending=[True, True, False], inplace=True)

    # Asignación de un número único de identificación a cada provisión
    vida['PROVISION_FLAG'] = np.where(vida['TIPO'] == "Provision", 1, 0)
    vida['CDPROVISION'] = np.where(vida['PROVISION_FLAG'] == 1, vida['PROVISION_FLAG'].cumsum(), "")
    vida.drop(['PROVISION_FLAG'], axis=1, inplace=True)

    #####################################################################################################################
    Nmpoliza = ""
    Tipo = ""
    cdprovision = "" # Va a guardar el número de provisión anterior
    Aux_cdprovision = "" # Va a guardar el contenido de la línea anterior en el campo 

    for index, row in vida.iterrows():
        # Escenario primera línea
        if Nmpoliza == "" and Tipo == "":
            Nmpoliza = row['NMPOLIZA']
            Tipo = row['TIPO']
            if Tipo == "Provision":
                #print("Se ejecuto primera linea")
                cdprovision = row['CDPROVISION']
                vida.at[index, "OBSERVACION"] = ""
            else:
                vida.at[index, "OBSERVACION"] = "Pago sin Provision"
        # Escenarios para misma Nmpoliza
        elif row['NMPOLIZA'] == Nmpoliza:
            #print(f"Registro con la poliza igual al anterior;Actual {row['NMPOLIZA']}, anterior: {Nmpoliza}")
            # Más de una provisión consecutiva dentro de una misma Nmpoliza
            if row['CDPROVISION'] != "" and Tipo == "Provision":
                vida.at[index, "CDPROVISION"] = Aux_cdprovision
                vida.at[index, "OBSERVACION"] = ""

            # Cuando encuentra por primera vez una provisión despues de pagos
            # No debería pasar si se organiza cdprovision descendente
            elif row['CDPROVISION'] != "" and cdprovision == "":
                cdprovision = row['CDPROVISION']
                vida.at[index, "OBSERVACION"] = ""

            # Cuando son pagos en una misma Nmpoliza y no tienen una provisión previa
            elif cdprovision == "" and Tipo == "Pago":
                vida.at[index, "OBSERVACION"] = "Pago sin Provision"
            
            # Cuando es un pago despues de una provión
            elif row['CDPROVISION'] == "" and row['TIPO'] == "Pago":
                vida.at[index, "CDPROVISION"] = cdprovision
                vida.at[index, "OBSERVACION"] = ""
            
            # Encontro otra provisión pero el anterior registro es un pago
            elif row['TIPO'] != Tipo and row['TIPO'] == "Provision":
                cdprovision = row['CDPROVISION']
                vida.at[index, "OBSERVACION"] = ""

            # Acá solo entran los registros que no tienen codigo de provisión y son Provisiones
            else:
                #print(f"Valor tabla para CDPROVISION: {row['CDPROVISION']}, Valor tabla NMPOLIZA: {row['TIPO']}")
                vida.at[index, "OBSERVACION"] = "Revisar"
                
        elif row['NMPOLIZA'] != Nmpoliza:
            #print(f"Registro con la poliza DIFERENTE al anterior;Actual {row['NMPOLIZA']}, anterior: {Nmpoliza}")
            Nmpoliza = row['NMPOLIZA']
            cdprovision = ""
            if row['TIPO'] == "Pago":
                vida.at[index, "OBSERVACION"] = "Pago sin Provision"
            elif row['TIPO'] == "Provision":
                cdprovision = row['CDPROVISION']
        
        # Variables del registro anterior
        Tipo = row['TIPO']
        Aux_cdprovision = vida.at[index, "CDPROVISION"]
    #####################################################################################################################
        
    # Quitar código de provisión a las provisiones con recibo 99999999
    vida['CDPROVISION'] = np.where((vida['NMRECIBO'].fillna("") == "99999999") | (vida['NMRECIBO'].fillna("") == "999999"),"",vida['CDPROVISION'])

    # Edición columna Observación para marcar polizas 99999999 y 999999 como revisión
    #vida['OBSERVACION'] = np.where((vida['NMRECIBO'].fillna("") == "99999999") | (vida['NMRECIBO'].fillna("") == "999999"),"Revisar",vida['OBSERVACION'])

    # Agrupar pólizas por código de provisión para determinar su valor y marcar las que tienen valor 0 
    vida_depurada4 = vida.groupby('CDPROVISION').agg({'PTCOMISION': 'sum'}).reset_index()

    vida_depurada4['ELIMINAR?'] = np.select(
        [vida_depurada4['PTCOMISION'].between(desde, hasta, inclusive='both')],
        ["X"],
        default=""
    )
    vida_depurada4 = vida_depurada4.drop('PTCOMISION', axis=1)

    # Cruce de tabla agrupada con la completa para eliminar los registros de las pólizas por código de provisión con valor 0
    vida = vida.merge(vida_depurada4, on=['CDPROVISION'], how='left')
    vida = vida.loc[vida['ELIMINAR?'] != "X"]
    vida = vida.drop('ELIMINAR?', axis=1)

    ## Eliminación de Pólizas por código coaseguro con valor 0 (Tolerancia definida en parametros iniciales)

    # Agrupar por código coaseguro para determinar su valor y marcar las que tienen valor 0
    vida_depurada5 = vida.loc[vida['CDCOASEGURO'] == "M"]
    vida_depurada5 = vida_depurada5.groupby(['NMPOLIZA','CDCOASEGURO','CDAGENTE','FEREGISTRO'])['PTCOMISION'].sum().reset_index()
    vida_depurada5['ELIMINAR?'] = np.select(
        [vida_depurada5['PTCOMISION'].between(desde, hasta, inclusive='both')],
        ["X"],
        default=""
    )
    vida_depurada5 = vida_depurada5.drop('PTCOMISION', axis=1)

    # Cruce de tabla agrupada con la completa para eliminar los registros de las pólizas/agente con valor 0
    vida = vida.merge(vida_depurada5, on=['NMPOLIZA','CDCOASEGURO','CDAGENTE','FEREGISTRO'], how='left')
    vida = vida.loc[vida['ELIMINAR?'] != "X"]
    vida = vida.drop('ELIMINAR?', axis=1)

    ## Eliminación de Pólizas/Recibo con valor 0 (Tolerancia definida en parametros iniciales)

    # Agrupar por póliza/recibo para determinar su valor y marcar las que tienen valor 0
    vida_depurada6 = vida[(vida['NMRECIBO'] != "99999999") | (vida['NMRECIBO'] != "9999999") | (vida['NMRECIBO'] != "999999") | (vida['CDCOASEGURO']) != "M"]
    vida_depurada6 = vida_depurada6.groupby(['NMPOLIZA','NMRECIBO'])['PTCOMISION'].sum().reset_index()
    vida_depurada6['ELIMINAR?'] = np.select(
        [vida_depurada6['PTCOMISION'].between(desde, hasta, inclusive='both')],
        ["X"],
        default=""
    )
    vida_depurada6 = vida_depurada6.drop('PTCOMISION', axis=1)

    # Cruce de tabla agrupada con la completa para eliminar los registros de las pólizas/recibo con valor 0
    vida = vida.merge(vida_depurada6, on=['NMPOLIZA','NMRECIBO'], how='left')
    vida = vida.loc[vida['ELIMINAR?'] != "X"]
    vida = vida.drop('ELIMINAR?', axis=1)

    ## Eliminación de Pólizas con valor 0 (Tolerancia definida en parametros iniciales)

    # Agrupar por póliza para determinar su valor y marcar las que tienen valor 0
    vida_depurada7 = vida.groupby('NMPOLIZA')['PTCOMISION'].sum().reset_index()
    vida_depurada7['ELIMINAR?'] = np.select(
        [vida_depurada7['PTCOMISION'].between(desde, hasta, inclusive='both')],
        ["X"],
        default=""
    )
    vida_depurada7 = vida_depurada7.drop('PTCOMISION', axis=1)

    # Cruce de tabla agrupada con la completa para eliminar los registros de las pólizas con valor 0
    vida = vida.merge(vida_depurada7, on='NMPOLIZA', how='left')
    vida = vida.loc[vida['ELIMINAR?'] != "X"]
    vida = vida.drop('ELIMINAR?', axis=1)

    print("Depuraciones realizadas.")

    return vida