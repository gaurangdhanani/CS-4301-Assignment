"""Test quantum counting against classical ground truth on four small instances."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import parse
from classical import count_satisfying
from oracle import build_oracle
from counting import quantum_count


def run_test(name, n, clauses, t=7, epsilon=0.01):
    print(f"\n{name}")
    print(f"  n={n}, m={len(clauses)}, t={t}")

    M_true, _ = count_satisfying(n, clauses)
    N = 2 ** n
    print(f"  classical ground truth: M={M_true} (N={N})")

    oracle = build_oracle(n, clauses)
    M_est = quantum_count(n, oracle, t=t)
    print(f"  quantum estimate:       M_est={M_est:.4f}")

    error = abs(M_est - M_true)
    tolerance = epsilon * N
    ok = error <= tolerance
    print(f"  |M_est - M| = {error:.4f}   tolerance ε·N = {tolerance:.4f}")
    print(f"  -> {'PASS' if ok else 'FAIL'}")
    return ok


# Test 1: spec example (M=5, N=8).
n1, clauses1 = parse("tests/inputs/example.txt")
t1 = run_test("Test 1: spec example", n1, clauses1, t=7)

# Test 2: unsatisfiable (M=0, N=2).
n2, clauses2 = parse("tests/inputs/unsat.txt")
t2 = run_test("Test 2: unsatisfiable", n2, clauses2, t=6)

# Test 3: tautology (M=N=4).
n3, clauses3 = parse("tests/inputs/tautology.txt")
t3 = run_test("Test 3: tautology", n3, clauses3, t=6)

# Test 4: hand-crafted n=4, M=1.
clauses4 = [
    [(0, False), (0, False), (0, False)],
    [(1, True),  (1, True),  (1, True)],
    [(2, False), (2, False), (2, False)],
    [(3, True),  (3, True),  (3, True)],
]
n4 = 4
t4 = run_test("Test 4: n=4, M=1 forced solution", n4, clauses4, t=7)

print(f"\n{'PASS' if all([t1, t2, t3, t4]) else 'FAIL'}")
