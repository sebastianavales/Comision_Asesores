import numpy as np
import pandas as pd

# Función para generar plantillas de ajustes financieros en USD
def plantillas_ajustes_usd(vida_ajustes,ultimo_dia_del_mes,mes_cierre,año_cierre):

    
    # Filtrar registros para Ajustes menos por Pólizas en Dólares
    vida_plantilla_ajustes2 = vida_ajustes.loc[(vida_ajustes['AJUSTAR?'] == "Ajustado Dólares")]

    # Identificar la fuente del registro
    vida_plantilla_ajustes2['FUENTE'] = np.select(
        [vida_plantilla_ajustes2['CDTIPO_FUENTE'].str.contains("CORE")],
        ["GW"],
        default="CS"
    )

    vida_plantilla_ajustes2['FUENTE'] = np.select(
        [(vida_plantilla_ajustes2['FUENTE'] == "CS") & (vida_plantilla_ajustes2['NMRECIBO'].str.len() >= 9)],
        ["GW"],
        default=vida_plantilla_ajustes2['FUENTE']
    )

    # Corrección del ramo
    vida_plantilla_ajustes2['CDRAMO'] = np.select(
        [vida_plantilla_ajustes2['NMPOLIZA'].astype(str).str[:3] == "900"],
        [vida_plantilla_ajustes2['CDRAMO']],
        default=vida_plantilla_ajustes2['NMPOLIZA'].astype(str).str[:3]
    )

    vida_plantilla_ajustes2_40 = vida_plantilla_ajustes2.fillna("").groupby(['NMPOLIZA','CDRAMO','NMRECIBO','CDAGENTE','FUENTE'])['PTCOMISION'].sum().reset_index()

    # Parametros para clave de contabilización 40
    vida_plantilla_ajustes2_40['Agrupador'] = 1
    vida_plantilla_ajustes2_40['Agrupador'] = vida_plantilla_ajustes2_40['Agrupador'].cumsum()
    vida_plantilla_ajustes2_40['Fecha de Documento'] = ultimo_dia_del_mes
    vida_plantilla_ajustes2_40['Clase de Documento'] = "SR"
    vida_plantilla_ajustes2_40['Sociedad'] = "1000"
    vida_plantilla_ajustes2_40['Fecha Contabilización'] = ultimo_dia_del_mes
    vida_plantilla_ajustes2_40['Período'] = ultimo_dia_del_mes[2:4]
    vida_plantilla_ajustes2_40['Clave de Moneda'] = "USD"
    vida_plantilla_ajustes2_40['Tipo de Cambio'] = ""
    vida_plantilla_ajustes2_40['Fe.conversión '] = ""
    vida_plantilla_ajustes2_40['Número documento de referencia'] = vida_plantilla_ajustes2_40['NMRECIBO']
    vida_plantilla_ajustes2_40['Texto de Cebecera'] = "MONEDA"
    vida_plantilla_ajustes2_40['Calc. Impuestos '] = ""
    vida_plantilla_ajustes2_40['Clave de contabilización para la siguiente posición'] = 40
    vida_plantilla_ajustes2_40['Número de identificación fiscal 1'] = ""
    vida_plantilla_ajustes2_40['Tipo de número de identificación fiscal'] = ""
    vida_plantilla_ajustes2_40['In. CME'] = ""
    vida_plantilla_ajustes2_40['Cuenta de mayor de la contabilidad principal'] = np.select(
        [(vida_plantilla_ajustes2_40['PTCOMISION'] > 0) & (vida_plantilla_ajustes2_40['FUENTE'] == "GW"),
        (vida_plantilla_ajustes2_40['PTCOMISION'] < 0) & (vida_plantilla_ajustes2_40['FUENTE'] == "GW"),
        (vida_plantilla_ajustes2_40['PTCOMISION'] > 0) & (vida_plantilla_ajustes2_40['FUENTE'] == "CS"),
        (vida_plantilla_ajustes2_40['PTCOMISION'] < 0) & (vida_plantilla_ajustes2_40['FUENTE'] == "CS")],
        ["2481010040",
        "5222103000",
        "2481010000",
        "5222103000"],
        default="Revisar"
    )
    vida_plantilla_ajustes2_40['Importe en la moneda del documento'] = abs(vida_plantilla_ajustes2_40['PTCOMISION'].round(0)).astype(int)
    vida_plantilla_ajustes2_40['Indicador IVA'] = ""
    vida_plantilla_ajustes2_40['Indicador retefuente WT_WITHCD'] = ""
    vida_plantilla_ajustes2_40['TP retefuente WITHT'] = ""
    vida_plantilla_ajustes2_40['indicador reteica WT_WITHCD'] = ""
    vida_plantilla_ajustes2_40['TP reteica WITHT'] = ""
    vida_plantilla_ajustes2_40['indicador reteiva WT_WITHCD'] = ""
    vida_plantilla_ajustes2_40['TP reteiva WITHT'] = ""
    vida_plantilla_ajustes2_40['indicador retetimbre WT_WITHCD'] = ""
    vida_plantilla_ajustes2_40['Tp retetimbre WITHT'] = ""
    #######################################################################
    division2 = vida_plantilla_ajustes2[['NMPOLIZA','NMRECIBO','CDDELEGACION']].fillna("")
    division2 = division2.rename(columns={'CDDELEGACION':'División'})
    vida_plantilla_ajustes2_40 = vida_plantilla_ajustes2_40.merge(division2,on=['NMPOLIZA','NMRECIBO'], how='left')
    vida_plantilla_ajustes2_40['Duplicado'] = vida_plantilla_ajustes2_40['Agrupador'].astype(str) + vida_plantilla_ajustes2_40['NMPOLIZA'] + vida_plantilla_ajustes2_40['NMRECIBO'].astype(str) + vida_plantilla_ajustes2_40['PTCOMISION'].astype(str) + vida_plantilla_ajustes2_40['Clave de contabilización para la siguiente posición'].astype(str)
    vida_plantilla_ajustes2_40 = vida_plantilla_ajustes2_40.drop_duplicates(subset=['Duplicado'], keep='first')
    vida_plantilla_ajustes2_40 = vida_plantilla_ajustes2_40.drop(['Duplicado'], axis=1)
    vida_plantilla_ajustes2_40['División'] = np.select(
        [(vida_plantilla_ajustes2_40['División'].str.len() < 4),
        (vida_plantilla_ajustes2_40['División'] == "0000") | (vida_plantilla_ajustes2_40['División'].str.len() > 4)],
        [vida_plantilla_ajustes2_40['División'].str.rjust(4, "0"),
        "0099"],
        default=vida_plantilla_ajustes2_40['División']
    )
    #vida_plantilla_ajustes1_40['División'] = ""
    #######################################################################
    vida_plantilla_ajustes2_40['Clave de condiciones de pago'] = ""
    vida_plantilla_ajustes2_40['Centro de coste'] = "10" + vida_plantilla_ajustes2_40['División'] + "000"
    vida_plantilla_ajustes2_40['Centro de beneficio'] = ""
    vida_plantilla_ajustes2_40['Días del descuento por pronto pago 1'] = ""
    vida_plantilla_ajustes2_40['Porcentaje de descuento por pronto pago 1'] = ""
    vida_plantilla_ajustes2_40['Días del descuento por pronto pago 2'] = ""
    vida_plantilla_ajustes2_40['Porcentaje de descuento por pronto pago 2'] = ""
    vida_plantilla_ajustes2_40['Plazo para condición de pago neto'] = ""
    vida_plantilla_ajustes2_40['Fecha Contabilización'] = ultimo_dia_del_mes
    vida_plantilla_ajustes2_40['Fecha base para cálculo del vencimiento'] = ""
    vida_plantilla_ajustes2_40['Condición de pago fija'] = ""
    vida_plantilla_ajustes2_40['Base de descuento'] = ""
    vida_plantilla_ajustes2_40['Vía de pago'] = ""
    vida_plantilla_ajustes2_40['Bloqueo pago'] = ""
    vida_plantilla_ajustes2_40['% DPP'] = ""
    vida_plantilla_ajustes2_40['Importe DPP'] = ""
    vida_plantilla_ajustes2_40['Número de asignación'] = vida_plantilla_ajustes2_40['NMRECIBO']
    vida_plantilla_ajustes2_40['Texto posición'] = "AJUSTE PROVISION"
    vida_plantilla_ajustes2_40['Número de orden'] = ""
    vida_plantilla_ajustes2_40['Clave de referencia de interlocutor comercial'] = vida_plantilla_ajustes2_40['NMPOLIZA']
    vida_plantilla_ajustes2_40['Clave de referencia de interlocutor comercial2'] = vida_plantilla_ajustes2_40['CDRAMO']  
    vida_plantilla_ajustes2_40['Clave de referencia para la posición de documento'] = vida_plantilla_ajustes2_40['CDAGENTE']
    vida_plantilla_ajustes2_40['Tipo de banco interlocutor'] = ""
    vida_plantilla_ajustes2_40['Fecha expedicion'] = ultimo_dia_del_mes[0:2] + "." + ultimo_dia_del_mes[2:4] + "." + ultimo_dia_del_mes[4:]
    vida_plantilla_ajustes2_40['Fecha fin vigencia'] = ultimo_dia_del_mes[0:2] + "." + ultimo_dia_del_mes[2:4] + "." + ultimo_dia_del_mes[4:]
    vida_plantilla_ajustes2_40['Poliza líder'] = ""
    vida_plantilla_ajustes2_40['Cert.lider'] = ""
    vida_plantilla_ajustes2_40['Nit'] = "8909034079"
    vida_plantilla_ajustes2_40['Nombre'] = ""

    # Parametros para clave de contabilización 50
    vida_plantilla_ajustes2_50 = vida_plantilla_ajustes2_40.copy()
    vida_plantilla_ajustes2_50['Clave de contabilización para la siguiente posición'] = 50
    vida_plantilla_ajustes2_50['Cuenta de mayor de la contabilidad principal'] = np.select(
        [(vida_plantilla_ajustes2_50['PTCOMISION'] > 0) & (vida_plantilla_ajustes2_50['FUENTE'] == "GW"),
        (vida_plantilla_ajustes2_50['PTCOMISION'] < 0) & (vida_plantilla_ajustes2_50['FUENTE'] == "GW"),
        (vida_plantilla_ajustes2_50['PTCOMISION'] > 0) & (vida_plantilla_ajustes2_50['FUENTE'] == "CS"),
        (vida_plantilla_ajustes2_50['PTCOMISION'] < 0) & (vida_plantilla_ajustes2_50['FUENTE'] == "CS")],
        ["5222103000",
        "2481010040",
        "5222103000",
        "2481010000"],
        default="Revisar"
    )

    # Concatenación de las dos tablas de clave de contabilización
    vida_plantilla_ajustes2_final = pd.concat([vida_plantilla_ajustes2_40, vida_plantilla_ajustes2_50], axis=0)
    vida_plantilla_ajustes2_final = vida_plantilla_ajustes2_final.drop(['NMPOLIZA','CDRAMO','NMRECIBO','CDAGENTE','FUENTE','PTCOMISION'], axis=1)
    vida_plantilla_ajustes2_final = vida_plantilla_ajustes2_final.sort_values(by=['Agrupador', 'Clave de contabilización para la siguiente posición'])

    # Calcula el número total de filas en el DataFrame
    total_filas3 = len(vida_plantilla_ajustes2_final)

    # Define el tamaño de la fracción
    tamano_fraccion3 = 19998

    # Calcula el número total de fracciones
    total_fracciones3 = total_filas3 // tamano_fraccion3 + (1 if total_filas3 % tamano_fraccion3 != 0 else 0)

    # Bucle para dividir y exportar en fracciones
    for i in range(total_fracciones3):
        inicio3 = i * tamano_fraccion3
        fin3 = min((i + 1) * tamano_fraccion3, total_filas3)
        
        # Obtén la fracción actual del DataFrame
        fraccion_df3 = vida_plantilla_ajustes2_final.iloc[inicio3:fin3]

        # Exporta la fracción a un archivo CSV
        fraccion_df3.to_excel(f'02. Output/Ajustes Dólares/Ajustes_Financieros_USD_Vida_{str(mes_cierre).zfill(2)}{año_cierre}_{i + 1}.xlsx', index=False)

    print(f"Ajustes financieros con pólizas en dólares exportados en la carpeta 02. Output/Ajustes Dólares.")