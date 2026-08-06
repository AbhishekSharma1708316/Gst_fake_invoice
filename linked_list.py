"""
linked_list.py
---------------
A singly linked list storing one firm's transaction history in chronological order.

WHY A LINKED LIST HERE?
For each firm, we want to append new invoices as we scan the CSV, and later
walk through a firm's full history in order (e.g. for an investigator reviewing
a flagged firm). Appending to the tail is O(1) if we track the tail pointer,
same as appending to a Python list — but this demonstrates you understand
building the structure yourself: nodes, pointers, traversal.
"""


class TransactionNode:
    def __init__(self, invoice_id, counterparty, amount, date, direction):
        self.invoice_id = invoice_id
        self.counterparty = counterparty      # the OTHER firm in this transaction
        self.amount = amount
        self.date = date
        self.direction = direction            # "SOLD_TO" or "BOUGHT_FROM"
        self.next = None                      # pointer to the next node


class TransactionHistory:
    def __init__(self, gstin):
        self.gstin = gstin
        self.head = None
        self.tail = None   # keeping a tail pointer avoids walking the whole
                            # list every time we add a transaction (O(1) append
                            # instead of O(n))

    def add_transaction(self, invoice_id, counterparty, amount, date, direction):
        new_node = TransactionNode(invoice_id, counterparty, amount, date, direction)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node

    def to_list(self):
        """Walk the linked list and return it as a plain Python list of dicts —
        useful for printing/inspecting without exposing the raw node objects."""
        result = []
        current = self.head
        while current is not None:
            result.append({
                "invoice_id": current.invoice_id,
                "counterparty": current.counterparty,
                "amount": current.amount,
                "date": current.date,
                "direction": current.direction
            })
            current = current.next
        return result

    def print_history(self):
        print(f"--- Transaction history for {self.gstin} ---")
        current = self.head
        while current is not None:
            print(f"  [{current.date}] {current.direction} {current.counterparty} "
                  f"| Invoice {current.invoice_id} | Rs.{current.amount}")
            current = current.next


class TransactionLedger:
    """Holds a TransactionHistory (linked list) for EVERY firm.
    This is just a dict wrapper: {gstin: TransactionHistory}.
    """
    def __init__(self):
        self.histories = {}

    def _get_or_create(self, gstin):
        if gstin not in self.histories:
            self.histories[gstin] = TransactionHistory(gstin)
        return self.histories[gstin]

    def record_invoice(self, seller_gstin, buyer_gstin, invoice_id, amount, date):
        """One invoice affects TWO firms' histories: the seller sold something,
        the buyer bought something. We add a node to each firm's linked list.
        """
        seller_history = self._get_or_create(seller_gstin)
        seller_history.add_transaction(invoice_id, buyer_gstin, amount, date, "SOLD_TO")

        buyer_history = self._get_or_create(buyer_gstin)
        buyer_history.add_transaction(invoice_id, seller_gstin, amount, date, "BOUGHT_FROM")

    def get_history(self, gstin):
        return self.histories.get(gstin)
