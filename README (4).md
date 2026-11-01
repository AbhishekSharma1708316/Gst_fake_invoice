# GST Circular Trading Fraud Detector

Finds suspicious patterns in GST invoice data: **circular trading rings** (firms invoicing each other in a loop) and **look-alike shell firm names**. The core logic is written from scratch, with no graph or string-matching libraries:

- a directed graph with **Tarjan's strongly connected components** algorithm
- **Levenshtein edit distance** (dynamic programming)
- a **binary search tree** for invoice amount range queries
- **linked lists** for per-firm transaction history

pandas reads the file. networkx and matplotlib are used only to *draw* a detected ring in the dashboard; they take no part in detection.

> The bundled dataset is **synthetic** (43 invoices, 2 planted rings). This is a learning and demonstration project, not a production fraud system. Flagged results are leads to review, not proof of fraud.

## The problem

In circular trading, a group of firms passes invoices around a loop (A -> B -> C -> A) so the same claimed value circulates and input tax credit can be claimed without a real supply of goods. Shell firms often use near-identical names to look like separate businesses. Both patterns can be found with classic algorithms.

## What it does

| Check | Technique | File |
|---|---|---|
| Circular trading rings | Seller -> buyer graph; Tarjan's SCC, rings = components with more than one firm | `graph.py` |
| Quick "is there any cycle?" check | DFS with a recursion stack | `graph.py` |
| Near-duplicate firm names | Levenshtein distance, pairwise, configurable threshold | `string_match.py` |
| Invoices in an amount range | Binary search tree with pruned range traversal | `bst.py` |
| Per-firm transaction history | Singly linked list with a tail pointer, one per firm | `linked_list.py` |

## Results on the sample data

Running `python main.py` on the bundled `gst_invoices.csv`:

- **2 rings found**: Shreeji Trading Co -> Vardhman Enterprises -> Shreeji Traderz Co -> Shreeji Trading Co, and a second ring through Ashirwad Metal / Ashirwad Metals / Jaikisan Agro.
- **2 near-duplicate name pairs**: "Shreeji Trading Co" vs "Shreeji Traderz Co" (distance 3) and "Ashirwad Metal Pvt Ltd" vs "Ashirwad Metals Pvt Ltd" (distance 1).
- The same lookalike names appear inside the rings, which is the combination the project is designed to surface.

## Project structure

```
.
├── app.py              # Streamlit dashboard (upload, visualize, query)
├── main.py             # Command-line report
├── graph.py            # Graph, cycle check, Tarjan's SCC, ring invoices
├── bst.py              # Invoice BST (insert, range query, inorder)
├── linked_list.py      # Transaction history (linked list) and ledger
├── string_match.py     # Levenshtein distance + suspicious name pairs
├── exploration.ipynb   # Early data exploration
├── gst_invoices.csv    # Sample synthetic data
├── requirements.txt
└── tests/              # pytest suite
```

## Input format

A CSV or Excel (`.xlsx`) file with these columns:

| Column | Description |
|---|---|
| `invoice_id` | Invoice number |
| `seller_gstin` | Seller's GSTIN |
| `seller_name` | Seller firm name |
| `buyer_gstin` | Buyer's GSTIN |
| `buyer_name` | Buyer firm name |
| `amount` | Invoice amount in Rs. (integer) |
| `date` | Invoice date |

If you upload a file with different column names, the dashboard asks you to map each required field to one of your columns.

## Setup

```bash
git clone https://github.com/AbhishekSharma1708316/Gst_fake_invoice.git
cd Gst_fake_invoice
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

**Dashboard**

```bash
streamlit run app.py
```

The dashboard shows summary metrics, each fraud ring as a graph picture with its invoices, a slider for the name-similarity threshold, a per-firm transaction history, and an amount range query.

**Command line**

```bash
python main.py                      # uses the bundled sample data
python main.py path/to/invoices.csv # or your own file
```

## Tests

```bash
pip install pytest
pytest
```

The suite covers each data structure on its own (cycles, disjoint rings, tails off a ring, BST range queries checked against brute force, linked-list order and tail pointer, known edit distances and thresholds) plus an end-to-end check on the sample data.

## How it works

1. **Load** invoices from CSV or Excel.
2. **Graph**: each firm (GSTIN) is a node; each invoice is a directed edge seller -> buyer carrying the invoice id and amount.
3. **Rings**: Tarjan's algorithm assigns each node a discovery index and a lowlink value. When a node's lowlink equals its index, it is the root of a strongly connected component and the component is popped off the stack. Components with more than one firm are reported as rings, together with the invoices inside them.
4. **Names**: every pair of distinct firm names is compared with Levenshtein distance. Pairs with a distance above 0 and at or below the threshold (default 3) are flagged.
5. **BST**: invoices are inserted by amount. A range query skips the left subtree when a node is at or below the lower bound, and the right subtree when it is at or above the upper bound.
6. **Linked lists**: each invoice adds a node to both the seller's list (`SOLD_TO`) and the buyer's list (`BOUGHT_FROM`). Histories are in the order invoices appear in the file.

## Complexity

V = firms, E = invoices, F = unique firm names, m and n = name lengths, h = BST height, k = results returned, t = transactions for one firm.

| Operation | Time |
|---|---|
| Build graph | O(V + E) |
| Cycle check (DFS) | O(V + E) |
| Tarjan's SCC | O(V + E) |
| Levenshtein, one pair | O(m * n) time and space |
| Name comparison across all firms | O(F^2 * m * n) |
| BST insert | O(log n) average, O(n) worst case |
| BST range query | O(h + k) |
| Linked list append (tail pointer) | O(1) |
| Read one firm's history | O(t) |

## Limitations

- **Synthetic data only.** There is no evaluation on real filings, and no false-positive analysis.
- **A cycle can be legitimate trade.** Rings are flagged by structure alone; amounts, dates and time windows are not used to score them.
- **Pairwise name matching is quadratic** in the number of unique names.
- **The BST is not self-balancing.** Sorted input degrades it to a linked list, and because insert and Tarjan's DFS are recursive, very large or very deep inputs (roughly a thousand levels) can hit Python's recursion limit.
- **Ring detection ignores self-invoicing.** A firm invoicing itself is a cycle for the DFS check but not a multi-firm ring.

## Future work

- Score rings by total value, number of hops and time window to rank leads.
- Replace the BST with a self-balancing tree (AVL or red-black) and make Tarjan's iterative.
- Block names by length or n-grams before computing edit distance.
- Flag names that differ only by case or punctuation, which currently count as distance 0.

## Author

Abhishek Sharma, IIIT Raichur. [GitHub](https://github.com/AbhishekSharma1708316/)
