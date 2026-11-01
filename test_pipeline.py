"""End-to-end checks on the bundled sample dataset (gst_invoices.csv)."""
import os

import pandas as pd
import pytest

from main import build_structures
from string_match import find_suspicious_name_pairs

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "gst_invoices.csv")


@pytest.fixture(scope="module")
def data():
    df = pd.read_csv(CSV_PATH)
    graph, ledger, bst, names = build_structures(df)
    return df, graph, ledger, bst, names


def test_sample_data_has_the_expected_columns(data):
    df = data[0]
    assert {"invoice_id", "seller_gstin", "seller_name",
            "buyer_gstin", "buyer_name", "amount", "date"} <= set(df.columns)


def test_sample_data_has_unique_invoice_ids(data):
    df = data[0]
    assert df["invoice_id"].is_unique


def test_two_planted_rings_are_found(data):
    _, graph, _, _, names = data
    rings = [{names[g] for g in ring} for ring in graph.find_fraud_rings()]
    assert len(rings) == 2
    assert {"Shreeji Trading Co", "Shreeji Traderz Co", "Vardhman Enterprises"} in rings
    assert {"Ashirwad Metal Pvt Ltd", "Ashirwad Metals Pvt Ltd",
            "Jaikisan Agro Industries"} in rings


def test_every_invoice_lands_in_every_structure(data):
    df, graph, ledger, bst, _ = data
    n = len(df)
    assert sum(len(edges) for edges in graph.adjacency_list.values()) == n
    assert len(bst.inorder()) == n
    # each invoice is recorded for both the seller and the buyer
    assert sum(len(h.to_list()) for h in ledger.histories.values()) == 2 * n


def test_bst_range_query_matches_pandas(data):
    df, _, _, bst, _ = data
    low, high = 50_000, 200_000
    expected = set(df[(df.amount >= low) & (df.amount <= high)].invoice_id)
    assert {r["invoice_id"] for r in bst.range_query(low, high)} == expected


def test_name_pairs_found_in_sample_data(data):
    df = data[0]
    pairs = find_suspicious_name_pairs(
        list(df["seller_name"]) + list(df["buyer_name"]), max_distance=3
    )
    found = {frozenset((p["name_a"], p["name_b"])) for p in pairs}
    assert frozenset(("Shreeji Trading Co", "Shreeji Traderz Co")) in found
    assert frozenset(("Ashirwad Metal Pvt Ltd", "Ashirwad Metals Pvt Ltd")) in found
