"""Dash application entry point."""
from __future__ import annotations

import os

import pandas as pd
from dash import Dash
import dash_bootstrap_components as dbc

from services import oracle
from callbacks.main import set_df
from components.layout import render_layout


def load_data() -> pd.DataFrame:
    if oracle.has_credentials():
        query = """


SELECT
         DECODE(NVL(G.OSA_DIVISAO,0),0,'ALMOXARIFADO',DECODE(H.DIVISAO,1,'INDUSTRIA',3,'ADMINISTRACAO','AGRICOLA')) DIVISAO,
       B.PLANO_CODIGO,
       TRUNC(A.DT_ATUALIZACAO) DATA,
       A.ID_PESSOA ||'-'|| A.ID_COMPLE COD_PESSOA,
       C.DS_NOME,
       A.NRO_NF,
       A.ESPECIE_DOCTO,
       B.CFO,
       B.PTNATOPE,
       B.CST_ICMS,
       B.COD_ITEM,
       REPLACE(UPPER(DECODE(SUBSTR(REPLACE(REPLACE(REPLACE(TRIM(B.DSC_ITEM),CHR(9)),CHR(10)),CHR(13)),1,1),'-',SUBSTR(REPLACE(REPLACE(REPLACE(TRIM(B.DSC_ITEM),CHR(9)),CHR(10)),CHR(13)),2),REPLACE(REPLACE(REPLACE(TRIM(B.DSC_ITEM),CHR(9)),CHR(10)),CHR(13)))),'"','')
AS
DSC_ITEM,
       DECODE(B.COD_ITEM_SPED,NULL,B.COD_ITEM,B.COD_ITEM_SPED) AS COD_ITEM_SPED,
       UPPER(REPLACE(REPLACE(REPLACE(TRIM(I.DSC_COMPLETA),CHR(9)),CHR(10)),CHR(13))) AS DSC_ITEM_SPED,
       I.NCM,
       I.ID_TIPO_ITEM,
       J.DESCRICAO AS DESCRICAO_TIPO_ITEM,
       ROUND(B.VLR_TOTALITEM / B.QTD_ENTREGUE * F.QTD_RATEIO_ENTREGUE,4) VR_TOTAL,
       ROUND(B.VLR_ICMS / B.QTD_ENTREGUE * F.QTD_RATEIO_ENTREGUE,4) VR_ICMS,
         B.CREDITO_ICMS,
       ROUND(B.VLR_IMPOSTO / B.QTD_ENTREGUE * F.QTD_RATEIO_ENTREGUE,4) VLR_IPI,
         D.COD_GRUPO,
         K.DSC_GRUPO,
         L.OSA_NRO_OS,
         E.DSC_SUBGRUPO,
         UPPER(REPLACE(REPLACE(REPLACE(TRIM(L.DSC_SERVICO),CHR(9)),CHR(10)),CHR(13))) AS DSC_SERVICO,
       H.COD_CCUSTO,
       UPPER(REPLACE(REPLACE(REPLACE(TRIM(UPPER(DSC_CCUSTO)),CHR(9)),CHR(10)),CHR(13))) AS DSC_CCUSTO,
       I.CREDITO_PIS_COFINS,
       H.SN_PRODUTIVO,
       DECODE(B.MANUT_INVEST,2,'SIM','NAO') AS IMOBILIZADO,
       CASE WHEN
       ROUND(B.VLR_TOTALITEM / B.QTD_ENTREGUE * F.QTD_RATEIO_ENTREGUE,4) = 0 THEN 0
       ELSE ROUND(B.VLR_ICMS / B.QTD_ENTREGUE * F.QTD_RATEIO_ENTREGUE,4) / ROUND(B.VLR_TOTALITEM / B.QTD_ENTREGUE * F.QTD_RATEIO_ENTREGUE,4) END PROPORCAO_ICMS

  FROM NOTA_FISCAL             A,
       ITEM_NOTA_FISCAL        B,
       PESSOA                  C,
       ITEM                    D,
       SUBGRUPO                E,
       RATEIO_ITEMNF           F,
       ITEM_SOLICITACAO_COMPRA G,
       CENTRO_CUSTO            H,
       PLANO_CONTA             P,
       ITEM                    I,
       TIPO_ITEM               J,
       GRUPO                   K,
       ABERTURA_OS             L
       --PESSOA_REGIME_TRIBUTARIO RT
WHERE A.ID_NEGOCIOS     = B.ID_NEGOCIOS
   AND A.ID_PESSOA       = B.ID_PESSOA
   AND A.ID_COMPLE       = B.ID_COMPLE
   AND A.NRO_NF          = B.NRO_NF
   AND A.SERIE_NF        = B.SERIE_NF
   AND A.DT_EMISSAO      = B.DT_EMISSAO
   AND A.ID_PESSOA       = C.ID_PESSOA
   AND B.COD_ITEM        = D.COD_ITEM(+)
   AND D.COD_GRUPO       = E.COD_GRUPO
   AND D.COD_SUBGRUPO    = E.COD_SUBGRUPO
   AND D.COD_GRUPO       = K.COD_GRUPO
   --AND C.ID_TRIBUTACAO = RT.ID_TRIBUTACAO(+)
   --AND A.SLD_EFETIVADO   = 'S'
   AND A.ID_NEGOCIOS     = 1
   AND TRUNC(A.DT_ATUALIZACAO) BETWEEN TO_DATE('14/07/2025','DD/MM/YYYY') AND TO_DATE('17/07/2025' ,'DD/MM/YYYY')
   --AND B.CFO IN ('1556.11','2407.90','2556.10','1556.05','1407.04','1407.90','1556.04','1556.10','2556.06','1556.06','2407.04','2556.04','2556.05','1556.13','1407.06')
   --AND B.CFO IN ('1101.03','1101.04','2101.03','1101.14')
   --AND B.CFO IN ('1406.02','2406.02','1406.05','1551.02','1551.04','1551.05','1551.10','1551.22','2406.90','2551.02','2551.10','2551.22','1406.90','2406.91','1406.05','1551.06','2551.04','1551.25')
   --AND B.CFO IN ('1101.18','2101.07','1116.02','1120.02','1922.02','1101.07','1101.08')
   --AND B.CFO IN ('1101.05','1101.06','1653.05','1653.06','2653.06','1407.08','1556.08','1556.14','1653.07','1653.18','2556.08')
   --AND B.CFO IN ('1352.01','2352.01','1352.04','1352.02','2352.02','2352.05','3352.04','1352.06')
   --AND B.CFO IN ('1407.04','1407.90','1556.04','1556.05','1556.10','2407.04','2407.90','2556.04','2556.05','2556.10','1556.06','1556.13')
   --AND B.CFO IN ('1','1933.02','2933.02','1933.03')
   --AND B.CFO IN ('1556','2407','2556','1407','1556.04')
   --AND B.CFO IN ('1252')
     AND B.CFO IN ('1406','2406','1551','2551','1922','2922')
   --AND B.CFO IN ('1101','2101','1116','1120','1922','1252','1653','2653','1102')
   --AND B.CFO IN ('1101','1653','2653','1407','1556','2556','2407','2101')
   --AND B.CFO IN ('1352','2352','2932','3352','1932')
   --AND B.CFO IN ('1407','1556','2407','2556','1653')
   --AND B.CFO IN ('1','1933','2933')
   --AND I.ID_TIPO_ITEM IN (7)
   --AND A.ESPECIE_DOCTO IN ('NF','NS','NSE','NFE','NST')
   --AND A.ESPECIE_DOCTO IN ('ND','REC','NC','FAT','NCE','NFO')
   --AND A.ESPECIE_DOCTO IN ('CTE','NFT','CTS')
   AND B.ID_NEGOCIOS     = F.ID_NEGOCIOS
   AND B.ID_PESSOA       = F.ID_PESSOA
   AND B.ID_COMPLE       = F.ID_COMPLE
   AND B.NRO_NF          = F.NRO_NF
   AND B.SERIE_NF        = F.SERIE_NF
   AND B.DT_EMISSAO      = F.DT_EMISSAO
   AND B.ITEM_NF         = F.ITEM_NF
   AND B.COD_ITEM        = F.COD_ITEM
   AND DECODE(B.COD_ITEM_SPED,NULL,B.COD_ITEM,B.COD_ITEM_SPED) = I.COD_ITEM
   AND I.ID_TIPO_ITEM    = J.ID_TIPO_ITEM
   AND P.PLANO_CODIGO    = B.PLANO_CODIGO
   --AND SUBSTR(P.MASCARA,1,3) = '1.4'
   --AND SUBSTR(P.MASCARA,1,3) <> '1.4'
   AND F.COD_SC          = G.COD_SC(+)
   AND F.COD_ITEM        = G.COD_ITEM(+)
   AND G.ID_NEGOCIOS     = H.ID_NEGOCIOS(+)
   AND G.COD_CCUSTO      = H.COD_CCUSTO(+)
   AND G.ID_NEGOCIOS     = L.ID_NEGOCIOS(+)
   AND G.OSA_DIVISAO     = L.OSA_DIVISAO(+)
   AND G.OSA_NRO_OS      = L.OSA_NRO_OS(+)
   AND G.OSA_SEQUENCIA   = L.OSA_SEQUENCIA(+)
   
"""  # placeholder
        df = oracle.fetch_dataframe(query)
    else:
        df = pd.DataFrame(
            {
                "Divisão": ["A", "B"],
                "Plano Conta": ["001", "002"],
                "Data": ["2023-01-01", "2023-01-02"],
                "Fornecedor": ["F1", "F2"],
                "NF": [123, 456],
                "Espécie": ["X", "Y"],
                "Item": [1, 2],
                "Tipo Item": ["T1", "T2"],
                "Valor Total": [100.0, 200.0],
                "Valor ICMS": [10.0, 20.0],
                "Grupo": ["G1", "G2"],
                "O.S-Serv": ["OS1", "OS2"],
                "C.C": ["C1", "C2"],
                "Produtivo": ["S", "N"],
                "Crédito ICMS": ["S", "N"],
                "Prob. Crédito": [30, 70],
            }
        )
    return df


def create_app() -> Dash:
    df = load_data()
    set_df(df)
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.layout = render_layout(df)
    return app


app = create_app()

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=int(os.getenv("PORT", 8050)))
