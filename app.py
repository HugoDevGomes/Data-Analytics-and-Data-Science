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
        query = "SELECT * FROM YOUR_TABLE"  # placeholder
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
