# GST Fake Invoice Detector

Detects suspicious GST invoice patterns, such as **circular trading rings** and **look-alike shell firm names**, using data structures and algorithms implemented from scratch (graph, BST, linked list, edit distance). pandas is used only to read the CSV.

> Built on a **synthetic** invoice dataset for learning and demonstration. It is not a production fraud system and makes no claim about real-world accuracy.

## Why this problem

In GST fraud, a group of firms can issue invoices to each other in a loop (A -> B -> C -> A) to claim input tax credit without any real supply of goods. Shell firms also often use near-identical names to look legitimate. Both patterns can be found with classic algorithms.

## What it does

| Check | Technique | File |
|---|---|---|
| Circular trading rings | Directed graph of seller -> buyer, strongly connected components via **Tarjan's SCC** | `graph.py` |
| Near-duplicate firm names | **Levenshtein edit distance** between firm names (threshold configurable) | `string_match.py` |
| Invoice amount range queries | **Binary search tree** keyed on invoice amount | `bst.py` |
| Per-firm transaction history | **Linked list** ledger per GSTIN | `linked_list.py` |

## Project structure

```
.
├── app.py              # Streamlit dashboard (upload CSV/Excel, view results)
├── main.py             # Command-line report
├── graph.py            # Graph + Tarjan's SCC fraud ring detection
├── bst.py              # Invoice BST with range query
├── linked_list.py      # Transaction ledger (linked lists)
├── string_match.py     # Levenshtein-based suspicious name pairs
├── exploration.ipynb   # Data exploration
├── gst_invoices.csv    # Sample synthetic data
└── requirements.txt
```

## Input format

A CSV (or Excel) file with these columns:

| Column | Description |
|---|---|
| `invoice_id` | Unique invoice number |
| `seller_gstin` | Seller's GSTIN |
| `buyer_gstin` | Buyer's GSTIN |
| `seller_name` | Seller firm name |
| `buyer_name` | Buyer firm name |
| `amount` | Invoice amount (Rs.) |
| `date` | Invoice date |

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

**Command line**

```bash
python main.py
```

The CLI prints three sections: detected fraud rings (with the invoices inside each ring), suspicious firm name pairs, and a sample transaction history and amount range query.

## How it works

1. **Load** invoices from CSV.
2. **Graph**: each firm is a node and each invoice is a directed edge (seller -> buyer) carrying the invoice id and amount.
3. **Rings**: Tarjan's algorithm finds strongly connected components. Any component with more than one firm means money flows in a cycle, so it is reported as a suspected ring along with its invoices.
4. **Names**: Levenshtein distance is computed between firm names. Pairs within the threshold (default 3) are flagged as possible shell-firm duplicates.
5. **BST / linked list**: invoices are indexed by amount for range queries, and each firm gets a linked-list ledger of its transactions.

## Complexity

| Operation | Time |
|---|---|
| Tarjan's SCC | O(V + E) |
| Levenshtein (one pair of names, lengths m and n) | O(m * n) |
| Name comparison across all firms | O(F^2 * m * n) for F firms |
| BST range query | O(h + k), h = tree height, k = results |
| Firm transaction history | O(t) for t transactions |

## Limitations

- Runs on synthetic data; flagged rings and name pairs are *suspicions to review*, not proof of fraud.
- A cycle can also be legitimate trade, so there is no false-positive analysis yet.
- Pairwise name comparison is quadratic in the number of firms.

## Future work

- Weight rings by total value and time window to reduce false positives.
- Add tests with known rings and known clean graphs.
- Faster name matching (e.g., blocking or n-gram filtering before edit distance).

## Author

Abhishek Sharma, IIIT Raichur. [GitHub](https://github.com/AbhishekSharma1708316/)
