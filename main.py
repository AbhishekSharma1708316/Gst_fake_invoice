"""
main.py
-------
Ties everything together:
1. Load CSV (pandas used ONLY for reading the file, not for any algorithm)
2. Build the Graph from invoices
3. Build the TransactionLedger (linked lists) from invoices
4. Build the BST from invoices
5. Run fraud ring detection (Tarjan's SCC) on the Graph
6. Run near-duplicate name detection (Levenshtein) on firm names
7. Print a readable fraud report
"""

import pandas as pd
from graph import Graph
from linked_list import TransactionLedger
from bst import InvoiceBST
from string_match import find_suspicious_name_pairs


def load_data(csv_path):
    df = pd.read_csv(csv_path)
    return df


def build_structures(df):
    graph = Graph()
    ledger = TransactionLedger()
    bst = InvoiceBST()
    gstin_to_name = {}   # for pretty-printing firm names instead of raw GSTINs

    for row in df.itertuples():
        graph.add_edge(row.seller_gstin, row.buyer_gstin, row.invoice_id, row.amount)
        ledger.record_invoice(row.seller_gstin, row.buyer_gstin, row.invoice_id,
                               row.amount, row.date)
        bst.insert({
            "invoice_id": row.invoice_id,
            "seller": row.seller_gstin,
            "buyer": row.buyer_gstin,
            "amount": row.amount,
            "date": row.date
        })
        gstin_to_name[row.seller_gstin] = row.seller_name
        gstin_to_name[row.buyer_gstin] = row.buyer_name

    return graph, ledger, bst, gstin_to_name


def print_fraud_report(graph, gstin_to_name):
    print("=" * 60)
    print("FRAUD RING DETECTION (Graph cycle detection / Tarjan's SCC)")
    print("=" * 60)

    if not graph.has_cycle():
        print("No cycles detected. No circular trading rings found.\n")
        return

    rings = graph.find_fraud_rings()
    print(f"Found {len(rings)} suspicious ring(s):\n")

    for idx, ring in enumerate(rings, start=1):
        print(f"--- Ring {idx} ---")
        names = [gstin_to_name.get(g, g) for g in ring]
        print(f"Firms involved: {names}")

        invoices = graph.get_ring_invoices(ring)
        for inv in invoices:
            seller_name = gstin_to_name.get(inv["seller"], inv["seller"])
            buyer_name = gstin_to_name.get(inv["buyer"], inv["buyer"])
            print(f"  {inv['invoice_id']}: {seller_name} -> {buyer_name} "
                  f"(Rs.{inv['amount']})")
        print()


def print_name_similarity_report(df):
    print("=" * 60)
    print("NEAR-DUPLICATE FIRM NAME DETECTION (Levenshtein distance)")
    print("=" * 60)

    all_names = list(df["seller_name"]) + list(df["buyer_name"])
    suspicious = find_suspicious_name_pairs(all_names, max_distance=3)

    if not suspicious:
        print("No suspiciously similar firm names found.\n")
        return

    print(f"Found {len(suspicious)} suspicious name pair(s):\n")
    for pair in suspicious:
        print(f"  '{pair['name_a']}'  <->  '{pair['name_b']}'  "
              f"(edit distance: {pair['edit_distance']})")
    print()


def demo_linked_list(ledger, gstin_to_name, sample_gstin):
    print("=" * 60)
    print(f"TRANSACTION HISTORY (Linked List) for {gstin_to_name.get(sample_gstin)}")
    print("=" * 60)
    history = ledger.get_history(sample_gstin)
    if history:
        history.print_history()
    print()


def demo_bst_range_query(bst, low, high):
    print("=" * 60)
    print(f"INVOICES BETWEEN Rs.{low} AND Rs.{high} (BST range query)")
    print("=" * 60)
    results = bst.range_query(low, high)
    for r in results:
        print(f"  {r['invoice_id']}: Rs.{r['amount']} on {r['date']}")
    print()


if __name__ == "__main__":
    import os
    import sys

    default_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gst_invoices.csv")
    csv_path = sys.argv[1] if len(sys.argv) > 1 else default_csv
    df = load_data(csv_path)

    graph, ledger, bst, gstin_to_name = build_structures(df)

    print_fraud_report(graph, gstin_to_name)
    print_name_similarity_report(df)
    demo_linked_list(ledger, gstin_to_name, "27BBBCR1122K1Z1")  # Shreeji Trading Co
    demo_bst_range_query(bst, 50000, 200000)