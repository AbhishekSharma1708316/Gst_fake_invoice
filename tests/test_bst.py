import random

from bst import InvoiceBST


def invoice(i, amount):
    return {"invoice_id": f"INV{i}", "seller": "S", "buyer": "B",
            "amount": amount, "date": "2026-01-01"}


def build(amounts):
    tree = InvoiceBST()
    for i, amt in enumerate(amounts):
        tree.insert(invoice(i, amt))
    return tree


def ids(rows):
    return sorted(r["invoice_id"] for r in rows)


def test_empty_tree_returns_nothing():
    tree = InvoiceBST()
    assert tree.range_query(0, 10**9) == []
    assert tree.inorder() == []


def test_range_is_inclusive_on_both_ends():
    tree = build([10, 20, 30, 40, 50])
    result = tree.range_query(20, 40)
    assert sorted(r["amount"] for r in result) == [20, 30, 40]


def test_range_with_no_matches():
    tree = build([10, 20, 30])
    assert tree.range_query(100, 200) == []


def test_single_value_range():
    tree = build([10, 20, 30])
    assert [r["amount"] for r in tree.range_query(20, 20)] == [20]


def test_duplicate_amounts_are_all_returned():
    tree = build([78000, 78000, 78000, 120000, 5000])
    result = tree.range_query(50000, 100000)
    assert len(result) == 3
    assert ids(result) == ["INV0", "INV1", "INV2"]


def test_inorder_is_sorted_by_amount():
    amounts = [50, 20, 70, 10, 30, 60, 80, 30]
    tree = build(amounts)
    assert [r["amount"] for r in tree.inorder()] == sorted(amounts)


def test_range_query_matches_brute_force_on_random_data():
    rng = random.Random(42)
    amounts = [rng.randint(1000, 500000) for _ in range(300)]
    tree = build(amounts)
    invoices = [invoice(i, a) for i, a in enumerate(amounts)]

    for _ in range(50):
        low = rng.randint(1000, 400000)
        high = low + rng.randint(0, 200000)
        expected = [inv for inv in invoices if low <= inv["amount"] <= high]
        assert ids(tree.range_query(low, high)) == ids(expected)


def test_sorted_insertion_still_correct_for_moderate_sizes():
    # Sorted input degenerates the BST into a linked list (worst case),
    # but results must still be correct.
    tree = build(list(range(1, 201)))
    assert [r["amount"] for r in tree.range_query(50, 60)] == list(range(50, 61))
