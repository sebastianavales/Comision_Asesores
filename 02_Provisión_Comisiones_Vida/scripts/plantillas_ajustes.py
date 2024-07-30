import pandas as pd
import numpy as np

# Función para generar plantillas de ajustes financieros
def plantillas_ajustes(vida_ajustes,ultimo_dia_del_mes,mes_cierre,año_cierre):
    
    # Filtrar registros para Ajustes menos por Pólizas en Dólares
    vida_plantilla_ajustes1 = vida_ajustes.loc[(vida_ajustes['AJUSTAR?'] == "Ajustado Póliza") |
                                               (vida_ajustes['AJUSTAR?'] == "Ajustado Póliza/Recibo") |
                                               (vida_ajustes['AJUSTAR?'] == "Ajustado Póliza/Agente") |
                                               (vida_ajustes['AJUSTAR?'] == "Ajustado Recibo Duplicado") |
                                               (vida_ajustes['AJUSTAR?'] == "Ajustado código agrupación")].fillna("")
    
    # Identificar la fuente del registro
    vida_plantilla_ajustes1['FUENTE'] = np.select(
        [vida_plantilla_ajustes1['CDTIPO_FUENTE'].str.contains("CORE")],
        ["GW"],
        default="CS"
    )

    vida_plantilla_ajustes1['FUENTE'] = np.select(
        [(vida_plantilla_ajustes1['FUENTE'] == "CS") & (vida_plantilla_ajustes1['NMRECIBO'].str.len() >= 9)],
        ["GW"],
        default=vida_plantilla_ajustes1['FUENTE']
    )

    # Corrección del ramo
    vida_plantilla_ajustes1['CDRAMO'] = np.select(
        [vida_plantilla_ajustes1['NMPOLIZA'].astype(str).str[:3] == "900"],
        [vida_plantilla_ajustes1['CDRAMO']],
        default=vida_plantilla_ajustes1['NMPOLIZA'].astype(str).str[:3]
    )
                                                         
    # Ajustes por Póliza
    vida_plantilla_ajustes1_1 = vida_plantilla_ajustes1.loc[(vida_plantilla_ajustes1['AJUSTAR?'] == "Ajustado Póliza")].groupby(['NMPOLIZA','CDRAMO','FUENTE'])['PTCOMISION'].sum().reset_index()
    vida_plantilla_ajustes1_1 = vida_plantilla_ajustes1_1.merge(vida_plantilla_ajustes1[['NMPOLIZA','NMRECIBO','CDAGENTE']].drop_duplicates(subset=['NMPOLIZA']), on='NMPOLIZA', how='left')
    vida_plantilla_ajustes1_1 = vida_plantilla_ajustes1_1[['NMPOLIZA','CDRAMO','NMRECIBO','CDAGENTE','FUENTE','PTCOMISION']]

    # Ajustes por código de agrupación
    vida_plantilla_ajustes1_2 = vida_plantilla_ajustes1.loc[(vida_plantilla_ajustes1['AJUSTAR?'] == "Ajustado código agrupación")].groupby(['NMPOLIZA','CDRAMO','CDPROVISION','FUENTE'])['PTCOMISION'].sum().reset_index()
    vida_plantilla_ajustes1_2 = vida_plantilla_ajustes1_2.merge(vida_plantilla_ajustes1[['NMPOLIZA','NMRECIBO','CDAGENTE','CDPROVISION']].drop_duplicates(subset=['NMPOLIZA','CDPROVISION']), on=['NMPOLIZA','CDPROVISION'], how='left')
    vida_plantilla_ajustes1_2 = vida_plantilla_ajustes1_2[['NMPOLIZA','CDRAMO','NMRECIBO','CDAGENTE','FUENTE','PTCOMISION']]

    # Ajustes de los demás tipos
    vida_plantilla_ajustes1_3 = vida_plantilla_ajustes1.loc[(vida_plantilla_ajustes1['AJUSTAR?'] == "Ajustado Póliza/Recibo") |
                                                            (vida_plantilla_ajustes1['AJUSTAR?'] == "Ajustado Póliza/Agente") |
                                                            (vida_plantilla_ajustes1['AJUSTAR?'] == "Ajustado Recibo Duplicado")].groupby(['NMPOLIZA','CDRAMO','NMRECIBO','CDAGENTE','FUENTE'])['PTCOMISION'].sum().reset_index()

    # Concatenar dataframes de ajustes (menos por póliza y pólizas en dólares)
    vida_plantilla_ajustes1_40 = pd.concat([vida_plantilla_ajustes1_1,vida_plantilla_ajustes1_2,vida_plantilla_ajustes1_3], axis=0)

    vida_plantilla_ajustes1_40 = vida_plantilla_ajustes1_40.sort_values(by=['NMPOLIZA', 'NMRECIBO'], ascending=[True, True])

    # Parametros para clave de contabilización 40
    vida_plantilla_ajustes1_40['Agrupador'] = 1
    vida_plantilla_ajustes1_40['Agrupador'] = vida_plantilla_ajustes1_40['Agrupador'].cumsum()
    vida_plantilla_ajustes1_40['Fecha de Documento'] = ultimo_dia_del_mes
    vida_plantilla_ajustes1_40['Clase de Documento'] = "SR"
    vida_plantilla_ajustes1_40['Sociedad'] = "2000"
    vida_plantilla_ajustes1_40['Fecha Contabilización'] = ultimo_dia_del_mes
    vida_plantilla_ajustes1_40['Período'] = ultimo_dia_del_mes[2:4]
    vida_plantilla_ajustes1_40['Clave de Moneda'] = "COP"
    vida_plantilla_ajustes1_40['Tipo de Cambio'] = ""
    vida_plantilla_ajustes1_40['Fe.conversión '] = ""
    vida_plantilla_ajustes1_40['Número documento de referencia'] = vida_plantilla_ajustes1_40['NMRECIBO']
    vida_plantilla_ajustes1_40['Texto de Cebecera'] = "AJUSTE PROVISION"
    vida_plantilla_ajustes1_40['Calc. Impuestos '] = ""
    vida_plantilla_ajustes1_40['Clave de contabilización para la siguiente posición'] = 40
    vida_plantilla_ajustes1_40['Número de identificación fiscal 1'] = ""
    vida_plantilla_ajustes1_40['Tipo de número de identificación fiscal'] = ""
    vida_plantilla_ajustes1_40['In. CME'] = ""
    vida_plantilla_ajustes1_40['Cuenta de mayor de la contabilidad principal'] = np.select(
        [(vida_plantilla_ajustes1_40['PTCOMISION'] > 0) & (vida_plantilla_ajustes1_40['FUENTE'] == "GW"),
        (vida_plantilla_ajustes1_40['PTCOMISION'] < 0) & (vida_plantilla_ajustes1_40['FUENTE'] == "GW"),
        (vida_plantilla_ajustes1_40['PTCOMISION'] > 0) & (vida_plantilla_ajustes1_40['FUENTE'] == "CS"),
        (vida_plantilla_ajustes1_40['PTCOMISION'] < 0) & (vida_plantilla_ajustes1_40['FUENTE'] == "CS")],
        ["2481010040",
        "5209101010",
        "2481010000",
        "5209101000"],
        default="Revisar"
    )
    vida_plantilla_ajustes1_40['Importe en la moneda del documento'] = abs(vida_plantilla_ajustes1_40['PTCOMISION'].round(0)).astype(int)
    vida_plantilla_ajustes1_40['Indicador IVA'] = ""
    vida_plantilla_ajustes1_40['Indicador retefuente WT_WITHCD'] = ""
    vida_plantilla_ajustes1_40['TP retefuente WITHT'] = ""
    vida_plantilla_ajustes1_40['indicador reteica WT_WITHCD'] = ""
    vida_plantilla_ajustes1_40['TP reteica WITHT'] = ""
    vida_plantilla_ajustes1_40['indicador reteiva WT_WITHCD'] = ""
    vida_plantilla_ajustes1_40['TP reteiva WITHT'] = ""
    vida_plantilla_ajustes1_40['indicador retetimbre WT_WITHCD'] = ""
    vida_plantilla_ajustes1_40['Tp retetimbre WITHT'] = ""
    #######################################################################
    division = vida_plantilla_ajustes1[['NMPOLIZA','NMRECIBO','CDDELEGACION']].fillna("")
    division = division.rename(columns={'CDDELEGACION':'División'})
    vida_plantilla_ajustes1_40 = vida_plantilla_ajustes1_40.merge(division,on=['NMPOLIZA','NMRECIBO'], how='left')
    vida_plantilla_ajustes1_40['Duplicado'] = vida_plantilla_ajustes1_40['Agrupador'].astype(str) + vida_plantilla_ajustes1_40['NMPOLIZA'] + vida_plantilla_ajustes1_40['NMRECIBO'].astype(str) + vida_plantilla_ajustes1_40['PTCOMISION'].astype(str) + vida_plantilla_ajustes1_40['Clave de contabilización para la siguiente posición'].astype(str)
    vida_plantilla_ajustes1_40 = vida_plantilla_ajustes1_40.drop_duplicates(subset=['Duplicado'], keep='first')
    vida_plantilla_ajustes1_40 = vida_plantilla_ajustes1_40.drop(['Duplicado'], axis=1)
    vida_plantilla_ajustes1_40['División'] = np.select(
        [(vida_plantilla_ajustes1_40['División'].str.len() < 4),
        (vida_plantilla_ajustes1_40['División'] == "0000") | (vida_plantilla_ajustes1_40['División'].str.len() > 4) | (vida_plantilla_ajustes1_40['División'].isnull())],
        [vida_plantilla_ajustes1_40['División'].str.rjust(4, "0"),
        "0099"],
        default=vida_plantilla_ajustes1_40['División']
    )
    #######################################################################
    vida_plantilla_ajustes1_40['Clave de condiciones de pago'] = ""
    vida_plantilla_ajustes1_40['Centro de coste'] = "20" + vida_plantilla_ajustes1_40['División'] + "000"
    vida_plantilla_ajustes1_40['Centro de beneficio'] = ""
    vida_plantilla_ajustes1_40['Días del descuento por pronto pago 1'] = ""
    vida_plantilla_ajustes1_40['Porcentaje de descuento por pronto pago 1'] = ""
    vida_plantilla_ajustes1_40['Días del descuento por pronto pago 2'] = ""
    vida_plantilla_ajustes1_40['Porcentaje de descuento por pronto pago 2'] = ""
    vida_plantilla_ajustes1_40['Plazo para condición de pago neto'] = ""
    vida_plantilla_ajustes1_40['Fecha Contabilización'] = ultimo_dia_del_mes
    vida_plantilla_ajustes1_40['Fecha base para cálculo del vencimiento'] = ""
    vida_plantilla_ajustes1_40['Condición de pago fija'] = ""
    vida_plantilla_ajustes1_40['Base de descuento'] = ""
    vida_plantilla_ajustes1_40['Vía de pago'] = ""
    vida_plantilla_ajustes1_40['Bloqueo pago'] = ""
    vida_plantilla_ajustes1_40['% DPP'] = ""
    vida_plantilla_ajustes1_40['Importe DPP'] = ""
    vida_plantilla_ajustes1_40['Número de asignación'] = vida_plantilla_ajustes1_40['NMRECIBO']
    vida_plantilla_ajustes1_40['Texto posición'] = "AJUSTE PROVISION"
    vida_plantilla_ajustes1_40['Número de orden'] = ""
    vida_plantilla_ajustes1_40['Clave de referencia de interlocutor comercial'] = vida_plantilla_ajustes1_40['NMPOLIZA']
    vida_plantilla_ajustes1_40['Clave de referencia de interlocutor comercial2'] = vida_plantilla_ajustes1_40['CDRAMO']  
    vida_plantilla_ajustes1_40['Clave de referencia para la posición de documento'] = vida_plantilla_ajustes1_40['CDAGENTE']
    vida_plantilla_ajustes1_40['Tipo de banco interlocutor'] = ""
    vida_plantilla_ajustes1_40['Fecha expedicion'] = ultimo_dia_del_mes[0:2] + "." + ultimo_dia_del_mes[2:4] + "." + ultimo_dia_del_mes[4:]
    vida_plantilla_ajustes1_40['Fecha fin vigencia'] = ultimo_dia_del_mes[0:2] + "." + ultimo_dia_del_mes[2:4] + "." + ultimo_dia_del_mes[4:]
    vida_plantilla_ajustes1_40['Poliza líder'] = ""
    vida_plantilla_ajustes1_40['Cert.lider'] = ""
    vida_plantilla_ajustes1_40['Nit'] = "8909037905"
    vida_plantilla_ajustes1_40['Nombre'] = ""

    # Parametros para clave de contabilización 50
    vida_plantilla_ajustes1_50 = vida_plantilla_ajustes1_40.copy()
    vida_plantilla_ajustes1_50['Clave de contabilización para la siguiente posición'] = 50
    vida_plantilla_ajustes1_50['Cuenta de mayor de la contabilidad principal'] = np.select(
        [(vida_plantilla_ajustes1_50['PTCOMISION'] > 0) & (vida_plantilla_ajustes1_50['FUENTE'] == "GW"),
        (vida_plantilla_ajustes1_50['PTCOMISION'] < 0) & (vida_plantilla_ajustes1_50['FUENTE'] == "GW"),
        (vida_plantilla_ajustes1_50['PTCOMISION'] > 0) & (vida_plantilla_ajustes1_50['FUENTE'] == "CS"),
        (vida_plantilla_ajustes1_50['PTCOMISION'] < 0) & (vida_plantilla_ajustes1_50['FUENTE'] == "CS")],
        ["5209101010",
        "2481010040",
        "5209101000",
        "2481010000"],
        default="Revisar"
    )

    # Concatenación de las dos tablas de clave de contabilización
    vida_plantilla_ajustes1_final = pd.concat([vida_plantilla_ajustes1_40, vida_plantilla_ajustes1_50], axis=0)
    vida_plantilla_ajustes1_final = vida_plantilla_ajustes1_final.drop(['NMPOLIZA','CDRAMO','NMRECIBO','CDAGENTE','FUENTE','PTCOMISION'], axis=1)
    vida_plantilla_ajustes1_final = vida_plantilla_ajustes1_final.sort_values(by=['Agrupador', 'Clave de contabilización para la siguiente posición'])

    # Calcula el número total de filas en el DataFrame
    total_filas2 = len(vida_plantilla_ajustes1_final)

    # Define el tamaño de la fracción
    tamano_fraccion2 = 19998

    # Calcula el número total de fracciones
    total_fracciones2 = total_filas2 // tamano_fraccion2 + (1 if total_filas2 % tamano_fraccion2 != 0 else 0)

    # Bucle para dividir y exportar en fracciones
    for i in range(total_fracciones2):
        inicio2 = i * tamano_fraccion2
        fin2 = min((i + 1) * tamano_fraccion2, total_filas2)
        
        # Obtén la fracción actual del DataFrame
        fraccion_df2 = vida_plantilla_ajustes1_final.iloc[inicio2:fin2]
        
        # Exporta la fracción a un archivo CSV
        fraccion_df2.to_excel(f'02. Output/Ajustes/Ajustes_Financieros_Vida_{str(mes_cierre).zfill(2)}{año_cierre}_{i + 1}.xlsx', index=False)

    print(f"Ajustes financieros sin pólizas en dólares exportados en la carpeta 02. Output/Ajustes.")