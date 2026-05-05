"""Test Grover search end-to-end.

Test 1: spec example (n=3, M=5). Verify a satisfying assignment shows up.
Test 2: hand-crafted n=4, M=1 instance. Verify the unique solution dominates
        the counts (~96% probability with k=3)."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import parse
from classical import evaluate, count_satisfying
from oracle import build_oracle
from grover import grover_search, optimal_iterations


def run_test(name, n, clauses, k, expected_set=None, require_dominance=False):
    print(f"\n{name}")
    print(f"  n={n}, m={len(clauses)}, k={k}")

    oracle = build_oracle(n, clauses)
    counts = grover_search(n, oracle, k, shots=1024)
    sorted_counts = sorted(counts.items(), key=lambda kv: -kv[1])

    print(f"  top 5 outcomes:")
    for s, c in sorted_counts[:5]:
        flag = "SAT" if evaluate(s, clauses) else "   "
        print(f"    {s}: {c:4}  [{flag}]")

    # Find the most-frequent satisfying assignment.
    found = next((s for s, _ in sorted_counts if evaluate(s, clauses)), None)
    if found is None:
        print(f"  -> FAIL: no satisfying assignment in any outcome")
        return False
    if expected_set and found not in expected_set:
        print(f"  -> FAIL: expected one of {expected_set}, got {found}")
        return False

    if require_dominance:
        top_str, top_hits = sorted_counts[0]
        if not evaluate(top_str, clauses):
            print(f"  -> FAIL: most-frequent '{top_str}' is not satisfying")
            return False
        if top_hits < 700:
            print(f"  -> WARN: most-frequent only got {top_hits}/1024 hits "
                  f"(expected dominance)")

    print(f"  -> PASS (first satisfying assignment: {found})")
    return True


# --- Test 1: spec example ---
n1, clauses1 = parse("tests/inputs/example.txt")
M1, _ = count_satisfying(n1, clauses1)
# Force at least 1 iteration so we actually exercise the Grover circuit.
k1 = max(1, optimal_iterations(n1, M1))
expected1 = {"001", "011", "101", "110", "111"}
test1 = run_test(
    "Test 1: spec example (n=3, M=5)",
    n1, clauses1, k1, expected_set=expected1,
)

# --- Test 2: hand-crafted n=4 instance with a unique solution ---
# Each clause acts as a unit clause via repetition, forcing one assignment.
# Forced solution: x0=1, x1=0, x2=1, x3=0  -> string "1010".
clauses2 = [
    [(0, False), (0, False), (0, False)],   # x0
    [(1, True),  (1, True),  (1, True)],    # ¬x1
    [(2, False), (2, False), (2, False)],   # x2
    [(3, True),  (3, True),  (3, True)],    # ¬x3
]
n2 = 4
M2, sol2 = count_satisfying(n2, clauses2)
print(f"\n[sanity] hand-crafted instance: count={M2}, example={sol2}")
k2 = optimal_iterations(n2, M2)  # should be 3 for M=1, N=16
expected2 = {"1010"}
test2 = run_test(
    "Test 2: n=4, M=1, forced solution",
    n2, clauses2, k2, expected_set=expected2, require_dominance=True,
)

print(f"\n{'PASS' if test1 and test2 else 'FAIL'}")
