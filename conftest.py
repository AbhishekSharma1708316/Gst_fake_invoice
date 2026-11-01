import os
import sys

# Make the project root importable (graph.py, bst.py, ...) when running `pytest` from anywhere.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
