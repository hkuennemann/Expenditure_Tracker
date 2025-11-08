from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Dict, Iterable, Iterator, List, Tuple

import pandas as pd

import sankey_config as cfg

TransactionFrame = pd.DataFrame


@dataclass(frozen=True)
class SankeyData:
    grouped: pd.DataFrame
    node_labels: pd.Index
    node_label_map: Dict[str, str]
    selected_months: List[str]
    has_income_data: bool


def load_transactions(file_paths: Iterable[str]) -> TransactionFrame:
    frames: List[pd.DataFrame] = []
    for path in file_paths:
        frame = pd.read_csv(path)
        frame["__source_file"] = path
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def normalise_transactions(transactions: TransactionFrame) -> TransactionFrame:
    cleaned = transactions.rename(columns=lambda col: col.strip())
    for column in ("source", "target", "category"):
        cleaned[column] = cleaned[column].astype(str).str.strip()
    cleaned["amount"] = pd.to_numeric(cleaned["amount"], errors="coerce")
    return cleaned.dropna(subset=["amount"])


def remove_cross_file_duplicates(transactions: TransactionFrame) -> TransactionFrame:
    group_columns = ["source", "target", "category", "amount", "month"]
    unique_file_counts = (
        transactions.groupby(group_columns)["__source_file"].transform("nunique")
    )
    duplicated_across_files = unique_file_counts > 1
    duplicate_entries = transactions.duplicated(subset=group_columns, keep="first")
    mask = ~(duplicated_across_files & duplicate_entries)
    return transactions.loc[mask].copy()


def register_node(node_label_map: Dict[str, str], key: str, label: str) -> str:
    if key not in node_label_map:
        node_label_map[key] = label
    return key


def resolve_source_node(
    node_label_map: Dict[str, str],
    primary_nodes: List[str],
    source_value: str,
    category_name: str,
) -> str:
    if source_value in primary_nodes:
        return register_node(node_label_map, source_value, source_value)
    label = category_name or source_value
    key = f"src|{label}|{source_value}"
    return register_node(node_label_map, key, label)


def resolve_target_node(
    node_label_map: Dict[str, str],
    primary_nodes: List[str],
    target_value: str,
    category_name: str,
    source_key: str,
) -> str:
    if target_value in primary_nodes:
        return register_node(node_label_map, target_value, target_value)
    label = category_name or target_value
    key = f"tgt|{label}|{source_key}"
    return register_node(node_label_map, key, label)


MONTH_PATTERN = re.compile(r"[a-z]+_(\d{4})_(\d{2})\.csv$", re.IGNORECASE)


def extract_month_key(path: Path) -> str | None:
    match = MONTH_PATTERN.search(path.name)
    if not match:
        return None
    year, month = match.group(1), match.group(2)
    return f"{year}-{month}"


def discover_transaction_files() -> Dict[str, List[str]]:
    files_by_month: Dict[str, List[str]] = defaultdict(list)
    directories = getattr(cfg, "DATA_DIRECTORIES", None)
    if not directories:
        raise ValueError("DATA_DIRECTORIES is not configured in sankey_config.")
    search_dirs = [Path(directory) for directory in directories]

    for directory in search_dirs:
        if not directory.exists():
            continue
        for csv_path in sorted(directory.glob("*.csv")):
            month_key = extract_month_key(csv_path)
            if month_key:
                files_by_month[month_key].append(csv_path.as_posix())

    return dict(sorted(files_by_month.items()))


def list_available_months() -> List[str]:
    files_by_month = discover_transaction_files()
    return list(files_by_month.keys())


def make_flow(
    source_key: str,
    target_id: str,
    category: str,
    amount: float,
    detail: str = "",
) -> Dict[str, object]:
    return {
        "source": source_key,
        "target": target_id,
        "category": category,
        "amount": float(amount),
        "detail": detail,
    }


def iter_transaction_flows(
    transactions: TransactionFrame,
    primary_nodes: List[str],
    node_label_map: Dict[str, str],
) -> Iterator[Tuple[str, str, str, float, str]]:
    for _, row in transactions.iterrows():
        category = row["category"]
        source_key = resolve_source_node(node_label_map, primary_nodes, row["source"], category)
        target_id = resolve_target_node(node_label_map, primary_nodes, row["target"], category, source_key)
        yield source_key, target_id, category, row["amount"], row["target"]


def total_inflow(flows: List[Dict[str, object]], node: str) -> float:
    return sum(flow["amount"] for flow in flows if flow["target"] == node)


def total_outflow(flows: List[Dict[str, object]], node: str) -> float:
    return sum(flow["amount"] for flow in flows if flow["source"] == node)


def compute_surplus(flows: List[Dict[str, object]], node: str) -> float:
    surplus = total_inflow(flows, node) - total_outflow(flows, node)
    return surplus if surplus > cfg.FRACTIONAL_EPSILON else 0.0


