"""Main layout components."""
from __future__ import annotations

from dash import html, dcc
import dash_ag_grid as dag
import pandas as pd

from .sidebar import render as render_sidebar


def render_layout(df: pd.DataFrame) -> html.Div:
    columns = [
        {"field": c} for c in df.columns if c != "Prob. Crédito"
    ] + [
        {
            "field": "Prob. Crédito",
            "cellStyle": {
                "backgroundColor": {
                    "function": "d3.interpolateRdYlGn(1 - params.value/100)"
                }
            },
        },
        {
            "field": "action",
            "cellRenderer": "AgGridButtonRenderer",
            "cellRendererParams": {
                "label": "Verificar",
                "style": {"padding": "2px 6px"}
            },
        },
    ]

    return html.Div(
        [
            render_sidebar(),
            html.Div(
                className="main",
                children=[
                    html.Div(
                        className="range-card",
                        children=[
                            html.Div("Índice Probabilidade"),
                            dcc.RangeSlider(0, 100, 1, value=[0, 100], id="probability-range"),
                            html.Div(id="kpi-count", className="kpi"),
                        ],
                    ),
                    dcc.Graph(id="stacked-bar"),
                    html.Div(
                        [
                            dcc.Dropdown(id="periodo", placeholder="Período"),
                            dcc.Dropdown(id="plano", placeholder="Plano Código"),
                            dcc.Dropdown(id="custo", placeholder="C. Custo"),
                            dcc.Dropdown(id="credito", placeholder="Crédito ICMS"),
                        ],
                        style={"display": "flex", "gap": "1rem"},
                    ),
                    dcc.Graph(id="histogram"),
                    dag.AgGrid(
                        id="table",
                        columnDefs=columns,
                        rowData=df.to_dict("records"),
                        dashGridOptions={"pagination": True},
                    ),
                    html.Div(id="toast"),
                ],
            ),
        ]
    )
