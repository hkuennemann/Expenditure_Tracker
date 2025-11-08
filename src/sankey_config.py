DATA_DIRECTORIES = [
    "data/personal",
    "data/common",
]

CATEGORY_COLORS = {
    "Monthly Budget": "#2c7fb8",
    "Education": "#f28e2b",
    "Transportation": "#59a14f",
    "Home": "#e15759",
    "Groceries": "#af7aa1",
    "Other": "#b07aa1",
    "Sports": "#76b7b2",
    "Entertainment": "#ff9da7",
    "Monthly Allowance": "#edc948",
    "Savings": "#4c72b0",
    "Utilities": "#3caea3",
    "Restaurant": "#f6a623",
    "Sport": "#76b7b2",
    "Other Inflow": "#6a4c93",
    "Next Balance": "#b5b5b5",
}

BASE_NODE_COLORS = {
    "Parents": "#ffa600",
    "Personal Account": "#003f5c",
    "Common Account": "#58508d",
    "Lara's Account": "#9c755f",
    "Income": "#bc5090",
    "Balance": "#d0d0d0",
    "Other Inflow": "rgba(0, 0, 0, 0)",
    "Next Balance": "#b5b5b5",
}

INCOME_NODE_NAME = "Income"
INCOME_NODE_COLOR = "#bc5090"

SURPLUS_CATEGORY = "Savings"
SURPLUS_TARGET = "Savings"

PARENTS_NODE = "Parents"
INCOME_NODE = "Income"
PERSONAL_ACCOUNT_NODE = "Personal Account"
LARA_ACCOUNT_NODE = "Lara's Account"
BALANCE_NODE = "Balance"
COMMON_ACCOUNT_NODE = "Common Account"
OTHER_INFLOW_NODE = "Other Inflow"
OTHER_INFLOW_CATEGORY = "Other Inflow"
NEXT_BALANCE_NODE = "Next Balance"
NEXT_BALANCE_CATEGORY = "Next Balance"

PRIMARY_NODE_ORDER = [
    PARENTS_NODE,
    INCOME_NODE,
    OTHER_INFLOW_NODE,
    LARA_ACCOUNT_NODE,
    BALANCE_NODE,
    PERSONAL_ACCOUNT_NODE,
    COMMON_ACCOUNT_NODE,
]

NODE_X_POSITIONS = {
    PARENTS_NODE: 0.02,
    INCOME_NODE: 0.16,
    OTHER_INFLOW_NODE: 0.24,
    LARA_ACCOUNT_NODE: 0.36,
    BALANCE_NODE: 0.4,
    PERSONAL_ACCOUNT_NODE: 0.46,
    COMMON_ACCOUNT_NODE: 0.64,
    NEXT_BALANCE_NODE: 0.88,
    SURPLUS_TARGET: 0.92,
}

CATEGORY_X_POSITIONS = {
    LARA_ACCOUNT_NODE: 0.58,
    BALANCE_NODE: 0.6,
    PERSONAL_ACCOUNT_NODE: 0.72,
    COMMON_ACCOUNT_NODE: 0.8,
    NEXT_BALANCE_NODE: 0.94,
}

DEFAULT_CATEGORY_X = 0.76
DEFAULT_MISC_X = 0.96

NEUTRAL_LINK_COLOR = "#d0d0d0"
NEUTRAL_NODE_COLOR = "#b2b2b2"
LINK_ALPHA = 0.7

NODE_STYLE = {
    "pad": 25,
    "thickness": 26,
    "line": {"color": "rgba(41, 51, 92, 0.3)", "width": 1},
    "hovertemplate": "<b>%{label}</b><br>Total flow: £%{value:,.2f}<extra></extra>",
}

LINK_STYLE = {
    "hoverlabel": {"bgcolor": "white", "font": {"color": "black"}},
    "hovertemplate": (
        "<b>%{label}</b><br>"
        "Flow: £%{value:,.2f}"
        "<br>Members: %{customdata}"
        "<extra></extra>"
    ),
}

VALUE_FORMAT = ".2f"
VALUE_SUFFIX = " £"

LAYOUT_STYLE = {
    "font": {"family": "Inter, Arial, sans-serif", "size": 14, "color": "#2f2f2f"},
    "paper_bgcolor": "#f7f9fb",
    "plot_bgcolor": "#f7f9fb",
    "margin": {"l": 20, "r": 20, "t": 70, "b": 20},
}

FRACTIONAL_EPSILON = 1e-9

