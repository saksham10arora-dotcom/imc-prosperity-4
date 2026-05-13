"""Shared loaders for R5 research scripts. Read-only — does not modify any preexisting file."""
from __future__ import annotations
import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path("/Users/sakshamarora/Desktop/imcprosperity4/round5")
DAYS = (2, 3, 4)


def load_prices() -> pd.DataFrame:
    """Concat days 2/3/4. Adds a global tick `gt = day_offset*10000 + timestamp/100`.
    Each day has 10000 unique timestamps spaced by 100 (0, 100, ..., 999900).
    """
    frames = []
    for d in DAYS:
        df = pd.read_csv(DATA_DIR / f"prices_round_5_day_{d}.csv", sep=";")
        df["day"] = d
        frames.append(df)
    px = pd.concat(frames, ignore_index=True)
    # tick index per day (0..9999)
    px["tick"] = (px["timestamp"] // 100).astype(int)
    # global tick across days
    px["gt"] = (px["day"] - 2) * 10000 + px["tick"]
    return px


def pivot_mid(px: pd.DataFrame) -> pd.DataFrame:
    """Pivot to [gt × product] mid_price."""
    return (
        px.pivot_table(index="gt", columns="product", values="mid_price", aggfunc="last")
          .sort_index()
    )


def pivot_field(px: pd.DataFrame, field: str) -> pd.DataFrame:
    return px.pivot_table(index="gt", columns="product", values=field, aggfunc="last").sort_index()


def load_trades() -> pd.DataFrame:
    frames = []
    for d in DAYS:
        df = pd.read_csv(DATA_DIR / f"trades_round_5_day_{d}.csv", sep=";")
        df["day"] = d
        frames.append(df)
    tr = pd.concat(frames, ignore_index=True)
    tr["tick"] = (tr["timestamp"] // 100).astype(int)
    tr["gt"] = (tr["day"] - 2) * 10000 + tr["tick"]
    return tr


CATEGORIES = {
    "GALAXY_SOUNDS": ["DARK_MATTER", "BLACK_HOLES", "PLANETARY_RINGS", "SOLAR_WINDS", "SOLAR_FLAMES"],
    "SLEEP_POD": ["SUEDE", "LAMB_WOOL", "POLYESTER", "NYLON", "COTTON"],
    "MICROCHIP": ["CIRCLE", "OVAL", "SQUARE", "RECTANGLE", "TRIANGLE"],
    "PEBBLES": ["XS", "S", "M", "L", "XL"],
    "ROBOT": ["VACUUMING", "MOPPING", "DISHES", "LAUNDRY", "IRONING"],
    "UV_VISOR": ["YELLOW", "AMBER", "ORANGE", "RED", "MAGENTA"],
    "TRANSLATOR": ["SPACE_GRAY", "ASTRO_BLACK", "ECLIPSE_CHARCOAL", "GRAPHITE_MIST", "VOID_BLUE"],
    "PANEL": ["1X2", "2X2", "1X4", "2X4", "4X4"],
    "OXYGEN_SHAKE": ["MORNING_BREATH", "EVENING_BREATH", "MINT", "CHOCOLATE", "GARLIC"],
    "SNACKPACK": ["CHOCOLATE", "VANILLA", "PISTACHIO", "STRAWBERRY", "RASPBERRY"],
}


def all_products() -> list[str]:
    out = []
    for cat, members in CATEGORIES.items():
        out.extend(f"{cat}_{m}" for m in members)
    return out


def category_of(prod: str) -> str:
    for cat in CATEGORIES:
        if prod.startswith(cat + "_"):
            return cat
    raise ValueError(prod)
