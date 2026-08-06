"""
graph.py
--------
A directed graph built from scratch (no networkx) to represent GST invoices.

WHY A GRAPH?
Each firm (GSTIN) is a node. Each invoice is a directed edge: seller -> buyer.
A "circular trading ring" (fraud pattern) is just a CYCLE in this graph:
    A -> B -> C -> A
This file answers: "does this graph contain cycles, and which firms are in them?"

We use TARJAN'S ALGORITHM for Strongly Connected Components (SCC).
An SCC is a group of nodes where EVERY node can reach EVERY other node in the group.
If an SCC has more than 1 node, it means there's a cycle among those nodes -> fraud ring.
"""


class Graph:
    def __init__(self):
        # adjacency_list: {gstin: [(neighbor_gstin, invoice_id, amount), ...]}
        # This is the standard way to represent a graph in code.
        self.adjacency_list = {}

    def add_node(self, gstin):
        """Add a node (firm) if it doesn't already exist.
        We MUST check first — otherwise we'd overwrite an existing firm's
        edge list with an empty one and lose all its previously added invoices.
        """
        if gstin not in self.adjacency_list:
            self.adjacency_list[gstin] = []

    def add_edge(self, seller_gstin, buyer_gstin, invoice_id, amount):
        """Add a directed edge seller -> buyer.

        Direction matters: the invoice/credit flow goes from seller to buyer.
        A cycle seller1 -> seller2 -> seller3 -> seller1 means the same
        claimed value travels in a closed loop -> classic circular trading.
        """
        self.add_node(seller_gstin)
        self.add_node(buyer_gstin)
        self.adjacency_list[seller_gstin].append((buyer_gstin, invoice_id, amount))

    def has_cycle(self): 
        """Quick yes/no check: does ANY cycle exist anywhere in the graph?

        Uses DFS with two sets:
        - visited: nodes we've ever explored (across all DFS calls)
        - rec_stack: nodes on the CURRENT path of THIS DFS call chain

        If we reach a node that's already in rec_stack, we've looped back
        onto our own current path -> cycle found.
        If we reach a node that's in visited but NOT in rec_stack, it was
        reached via some other path earlier -> no cycle, just re-use.
        """
        visited = set()
        rec_stack = set()

        def dfs(node):
            visited.add(node)
            rec_stack.add(node)

            for neighbor, invoice_id, amount in self.adjacency_list.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True  # back edge found -> cycle!

            rec_stack.remove(node)  # done exploring this node's path, backtrack
            return False
 
        for node in self.adjacency_list:
            if node not in visited:
                if dfs(node):
                    return True
        return False

    def find_fraud_rings(self):
        """Tarjan's SCC algorithm: finds ALL groups of firms that form cycles.

        Returns a list of SCCs (each SCC is a list of GSTINs).
        We only care about SCCs with more than 1 node — a single node alone
        (no self-loop) isn't a ring.

        HOW TARJAN'S WORKS (intuition):
        - We DFS through the graph, assigning each node a discovery 'index'
          (the order we first visit it) and a 'lowlink' value.
        - 'lowlink[node]' = the SMALLEST index reachable from this node,
          including by using ONE back-edge to an ancestor still on our stack.
        - If lowlink[node] == index[node], this node is the "root" of an SCC —
          nothing deeper in the DFS could reach further back than this node.
          So we pop everything above it off the stack: that's one full SCC.
        """
        index_counter = [0]        # using a list so the nested function can mutate it
        index = {}                 # node -> discovery order
        lowlink = {}                # node -> lowest index reachable
        on_stack = {}               # node -> is it currently on our DFS stack?
        stack = []
        result = []

        def strongconnect(node):
            index[node] = index_counter[0]
            lowlink[node] = index_counter[0]
            index_counter[0] += 1
            stack.append(node)
            on_stack[node] = True

            for neighbor, invoice_id, amount in self.adjacency_list.get(node, []):
                if neighbor not in index:
                    # neighbor not visited yet -> recurse into it first
                    strongconnect(neighbor)
                    lowlink[node] = min(lowlink[node], lowlink[neighbor])
                elif on_stack.get(neighbor, False):
                    # neighbor is an ancestor still on stack -> back edge
                    lowlink[node] = min(lowlink[node], index[neighbor])
                # else: neighbor visited AND not on stack -> already resolved
                # into a different SCC, safely ignore it.

            if lowlink[node] == index[node]:
                # node is the root of an SCC -> pop the whole component off
                scc = []
                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    scc.append(w)
                    if w == node:
                        break
                result.append(scc)

        for node in self.adjacency_list:
            if node not in index:
                strongconnect(node)

        # Only keep SCCs with more than 1 node -> those are actual rings
        fraud_rings = [scc for scc in result if len(scc) > 1]
        return fraud_rings

    def get_ring_invoices(self, ring):
        """Given a list of GSTINs forming a ring, return the actual invoices
        (edges) that connect them — so you can show WHICH invoices are suspicious,
        not just which firms.
        """
        ring_set = set(ring)
        ring_invoices = []
        for seller in ring:
            for buyer, invoice_id, amount in self.adjacency_list.get(seller, []):
                if buyer in ring_set:
                    ring_invoices.append({
                        "seller": seller,
                        "buyer": buyer,
                        "invoice_id": invoice_id,
                        "amount": amount
                    })
        return ring_invoices
