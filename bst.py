"""
bst.py
------
A Binary Search Tree (BST) that indexes invoices by AMOUNT.

WHY A BST HERE?
An investigator often wants: "show me all invoices between Rs.50,000 and Rs.2,00,000."
Scanning every invoice every time (a plain list) is O(n) per query.
A BST lets us prune whole branches we know can't contain the answer,
making range queries much faster once the dataset is large — and more
importantly for your resume, it demonstrates BST insert + range traversal
from scratch.

NOTE: A plain BST can become unbalanced (worst case O(n)) if amounts come
in sorted order. For THIS project that's an acceptable simplification —
if you want to go further later, look up AVL trees or Red-Black trees,
which self-balance. Mentioning "I know this could be improved with a
self-balancing tree" is actually a good thing to say in an interview.
"""


class BSTNode:
    def __init__(self, invoice_row):
        self.amount = invoice_row["amount"]
        self.data = invoice_row   # store the full invoice dict at this node
        self.left = None
        self.right = None


class InvoiceBST:
    def __init__(self):
        self.root = None

    def insert(self, invoice_row):
        new_node = BSTNode(invoice_row)
        if self.root is None:
            self.root = new_node
            return
        self._insert_recursive(self.root, new_node)

    def _insert_recursive(self, current, new_node):
        if new_node.amount < current.amount:
            if current.left is None:
                current.left = new_node
            else:
                self._insert_recursive(current.left, new_node)
        else:
            if current.right is None:
                current.right = new_node
            else:
                self._insert_recursive(current.right, new_node)

    def range_query(self, low, high):
        """Return all invoices with amount in [low, high].

        Key BST optimization: if the current node's amount is BELOW low,
        we don't need to search its left subtree at all (everything there
        is even smaller). Same logic mirrored for the right subtree/high.
        This is what makes a BST faster than scanning a plain list.
        """
        results = []

        def _search(node):
            if node is None:
                return
            if low <= node.amount <= high:
                results.append(node.data)
            if node.amount > low:
                _search(node.left)
            if node.amount < high:
                _search(node.right)

        _search(self.root)
        return results

    def inorder(self):
        """Return all invoices sorted by amount (ascending).
        Inorder traversal of a BST always yields sorted order — classic property."""
        results = []

        def _walk(node):
            if node is None:
                return
            _walk(node.left)
            results.append(node.data)
            _walk(node.right)

        _walk(self.root)
        return results
