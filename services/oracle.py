"""Oracle database service utilities."""
from __future__ import annotations

import os
from typing import Optional

import pandas as pd

try:
    import cx_Oracle  # type: ignore
except ImportError:  # pragma: no cover
    cx_Oracle = None  # type: ignore

DSN = os.getenv("ORACLE_DSN")
USER = os.getenv("ORACLE_USER")
PASSWORD = os.getenv("ORACLE_PASSWORD")


def has_credentials() -> bool:
    """Return True if Oracle credentials are available."""
    return all([DSN, USER, PASSWORD, cx_Oracle])


def get_connection() -> Optional["cx_Oracle.Connection"]:
    """Return Oracle connection if credentials are set."""
    if not has_credentials():
        return None
    return cx_Oracle.connect(user=USER, password=PASSWORD, dsn=DSN)


def fetch_dataframe(query: str) -> pd.DataFrame:
    """Fetch a dataframe from Oracle or return empty df."""
    conn = get_connection()
    if not conn:
        return pd.DataFrame()
    try:
        return pd.read_sql(query, conn)
    finally:
        conn.close()
