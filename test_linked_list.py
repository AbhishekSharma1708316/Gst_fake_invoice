from linked_list import TransactionHistory, TransactionLedger


def test_history_keeps_insertion_order():
    h = TransactionHistory("G1")
    h.add_transaction("INV1", "G2", 100, "2026-01-01", "SOLD_TO")
    h.add_transaction("INV2", "G3", 200, "2026-01-02", "BOUGHT_FROM")
    h.add_transaction("INV3", "G4", 300, "2026-01-03", "SOLD_TO")
    assert [t["invoice_id"] for t in h.to_list()] == ["INV1", "INV2", "INV3"]


def test_tail_pointer_tracks_last_node():
    h = TransactionHistory("G1")
    assert h.head is None and h.tail is None
    h.add_transaction("INV1", "G2", 100, "2026-01-01", "SOLD_TO")
    assert h.head is h.tail
    h.add_transaction("INV2", "G2", 100, "2026-01-02", "SOLD_TO")
    assert h.tail.invoice_id == "INV2"
    assert h.head.next is h.tail
    assert h.tail.next is None


def test_empty_history_is_an_empty_list():
    assert TransactionHistory("G1").to_list() == []


def test_one_invoice_updates_both_firms():
    ledger = TransactionLedger()
    ledger.record_invoice("SELLER", "BUYER", "INV1", 500, "2026-02-02")

    seller = ledger.get_history("SELLER").to_list()
    buyer = ledger.get_history("BUYER").to_list()

    assert len(seller) == 1 and len(buyer) == 1
    assert seller[0]["direction"] == "SOLD_TO"
    assert seller[0]["counterparty"] == "BUYER"
    assert buyer[0]["direction"] == "BOUGHT_FROM"
    assert buyer[0]["counterparty"] == "SELLER"
    assert seller[0]["amount"] == buyer[0]["amount"] == 500


def test_histories_accumulate_per_firm():
    ledger = TransactionLedger()
    ledger.record_invoice("A", "B", "INV1", 100, "2026-01-01")
    ledger.record_invoice("B", "C", "INV2", 200, "2026-01-02")
    ledger.record_invoice("A", "C", "INV3", 300, "2026-01-03")

    assert len(ledger.get_history("A").to_list()) == 2
    assert len(ledger.get_history("B").to_list()) == 2
    assert len(ledger.get_history("C").to_list()) == 2


def test_unknown_firm_has_no_history():
    assert TransactionLedger().get_history("NOPE") is None
