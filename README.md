# Personal Finance Sankey

Interactive Sankey diagrams built with Streamlit and Plotly to visualize cash flows between accounts, categories, and destinations.

## Project structure

```
Personal_Finance/
├─ data/                  # Raw monthly CSVs (ignored by Git)
├─ src/
│  ├─ sankey_app.py       # Streamlit UI entry point
│  ├─ sankey_data.py      # Data loading, aggregation, helpers
│  ├─ sankey_plot.py      # Plotly Sankey figure builder
│  └─ sankey_config.py    # Colors, layout, node settings
├─ requirements.txt
└─ README.md
```

## Getting started

1. **Create & activate a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate      # Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit app**
   ```bash
   streamlit run src/sankey_app.py
   ```

   The dashboard opens with a horizontal month selector. Choose any single month or the `All` option to see combined flows. The raw CSVs live in `data/` (obviously ignored by Git), so drop new files into `data/personal/` and `data/common/` to update the chart.

## Data format

Each CSV is named either `c_YYYY_MM.csv` (common account) or `p_YYYY_MM.csv` (personal account), both with the following columns:

```
source,target,category,amount
```

Files placed in `data/personal/` and `data/common/` are automatically discovered by month.

## Running without Streamlit

If you just want the Sankey figure in a notebook or script:

```python
from src.sankey_plot import build_sankey_figure

fig = build_sankey_figure()
fig.show()
```

## TODO
- Being able to compare two months
