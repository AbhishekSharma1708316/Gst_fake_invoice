from graph import Graph


def build(edges):
    g = Graph()
    for i, (seller, buyer) in enumerate(edges):
        g.add_edge(seller, buyer, f"INV{i}", 1000 * (i + 1))
    return g


def as_sets(rings):
    return [set(r) for r in rings]


def test_three_firm_cycle_is_one_ring():
    g = build([("A", "B"), ("B", "C"), ("C", "A")])
    assert g.has_cycle() is True
    rings = g.find_fraud_rings()
    assert len(rings) == 1
    assert set(rings[0]) == {"A", "B", "C"}


def test_two_firm_cycle_is_a_ring():
    g = build([("A", "B"), ("B", "A")])
    assert as_sets(g.find_fraud_rings()) == [{"A", "B"}]


def test_chain_without_cycle_has_no_rings():
    g = build([("A", "B"), ("B", "C"), ("C", "D")])
    assert g.has_cycle() is False
    assert g.find_fraud_rings() == []


def test_empty_graph():
    g = Graph()
    assert g.has_cycle() is False
    assert g.find_fraud_rings() == []


def test_two_disjoint_cycles_are_two_rings():
    g = build([("A", "B"), ("B", "C"), ("C", "A"),
               ("X", "Y"), ("Y", "Z"), ("Z", "X")])
    rings = as_sets(g.find_fraud_rings())
    assert len(rings) == 2
    assert {"A", "B", "C"} in rings
    assert {"X", "Y", "Z"} in rings


def test_tail_hanging_off_a_ring_is_not_part_of_it():
    # A -> B -> C -> A is the ring; C -> D leaves it, D -> E is a plain chain
    g = build([("A", "B"), ("B", "C"), ("C", "A"), ("C", "D"), ("D", "E")])
    rings = as_sets(g.find_fraud_rings())
    assert rings == [{"A", "B", "C"}]


def test_firm_that_only_feeds_into_a_ring_is_not_in_it():
    g = build([("S", "A"), ("A", "B"), ("B", "A")])
    assert as_sets(g.find_fraud_rings()) == [{"A", "B"}]


def test_ring_invoices_only_contain_edges_inside_the_ring():
    g = build([("A", "B"), ("B", "C"), ("C", "A"), ("C", "D")])
    ring = g.find_fraud_rings()[0]
    invoices = g.get_ring_invoices(ring)
    assert len(invoices) == 3
    for inv in invoices:
        assert inv["seller"] in {"A", "B", "C"}
        assert inv["buyer"] in {"A", "B", "C"}
    assert {inv["invoice_id"] for inv in invoices} == {"INV0", "INV1", "INV2"}


def test_parallel_invoices_are_kept_as_separate_edges():
    g = Graph()
    g.add_edge("A", "B", "INV1", 100)
    g.add_edge("A", "B", "INV2", 200)
    g.add_edge("B", "A", "INV3", 300)
    ring = g.find_fraud_rings()[0]
    assert len(g.get_ring_invoices(ring)) == 3


def test_add_node_does_not_wipe_existing_edges():
    g = Graph()
    g.add_edge("A", "B", "INV1", 100)
    g.add_node("A")
    assert len(g.adjacency_list["A"]) == 1
