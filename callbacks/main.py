"""Dash callbacks."""
from __future__ import annotations

import json
from typing import Any, Dict

import pandas as pd
from dash import html
import dash
import requests
from dash import Input, Output, State, callback

DF_CACHE: Dict[str, pd.DataFrame] = {}


def get_df() -> pd.DataFrame:
    return DF_CACHE.get("df", pd.DataFrame())


def set_df(df: pd.DataFrame) -> None:
    DF_CACHE["df"] = df


@callback(
    Output("table", "rowData"),
    Output("kpi-count", "children"),
    Output("stacked-bar", "figure"),
    Output("histogram", "figure"),
    Input("probability-range", "value"),
    Input("periodo", "value"),
    Input("plano", "value"),
    Input("custo", "value"),
    Input("credito", "value"),
)
def update_outputs(range_val, periodo, plano, custo, credito):
    df = get_df()
    if df.empty:
        return [], "0", {}, {}
    filt = (df["Prob. Crédito"].between(range_val[0], range_val[1]))
    if periodo:
        filt &= df["Data"].astype(str).str.contains(periodo)
    if plano:
        filt &= df["Plano Conta"].eq(plano)
    if custo:
        filt &= df["C.C"].eq(custo)
    if credito:
        filt &= df["Crédito ICMS"].eq(credito)
    filtered = df[filt]
    kpi = (df.shape[0] - filtered.shape[0])
    hist_fig = {
        "data": [{"type": "histogram", "x": filtered["Prob. Crédito"], "nbinsx": 20}],
        "layout": {"paper_bgcolor": "#18181B", "plot_bgcolor": "#18181B", "font": {"color": "#F5F5F5"}},
    }
    bar_data = filtered.copy()
    bar_data["bucket"] = pd.cut(bar_data["Prob. Crédito"], [0,20,40,60,80,100], right=True)
    bar = bar_data.groupby(["Crédito ICMS", "bucket"]).size().reset_index(name="count")
    bar_fig = {
        "data": [],
        "layout": {"barmode": "stack", "paper_bgcolor": "#18181B", "plot_bgcolor": "#18181B", "font": {"color": "#F5F5F5"}},
    }
    for credito_val in bar["Crédito ICMS"].unique():
        subset = bar[bar["Crédito ICMS"] == credito_val]
        bar_fig["data"].append({
            "type": "bar",
            "name": str(credito_val),
            "x": subset["bucket"].astype(str),
            "y": subset["count"],
            "orientation": "h",
        })
    return filtered.to_dict("records"), f"Itens para verificar: {kpi}", bar_fig, hist_fig


@callback(
    Output("toast", "children"),
    Input("table", "cellRendererData"),
    State("table", "rowData"),
    prevent_initial_call=True,
)
def on_action(data: Any, rows):
    if not data:
        return dash.no_update
    if isinstance(data, dict) and data.get("row") is not None:
        row = rows[data["row"]]
        payload = {
            "nf": row.get("NF"),
            "item": row.get("Item"),
            "prob": row.get("Prob. Crédito"),
        }
        try:
            res = requests.post("/acao", json=payload, timeout=5)
            msg = "Sucesso" if res.ok else "Falha"
        except Exception:
            msg = "Falha"
        return html.Div(msg, style={"background": "#24FF8B" if msg=="Sucesso" else "red"})
    return dash.no_update
