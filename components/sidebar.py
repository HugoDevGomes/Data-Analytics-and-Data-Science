"""Sidebar component."""
from dash import html, dcc


def render() -> html.Div:
    """Render the sidebar."""
    return html.Div(
        className="sidebar",
        children=[
            html.Img(src="/assets/logo.png", style={"width": "40px", "margin-bottom": "1rem"}),
            html.Div("Dashboard", style={"color": "#F5F5F5", "margin-bottom": "1rem"}),
            dcc.RadioItems(
                id="theme-switch",
                options=[{"label": "Dark", "value": "dark"}, {"label": "Light", "value": "light"}],
                value="dark",
                style={"color": "#F5F5F5", "margin-bottom": "1rem"},
            ),
            html.I(className="fa fa-cog", style={"color": "#F5F5F5"}),
        ],
    )
