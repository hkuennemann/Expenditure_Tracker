import pandas as pd
import plotly.graph_objects as go
from plotly.colors import hex_to_rgb

import sankey_config as cfg
from sankey_data import SankeyData, prepare_sankey_data


CATEGORY_COLORS = cfg.CATEGORY_COLORS
NEUTRAL_LINK_COLOR = cfg.NEUTRAL_LINK_COLOR


def apply_alpha(color_value: str) -> str:
    if isinstance(color_value, str) and color_value.startswith("#"):
        r, g, b = hex_to_rgb(color_value)
        return f"rgba({r}, {g}, {b}, {cfg.LINK_ALPHA})"
    return color_value


def build_node_index(grouped: pd.DataFrame) -> tuple[pd.Index, dict[str, int]]:
    labels = pd.Index(
        pd.concat([grouped["source"], grouped["target"]]).unique(),
        name="label",
    )
    index_map = {label: idx for idx, label in enumerate(labels)}
    return labels, index_map


def format_currency(value: float) -> str:
    return f"£{value:,.2f}"


def is_hidden_node(label_key: str, node_label_map: dict[str, str]) -> bool:
    resolved_label = node_label_map.get(label_key, label_key)
    return resolved_label == cfg.OTHER_INFLOW_NODE


def resolve_node_color(
    label_key: str,
    node_label_map: dict[str, str],
    has_income_data: bool,
) -> str:
    node_color_map = cfg.BASE_NODE_COLORS.copy()
    if has_income_data:
        node_color_map.setdefault(cfg.INCOME_NODE_NAME, cfg.INCOME_NODE_COLOR)

    resolved_label = node_label_map.get(label_key, label_key)
    if resolved_label == cfg.OTHER_INFLOW_NODE:
        return "rgba(0,0,0,0)"
    return node_color_map.get(
        label_key,
        CATEGORY_COLORS.get(resolved_label, cfg.NEUTRAL_NODE_COLOR),
    )


def resolve_link_color(category_series: pd.Series) -> pd.Series:
    return (
        category_series
        .map(CATEGORY_COLORS)
        .fillna(NEUTRAL_LINK_COLOR)
        .where(category_series != cfg.OTHER_INFLOW_CATEGORY, "rgba(0,0,0,0)")
        .where(category_series != cfg.NEXT_BALANCE_CATEGORY, NEUTRAL_LINK_COLOR)
        .apply(apply_alpha)
    )


def format_node_labels(
    node_labels: pd.Index,
    node_label_map: dict[str, str],
    incoming_totals: dict[str, float],
    outgoing_totals: dict[str, float],
) -> list[str]:
    formatted: list[str] = []
    for label_key in node_labels:
        if is_hidden_node(label_key, node_label_map):
            formatted.append("")
            continue
        display_label = node_label_map.get(label_key, label_key)
        incoming = incoming_totals.get(label_key, 0.0)
        outgoing = outgoing_totals.get(label_key, 0.0)
        if incoming > 0:
            formatted.append(f"{display_label}<br>{format_currency(incoming)}")
        elif outgoing > 0:
            formatted.append(f"{display_label}<br>{format_currency(outgoing)}")
        else:
            formatted.append(display_label)
    return formatted


def build_sankey_figure(data: SankeyData | None = None) -> go.Figure:
    if data is None:
        data = prepare_sankey_data()

    grouped = data.grouped.copy()

    node_labels, label_to_index = build_node_index(grouped)
    grouped["source_id"] = grouped["source"].map(label_to_index)
    grouped["target_id"] = grouped["target"].map(label_to_index)

    grouped["amount_formatted"] = grouped["amount"].apply(format_currency)
    grouped["link_label"] = grouped.apply(
        lambda row: f"{row['category']} · {row['amount_formatted']}",
        axis=1,
    )

    outgoing_totals = grouped.groupby("source")["amount"].sum().to_dict()
    incoming_totals = grouped.groupby("target")["amount"].sum().to_dict()

    node_display_labels = format_node_labels(
        node_labels,
        data.node_label_map,
        incoming_totals,
        outgoing_totals,
    )

    node_colors = [
        resolve_node_color(label_key, data.node_label_map, data.has_income_data)
        for label_key in node_labels
    ]

    fig = go.Figure(data=[go.Sankey(
        valueformat=cfg.VALUE_FORMAT,
        valuesuffix=cfg.VALUE_SUFFIX,
        node=dict(
            **cfg.NODE_STYLE,
            label=node_display_labels,
            color=node_colors,
        ),
        link=dict(
            source=grouped["source_id"],
            target=grouped["target_id"],
            value=grouped["amount"],
            color=resolve_link_color(grouped["category"]),
            label=grouped["link_label"],
            customdata=grouped["detail"].fillna("—").replace("", "—"),
            **cfg.LINK_STYLE,
        )
    )])

    layout = dict(cfg.LAYOUT_STYLE)
    layout.setdefault("height", 700)
    fig.update_layout(**layout)
    return fig