def append_surplus_flow(
    flows: List[Dict[str, object]],
    node_label_map: Dict[str, str],
    primary_nodes: List[str],
    source_node: str,
    category: str,
    target_node: str,
    detail: str = "",
) -> None:
    surplus = compute_surplus(flows, source_node)
    if surplus <= 0:
        return
    source_key = resolve_source_node(node_label_map, primary_nodes, source_node, category)
    target_id = resolve_target_node(node_label_map, primary_nodes, target_node, category, source_key)
    flows.append(make_flow(source_key, target_id, category, surplus, detail))


def add_other_inflow(
    flows: List[Dict[str, object]],
    node_label_map: Dict[str, str],
    primary_nodes: List[str],
) -> None:
    source_node = cfg.OTHER_INFLOW_NODE
    category = cfg.OTHER_INFLOW_CATEGORY
    support_targets = [cfg.LARA_ACCOUNT_NODE, cfg.BALANCE_NODE]
    source_key = resolve_source_node(node_label_map, primary_nodes, source_node, category)

    for target_name in support_targets:
        outgoing_total = total_outflow(flows, target_name)
        if outgoing_total <= cfg.FRACTIONAL_EPSILON:
            continue
        target_id = resolve_source_node(node_label_map, primary_nodes, target_name, category)
        flows.append(
            make_flow(
                source_key,
                target_id,
                category,
                outgoing_total,
                f"{target_name} inflow",
            )
        )


def combine_details(values: pd.Series) -> str:
    items = sorted({value for value in values if pd.notna(value)})
    return ", ".join(items)


def summarise_flows(flows: List[Dict[str, object]]) -> TransactionFrame:
    flow_df = pd.DataFrame(flows)
    if flow_df.empty:
        return flow_df
    return (
        flow_df.groupby(["source", "target", "category"], as_index=False)
        .agg(amount=("amount", "sum"), detail=("detail", combine_details))
        .query("amount > 0")
    )


def prepare_sankey_data(months: Iterable[str] | None = None) -> SankeyData:
    files_by_month = discover_transaction_files()
    if not files_by_month:
        raise FileNotFoundError("No transaction files found in configured directories.")

    filter_nodes: set[str] = set()

    if months:
        selected_months = [month for month in months if month in files_by_month]
        if not selected_months:
            raise ValueError("No matching months found for selection.")
    else:
        selected_months = list(files_by_month.keys())
        filter_nodes = {cfg.BALANCE_NODE, cfg.NEXT_BALANCE_NODE}

    file_paths: List[str] = []
    month_lookup: Dict[str, str] = {}
    for month in selected_months:
        for path in files_by_month[month]:
            file_paths.append(path)
            month_lookup[path] = month

    if months and len(selected_months) > 1:
        filter_nodes = {
            cfg.BALANCE_NODE,
            cfg.NEXT_BALANCE_NODE,
        }

    df = load_transactions(file_paths)
    df = normalise_transactions(df)
    df["month"] = df["__source_file"].map(month_lookup).fillna("unknown")
    df = remove_cross_file_duplicates(df)
    df = df.drop(columns=["__source_file", "month"])

    has_income_data = df["source"].eq(cfg.INCOME_NODE_NAME).any() or df["target"].eq(cfg.INCOME_NODE_NAME).any()

    primary_nodes = list(cfg.PRIMARY_NODE_ORDER)
    if has_income_data and cfg.INCOME_NODE_NAME not in primary_nodes:
        primary_nodes.insert(1, cfg.INCOME_NODE_NAME)

    node_label_map: Dict[str, str] = {}

    flows: List[Dict[str, object]] = [
        make_flow(source_key, target_id, category_name, value, detail)
        for source_key, target_id, category_name, value, detail in iter_transaction_flows(df, primary_nodes, node_label_map)
    ]

    append_surplus_flow(
        flows,
        node_label_map,
        primary_nodes,
        cfg.PERSONAL_ACCOUNT_NODE,
        cfg.SURPLUS_CATEGORY,
        cfg.SURPLUS_TARGET,
    )
    add_other_inflow(flows, node_label_map, primary_nodes)
    append_surplus_flow(
        flows,
        node_label_map,
        primary_nodes,
        cfg.COMMON_ACCOUNT_NODE,
        cfg.NEXT_BALANCE_CATEGORY,
        cfg.NEXT_BALANCE_NODE,
    )

    grouped = summarise_flows(flows)
    if not grouped.empty:
        if filter_nodes:
            grouped = grouped[
                ~grouped["source"].isin(filter_nodes)
                & ~grouped["target"].isin(filter_nodes)
                & ~grouped["category"].isin({cfg.NEXT_BALANCE_CATEGORY})
            ]
            for node in filter_nodes:
                node_label_map.pop(node, None)
        grouped = (
            grouped.assign(
                sort_rank=grouped["category"].eq(cfg.SURPLUS_CATEGORY).astype(int)
            )
            .sort_values(
                by=["source", "sort_rank", "target", "category"],
                ascending=[True, True, True, True],
            )
            .drop(columns=["sort_rank"])
        )
    node_labels = pd.Index(
        pd.concat([grouped["source"], grouped["target"]]).unique(),
        name="label",
    )

    return SankeyData(
        grouped=grouped,
        node_labels=node_labels,
        node_label_map=node_label_map,
        selected_months=selected_months,
        has_income_data=has_income_data,
    )

