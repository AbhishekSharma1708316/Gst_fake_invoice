"""
app.py
------
Streamlit dashboard for the GST Circular Trading Fraud Detector.

IMPORTANT: This file does NOT contain any DSA logic. It only:
  1. Takes user input (CSV upload, slider values, dropdown selection)
  2. Calls YOUR classes from graph.py / linked_list.py / bst.py / string_match.py
  3. Displays the results nicely

networkx + matplotlib are used ONLY to DRAW the graph as a picture.
The actual cycle detection is done by graph.find_fraud_rings() (your Tarjan's
code) — nothing here re-detects cycles using networkx.

RUN THIS WITH:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

from graph import Graph
from linked_list import TransactionLedger
from bst import InvoiceBST
from string_match import find_suspicious_name_pairs


st.set_page_config(page_title="GST Circular Trading Fraud Detector", layout="wide")
st.title("🔍 GST Circular Trading Fraud Detector")
st.caption("Detects fraud rings using Graph cycle detection (Tarjan's SCC), "
           "flags near-duplicate shell firm names (Levenshtein distance), "
           "and indexes invoices (BST) — all DSA implemented from scratch.")


# ---------- 1. Load data ----------
st.sidebar.header("Data")
uploaded = st.sidebar.file_uploader(
    "Upload invoice file (CSV or Excel)", type=["csv", "xlsx", "xls"]
)

if uploaded is not None:
    # Tally / bank exports are almost always .xlsx, so we branch on extension.
    # pd.read_excel needs the 'openpyxl' package installed for .xlsx files.
    if uploaded.name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded)
    else:
        df = pd.read_csv(uploaded)
else:
    df = pd.read_csv("gst_invoices.csv")
    st.sidebar.info("Using bundled sample dataset (gst_invoices.csv). "
                     "Upload your own CSV or Excel file to try different data.")

required_cols = {"invoice_id", "seller_gstin", "seller_name",
                  "buyer_gstin", "buyer_name", "amount", "date"}

if not required_cols.issubset(df.columns):
    st.sidebar.warning(
        "Your file's column names don't match what the detector expects. "
        "Map your columns below:"
    )
    col_map = {}
    available_cols = list(df.columns)
    for req_col in required_cols:
        col_map[req_col] = st.sidebar.selectbox(
            f"Column for '{req_col}'", options=["-- none --"] + available_cols,
            key=f"map_{req_col}"
        )

    if "-- none --" in col_map.values():
        st.error("Please map every required field in the sidebar before continuing.")
        st.stop()

    # rename the user's columns to our expected names
    rename_lookup = {v: k for k, v in col_map.items()}
    df = df.rename(columns=rename_lookup)[list(required_cols)]


# ---------- 2. Build data structures (YOUR classes, not networkx) ----------
@st.cache_data
def build_structures(df):
    graph = Graph()
    ledger = TransactionLedger()
    bst = InvoiceBST()
    gstin_to_name = {}

    for row in df.itertuples():
        graph.add_edge(row.seller_gstin, row.buyer_gstin, row.invoice_id, row.amount)
        ledger.record_invoice(row.seller_gstin, row.buyer_gstin, row.invoice_id,
                               row.amount, row.date)
        bst.insert({
            "invoice_id": row.invoice_id, "seller": row.seller_gstin,
            "buyer": row.buyer_gstin, "amount": row.amount, "date": row.date
        })
        gstin_to_name[row.seller_gstin] = row.seller_name
        gstin_to_name[row.buyer_gstin] = row.buyer_name

    return graph, ledger, bst, gstin_to_name


graph, ledger, bst, gstin_to_name = build_structures(df)
rings = graph.find_fraud_rings()  # <-- your Tarjan's SCC implementation


# ---------- 3. Overview metrics ----------
col1, col2, col3 = st.columns(3)
col1.metric("Total invoices", len(df))
col2.metric("Unique firms", len(gstin_to_name))
col3.metric("Fraud rings detected", len(rings))


# ---------- 4. Fraud rings + graph visualization ----------
st.header("Fraud Rings (Graph Cycle Detection)")

if not rings:
    st.success("No circular trading rings detected in this dataset.")
else:
    for idx, ring in enumerate(rings, start=1):
        with st.expander(f"Ring {idx} — {len(ring)} firms involved", expanded=(idx == 1)):
            invoices = graph.get_ring_invoices(ring)

            # --- draw this ring as a small graph picture (visualization only) ---
            g_viz = nx.DiGraph()
            for inv in invoices:
                g_viz.add_edge(gstin_to_name.get(inv["seller"], inv["seller"]),
                                gstin_to_name.get(inv["buyer"], inv["buyer"]),
                                label=f"₹{inv['amount']:,}")

            fig, ax = plt.subplots(figsize=(5, 4))
            pos = nx.circular_layout(g_viz)
            nx.draw(g_viz, pos, ax=ax, with_labels=True, node_color="#ffcccb",
                    node_size=2500, font_size=8, arrowsize=20, edge_color="#cc0000")
            edge_labels = nx.get_edge_attributes(g_viz, "label")
            nx.draw_networkx_edge_labels(g_viz, pos, edge_labels=edge_labels,
                                          font_size=7, ax=ax)
            st.pyplot(fig)
            plt.close(fig)

            # --- invoice table for this ring ---
            table_rows = [{
                "Invoice": inv["invoice_id"],
                "Seller": gstin_to_name.get(inv["seller"], inv["seller"]),
                "Buyer": gstin_to_name.get(inv["buyer"], inv["buyer"]),
                "Amount": f"₹{inv['amount']:,}"
            } for inv in invoices]
            st.table(pd.DataFrame(table_rows))


# ---------- 5. Near-duplicate firm names ----------
st.header("Suspicious Near-Duplicate Firm Names (Levenshtein Distance)")
max_dist = st.slider("Max edit distance to flag as suspicious", 1, 6, 3)
all_names = list(df["seller_name"]) + list(df["buyer_name"])
suspicious = find_suspicious_name_pairs(all_names, max_distance=max_dist)

if not suspicious:
    st.success("No suspiciously similar firm names found at this threshold.")
else:
    st.table(pd.DataFrame([{
        "Firm A": p["name_a"], "Firm B": p["name_b"], "Edit distance": p["edit_distance"]
    } for p in suspicious]))


# ---------- 6. Per-firm transaction history (Linked List) ----------
st.header("Firm Transaction History (Linked List)")
firm_names_sorted = sorted(set(gstin_to_name.values()))
selected_name = st.selectbox("Select a firm", firm_names_sorted)
selected_gstin = [g for g, n in gstin_to_name.items() if n == selected_name][0]

history = ledger.get_history(selected_gstin)
if history:
    st.table(pd.DataFrame(history.to_list()))


# ---------- 7. Amount range query (BST) ----------
st.header("Invoice Range Query (Binary Search Tree)")
min_amt, max_amt = int(df["amount"].min()), int(df["amount"].max())
low, high = st.slider("Amount range (₹)", min_amt, max_amt, (min_amt, max_amt))
range_results = bst.range_query(low, high)
st.write(f"{len(range_results)} invoice(s) found")
st.table(pd.DataFrame(range_results))