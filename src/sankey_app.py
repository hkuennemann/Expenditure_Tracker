import streamlit as st

from sankey_data import list_available_months, prepare_sankey_data
from sankey_plot import build_sankey_figure

st.set_page_config(page_title="Personal Finance Sankey", layout="wide")

st.title("Personal Finance Sankey Diagrams")

available_months = list_available_months()

if not available_months:
    st.error("No transaction data found.")
    st.stop()

if "selected_months" not in st.session_state:
    st.session_state["selected_months"] = [available_months[-1]]

if "month_radio" not in st.session_state:
    st.session_state["month_radio"] = available_months[-1]

st.subheader("Select months")
month_options = ["All"] + available_months
selected_option = st.radio(
    "Month",
    options=month_options,
    key="month_radio",
    horizontal=True,
)

if selected_option == "All":
    session_selected = available_months[:]
    title_text = "All Months"
else:
    session_selected = [selected_option]
    title_text = selected_option

st.session_state["selected_months"] = session_selected

if not session_selected:
    st.warning("Select at least one month to display the diagram.")
    st.stop()

data = prepare_sankey_data(session_selected)
figure = build_sankey_figure(data)
figure.update_layout(
    title={
        "text": f"Personal Finance Sankey Diagram — {title_text}",
        "font": {"size": 24, "color": "#1f2a44"},
        "x": 0.5,
    }
)

st.plotly_chart(figure, use_container_width=True)

