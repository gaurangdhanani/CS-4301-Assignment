"""End-to-end regression test suite.

For each test input file:
  1. Compute the true count classically (brute force).
  2. Run `main.py` and parse its two-line stdout.
  3. Verify that the assignment satisfies the formula (or that the unsat
     message is reported correctly), and that the count is within ε·N of
     the true count, with ε = 0.01.

Prints one line per test (PASS/FAIL with deviation and timing) and exits
with status 0 if everything passed, 1 otherwise.
"""

import os
import sys
import subprocess
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import parse
from classical import count_satisfying, evaluate


TESTS = [
    ("spec example",   "tests/inputs/example.txt"),
    ("unsatisfiable",  "tests/inputs/unsat.txt"),
    ("tautology",      "tests/inputs/tautology.txt"),
    ("random n=3",     "tests/inputs/random_n3.txt"),
    ("random n=4",     "tests/inputs/random_n4.txt"),
]

EPSILON = 0.01


def run_main(input_file):
    """Invoke `python main.py input_file` and return (stdout_lines, stderr, exit_code)."""
    r = subprocess.run(
        [sys.executable, "main.py", input_file],
        capture_output=True, text=True,
    )
    return r.stdout.strip().split("\n"), r.stderr, r.returncode


def check(name, input_file):
    """Run one test; return (passed: bool, message: str)."""
    if not os.path.exists(input_file):
        return False, f"input file not found: {input_file}"

    n, clauses = parse(input_file)
    N = 2 ** n
    M_true, _ = count_satisfying(n, clauses)
    is_unsat = (M_true == 0)

    t0 = time.time()
    out, err, code = run_main(input_file)
    elapsed = time.time() - t0

    if code != 0:
        return False, f"exit {code} ({elapsed:.1f}s); stderr tail: {err.strip().splitlines()[-1] if err.strip() else '<empty>'}"

    if len(out) != 2:
        return False, f"expected 2 stdout lines, got {len(out)}: {out!r}"

    line1, line2 = out

    if is_unsat:
        if "No satisfying assignment" not in line1 or line2 != "0":
            return False, f"expected unsat, got line1={line1!r} line2={line2!r}"
        return True, f"unsat correctly reported  ({elapsed:.1f}s)"

    # Satisfiable case
    if not evaluate(line1, clauses):
        return False, f"assignment {line1!r} does not satisfy the formula"

    try:
        M_est = int(line2)
    except ValueError:
        return False, f"line 2 not an integer: {line2!r}"

    deviation = abs(M_est - M_true)
    tolerance = max(1, round(EPSILON * N))
    if deviation > tolerance:
        return False, (
            f"count {M_est} off by {deviation} from true M={M_true} "
            f"(tolerance {tolerance})"
        )

    return True, (
        f"M_true={M_true}, M_est={M_est}, dev={deviation}, "
        f"assignment={line1}  ({elapsed:.1f}s)"
    )


def main():
    print(f"Running {len(TESTS)} regression tests...\n")
    passed = 0
    for name, input_file in TESTS:
        ok, msg = check(name, input_file)
        flag = "PASS" if ok else "FAIL"
        print(f"  [{flag}] {name:18s}  {msg}")
        if ok:
            passed += 1

    total = len(TESTS)
    print(f"\n{passed}/{total} tests passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
