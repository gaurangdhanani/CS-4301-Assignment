"""Entry point: parse a 3-SAT input file, run quantum counting and Grover
search, and print a satisfying assignment plus an estimate of the number
of solutions.

Usage:
    python main.py <input_file>

Output (stdout, exactly two lines):
    line 1: a satisfying assignment as an n-bit string (x_0 leftmost),
            or the message "No satisfying assignment exists" if unsat.
    line 2: the rounded estimate of the number of satisfying assignments,
            or 0 if unsat.
Progress and debug messages go to stderr.
"""

import sys
from typing import Optional

from parser import parse
from classical import evaluate
from oracle import build_oracle
from grover import grover_search, optimal_iterations
from counting import quantum_count


def log(msg: str) -> None:
    """Print to stderr so it doesn't pollute the program's actual output."""
    print(msg, file=sys.stderr)


def choose_t(n: int) -> int:
    """Number of counting qubits.

    t=7 satisfies ε ≤ 0.01 for n ≤ 4 in our tests; scale up gently for
    larger n. Larger t = better accuracy but deeper circuit.
    """
    return max(7, n + 3)


def find_satisfying(n, clauses, oracle, M_estimate) -> Optional[str]:
    """Run Grover and return the most-frequent satisfying assignment.

    The optimal k usually works on the first try. As a safety net, we also
    try a couple of nearby k values in case the chosen one happened to
    amplify a non-solution at the expense of solutions.
    """
    base_k = optimal_iterations(n, M_estimate)
    candidates = [base_k]
    if 1 not in candidates:
        candidates.append(1)
    if base_k + 1 not in candidates:
        candidates.append(base_k + 1)

    for attempt, k in enumerate(candidates):
        if k < 0:
            continue
        log(f"  Grover attempt {attempt + 1}: k={k}")
        counts = grover_search(n, oracle, k=k, shots=1024)
        for assignment, _ in sorted(counts.items(), key=lambda kv: -kv[1]):
            if evaluate(assignment, clauses):
                return assignment
    return None


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_file>", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]

    log(f"Parsing {input_path}...")
    n, clauses = parse(input_path)
    N = 2 ** n
    log(f"  n={n}, m={len(clauses)}, N={N}")

    log("Building oracle...")
    oracle = build_oracle(n, clauses)

    t = choose_t(n)
    log(f"Running quantum counting (t={t})...")
    M_estimate = quantum_count(n, oracle, t=t)
    log(f"  M_estimate = {M_estimate:.4f}")

    # --- Branch: unsatisfiable? ---
    if M_estimate < 0.5:
        print("No satisfying assignment exists")
        print(0)
        return

    # --- Search for a satisfying assignment ---
    log("Running Grover search...")
    assignment = find_satisfying(n, clauses, oracle, M_estimate)

    if assignment is None:
        # Should not happen for genuinely satisfiable inputs; safety net only.
        log("WARNING: Grover failed to find a satisfying assignment.")
        print("No satisfying assignment found")
        print(round(M_estimate))
        return

    # --- Required output ---
    print(assignment)
    print(round(M_estimate))


if __name__ == "__main__":
    main()
