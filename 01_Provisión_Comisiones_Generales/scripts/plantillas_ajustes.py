import pandas as pd
import numpy as np

# Función para generar plantillas de ajustes financieros
def plantillas_ajustes(generales_ajustes,ultimo_dia_del_mes,mes_cierre,año_cierre):

    # Filtrar registros para Ajustes menos por Pólizas en Dólares
    generales_plantilla_ajustes1 = generales_ajustes.loc[(generales_ajustes['AJUSTAR?'] == "Ajustado Póliza") |
                                                         (generales_ajustes['AJUSTAR?'] == "Ajustado Póliza/Recibo") |
                                                         (generales_ajustes['AJUSTAR?'] == "Ajustado Póliza/Agente") |
                                                         (generales_ajustes['AJUSTAR?'] == "Ajustado Recibo Duplicado")]

    # Identificar la fuente del registro
    generales_plantilla_ajustes1['FUENTE'] = np.select(
        [generales_plantilla_ajustes1['CDTIPO_FUENTE'].str.contains("CORE")],
        ["GW"],
        default="CS"
    )

    generales_plantilla_ajustes1['FUENTE'] = np.select(
        [(generales_plantilla_ajustes1['FUENTE'] == "CS") & (generales_plantilla_ajustes1['NMRECIBO'].str.len() >= 9)],
        ["GW"],
        default=generales_plantilla_ajustes1['FUENTE']
    )

    # Corrección del ramo
    generales_plantilla_ajustes1['CDRAMO'] = np.select(
        [generales_plantilla_ajustes1['NMPOLIZA'].astype(str).str[:3] == "900"],
        [generales_plantilla_ajustes1['CDRAMO']],
        default=generales_plantilla_ajustes1['NMPOLIZA'].astype(str).str[:3]
    )

    generales_plantilla_ajustes1_40 = generales_plantilla_ajustes1.fillna("").groupby(['NMPOLIZA','CDRAMO','NMRECIBO','CDAGENTE','FUENTE'])['PTCOMISION'].sum().reset_index()
    
    # Parametros para clave de contabilización 40
    generales_plantilla_ajustes1_40['Agrupador'] = 1
    generales_plantilla_ajustes1_40['Agrupador'] = generales_plantilla_ajustes1_40['Agrupador'].cumsum()
    generales_plantilla_ajustes1_40['Fecha de Documento'] = ultimo_dia_del_mes
    generales_plantilla_ajustes1_40['Clase de Documento'] = "SR"
    generales_plantilla_ajustes1_40['Sociedad'] = "1000"
    generales_plantilla_ajustes1_40['Fecha Contabilización'] = ultimo_dia_del_mes
    generales_plantilla_ajustes1_40['Período'] = ultimo_dia_del_mes[2:4]
    generales_plantilla_ajustes1_40['Clave de Moneda'] = "COP"
    generales_plantilla_ajustes1_40['Tipo de Cambio'] = ""
    generales_plantilla_ajustes1_40['Fe.conversión '] = ""
    generales_plantilla_ajustes1_40['Número documento de referencia'] = generales_plantilla_ajustes1_40['NMRECIBO'].astype(str)
    generales_plantilla_ajustes1_40['Texto de Cebecera'] = "AJUSTE PROVISION"
    generales_plantilla_ajustes1_40['Calc. Impuestos '] = ""
    generales_plantilla_ajustes1_40['Clave de contabilización para la siguiente posición'] = 40
    generales_plantilla_ajustes1_40['Número de identificación fiscal 1'] = ""
    generales_plantilla_ajustes1_40['Tipo de número de identificación fiscal'] = ""
    generales_plantilla_ajustes1_40['In. CME'] = ""
    generales_plantilla_ajustes1_40['Cuenta de mayor de la contabilidad principal'] = np.select(
        [(generales_plantilla_ajustes1_40['PTCOMISION'] > 0) & (generales_plantilla_ajustes1_40['FUENTE'] == "GW"),
        (generales_plantilla_ajustes1_40['PTCOMISION'] < 0) & (generales_plantilla_ajustes1_40['FUENTE'] == "GW"),
        (generales_plantilla_ajustes1_40['PTCOMISION'] > 0) & (generales_plantilla_ajustes1_40['FUENTE'] == "CS"),
        (generales_plantilla_ajustes1_40['PTCOMISION'] < 0) & (generales_plantilla_ajustes1_40['FUENTE'] == "CS")],
        ["2481010040",
        "5209101010",
        "2481010000",
        "5209101000"],
        default="Revisar"
    )
    generales_plantilla_ajustes1_40['Importe en la moneda del documento'] = abs(generales_plantilla_ajustes1_40['PTCOMISION'].round(0)).astype(int)
    generales_plantilla_ajustes1_40['Indicador IVA'] = ""
    generales_plantilla_ajustes1_40['Indicador retefuente WT_WITHCD'] = ""
    generales_plantilla_ajustes1_40['TP retefuente WITHT'] = ""
    generales_plantilla_ajustes1_40['indicador reteica WT_WITHCD'] = ""
    generales_plantilla_ajustes1_40['TP reteica WITHT'] = ""
    generales_plantilla_ajustes1_40['indicador reteiva WT_WITHCD'] = ""
    generales_plantilla_ajustes1_40['TP reteiva WITHT'] = ""
    generales_plantilla_ajustes1_40['indicador retetimbre WT_WITHCD'] = ""
    generales_plantilla_ajustes1_40['Tp retetimbre WITHT'] = ""
    #######################################################################
    division = generales_plantilla_ajustes1[['NMPOLIZA','NMRECIBO','CDDELEGACION']].fillna("")
    division = division.rename(columns={'CDDELEGACION':'División'})
    generales_plantilla_ajustes1_40 = generales_plantilla_ajustes1_40.merge(division,on=['NMPOLIZA','NMRECIBO'], how='left')
    generales_plantilla_ajustes1_40['Duplicado'] = generales_plantilla_ajustes1_40['Agrupador'].astype(str) + generales_plantilla_ajustes1_40['NMPOLIZA'] + generales_plantilla_ajustes1_40['NMRECIBO'].astype(str) + generales_plantilla_ajustes1_40['PTCOMISION'].astype(str) + generales_plantilla_ajustes1_40['Clave de contabilización para la siguiente posición'].astype(str)
    generales_plantilla_ajustes1_40 = generales_plantilla_ajustes1_40.drop_duplicates(subset=['Duplicado'], keep='first')
    generales_plantilla_ajustes1_40 = generales_plantilla_ajustes1_40.drop(['Duplicado'], axis=1)
    generales_plantilla_ajustes1_40['División'] = np.select(
        [(generales_plantilla_ajustes1_40['División'].str.len() < 4),
        (generales_plantilla_ajustes1_40['División'] == "0000") | (generales_plantilla_ajustes1_40['División'].str.len() > 4)],
        [generales_plantilla_ajustes1_40['División'].str.rjust(4, "0"),
        "0099"],
        default=generales_plantilla_ajustes1_40['División']
    )
    #######################################################################
    generales_plantilla_ajustes1_40['Clave de condiciones de pago'] = ""
    generales_plantilla_ajustes1_40['Centro de coste'] = "10" + generales_plantilla_ajustes1_40['División'] + "000"
    generales_plantilla_ajustes1_40['Centro de beneficio'] = ""
    generales_plantilla_ajustes1_40['Días del descuento por pronto pago 1'] = ""
    generales_plantilla_ajustes1_40['Porcentaje de descuento por pronto pago 1'] = ""
    generales_plantilla_ajustes1_40['Días del descuento por pronto pago 2'] = ""
    generales_plantilla_ajustes1_40['Porcentaje de descuento por pronto pago 2'] = ""
    generales_plantilla_ajustes1_40['Plazo para condición de pago neto'] = ""
    generales_plantilla_ajustes1_40['Fecha Contabilización'] = ultimo_dia_del_mes
    generales_plantilla_ajustes1_40['Fecha base para cálculo del vencimiento'] = ""
    generales_plantilla_ajustes1_40['Condición de pago fija'] = ""
    generales_plantilla_ajustes1_40['Base de descuento'] = ""
    generales_plantilla_ajustes1_40['Vía de pago'] = ""
    generales_plantilla_ajustes1_40['Bloqueo pago'] = ""
    generales_plantilla_ajustes1_40['% DPP'] = ""
    generales_plantilla_ajustes1_40['Importe DPP'] = ""
    generales_plantilla_ajustes1_40['Número de asignación'] = generales_plantilla_ajustes1_40['NMRECIBO'].astype(str)
    generales_plantilla_ajustes1_40['Texto posición'] = "AJUSTE PROVISION"
    generales_plantilla_ajustes1_40['Número de orden'] = ""
    generales_plantilla_ajustes1_40['Clave de referencia de interlocutor comercial'] = generales_plantilla_ajustes1_40['NMPOLIZA']
    generales_plantilla_ajustes1_40['Clave de referencia de interlocutor comercial2'] = generales_plantilla_ajustes1_40['CDRAMO']
    generales_plantilla_ajustes1_40['Clave de referencia para la posición de documento'] = generales_plantilla_ajustes1_40['CDAGENTE']
    generales_plantilla_ajustes1_40['Tipo de banco interlocutor'] = ""
    generales_plantilla_ajustes1_40['Fecha expedicion'] = ultimo_dia_del_mes[0:2] + "." + ultimo_dia_del_mes[2:4] + "." + ultimo_dia_del_mes[4:]
    generales_plantilla_ajustes1_40['Fecha fin vigencia'] = ultimo_dia_del_mes[0:2] + "." + ultimo_dia_del_mes[2:4] + "." + ultimo_dia_del_mes[4:]
    generales_plantilla_ajustes1_40['Poliza líder'] = ""
    generales_plantilla_ajustes1_40['Cert.lider'] = ""
    generales_plantilla_ajustes1_40['Nit'] = "8909034079"
    generales_plantilla_ajustes1_40['Nombre'] = ""

    # Parametros para clave de contabilización 50
    generales_plantilla_ajustes1_50 = generales_plantilla_ajustes1_40.copy()
    generales_plantilla_ajustes1_50['Clave de contabilización para la siguiente posición'] = 50
    generales_plantilla_ajustes1_50['Cuenta de mayor de la contabilidad principal'] = np.select(
        [(generales_plantilla_ajustes1_50['PTCOMISION'] > 0) & (generales_plantilla_ajustes1_50['FUENTE'] == "GW"),
        (generales_plantilla_ajustes1_50['PTCOMISION'] < 0) & (generales_plantilla_ajustes1_50['FUENTE'] == "GW"),
        (generales_plantilla_ajustes1_50['PTCOMISION'] > 0) & (generales_plantilla_ajustes1_50['FUENTE'] == "CS"),
        (generales_plantilla_ajustes1_50['PTCOMISION'] < 0) & (generales_plantilla_ajustes1_50['FUENTE'] == "CS")],
        ["5209101010",
        "2481010040",
        "5209101000",
        "2481010000"],
        default="Revisar"
    )

    # Concatenación de las dos tablas de clave de contabilización
    generales_plantilla_ajustes1_final = pd.concat([generales_plantilla_ajustes1_40, generales_plantilla_ajustes1_50], axis=0)
    generales_plantilla_ajustes1_final = generales_plantilla_ajustes1_final.drop(['NMPOLIZA','CDRAMO','NMRECIBO','CDAGENTE','FUENTE','PTCOMISION'], axis=1)
    generales_plantilla_ajustes1_final = generales_plantilla_ajustes1_final.sort_values(by=['Agrupador', 'Clave de contabilización para la siguiente posición'])

    # Calcula el número total de filas en el DataFrame
    total_filas2 = len(generales_plantilla_ajustes1_final)

    # Define el tamaño de la fracción
    tamano_fraccion2 = 19998

    # Calcula el número total de fracciones
    total_fracciones2 = total_filas2 // tamano_fraccion2 + (1 if total_filas2 % tamano_fraccion2 != 0 else 0)

    # Bucle para dividir y exportar en fracciones
    for i in range(total_fracciones2):
        inicio2 = i * tamano_fraccion2
        fin2 = min((i + 1) * tamano_fraccion2, total_filas2)
        
        # Obtén la fracción actual del DataFrame
        fraccion_df2 = generales_plantilla_ajustes1_final.iloc[inicio2:fin2]
        
        # Exporta la fracción a un archivo CSV
        fraccion_df2.to_csv(f'02. Output/Ajustes/Ajustes_Financieros_{str(mes_cierre).zfill(2)}{año_cierre}_{i + 1}.csv', index=False, sep=';', encoding="latin1")

    print(f"Ajustes financieros sin pólizas en dólares exportados en la carpeta 02. Output/Ajustes.")