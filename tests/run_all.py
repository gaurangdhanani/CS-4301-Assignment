"""All-in-one regression test suite for the Quantum 3-SAT pipeline.

Every test case (formula text + expected behavior) is defined inline in this
file. Each test is written to a temp file at runtime, fed to `main.py`, and
the result is verified against the brute-force classical counter.

Usage:
    python tests/run_all.py

Exits with status 0 if every test passes, 1 otherwise.
"""

import os
import sys
import tempfile
import subprocess
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import parse
from classical import count_satisfying, evaluate


EPSILON = 0.01


# Each entry: (test name, formula text). Order matters: small/fast tests first
# so a quick Ctrl+C still gives you broad coverage of the easy cases.
TESTS = [
    # 1. Trivial single-variable
    ("single var positive (M=1)", """1
0 0 0"""),

    # 2. Single var, negated. Tests the -0 parsing trap.
    ("single var negative (tests -0)", """1
-0 -0 -0"""),

    # 3. Unsat at n=1: forces x0 to be both 0 and 1.
    ("unsat n=1", """1
0 0 0
-0 -0 -0"""),

    # 4. n=2 with exactly two solutions: 01 and 10.
    ("two var (M=2)", """2
0 1 1
-0 -1 -1"""),

    # 5. Tautology: every assignment satisfies. M=N=4.
    ("tautology n=2 (M=N)", """2
0 -0 1"""),

    # 6. n=2 hard unsat: forces both polarities of both variables.
    ("unsat n=2 (forced contradictions)", """2
0 0 0
-0 -0 -0
1 1 1
-1 -1 -1"""),

    # 7. Spec example.
    ("spec example (M=5)", """3
0 1 2
-0 1 2
0 -1 2"""),

    # 8. Single clause; only one assignment fails. Tests the high-M branch.
    ("near tautology n=3 (M=N-1=7)", """3
0 1 2"""),

    # 9. Three tautological clauses; every assignment satisfies. M=8.
    ("all tautologies n=3 (M=N=8)", """3
0 -0 1
1 -1 2
2 -2 0"""),

    # 10. Repeated and self-cancelling literals; exercises mark_clause dedup.
    ("repeated variables n=3 (M=3)", """3
0 0 1
1 1 -2
-2 -2 -2"""),

    # 11. n=3 with a moderate solution count.
    ("random n=3 (M=3)", """3
0 1 2
-0 1 -2
0 -1 -2
-0 -1 2
0 -1 2"""),

    # 12. n=4 with a unique solution: 0110.
    ("forced unique n=4 (M=1)", """4
-0 -0 -0
1 1 1
2 2 2
-3 -3 -3"""),

    # 13. n=4 sparse; only 4 of 16 assignments fail. High M, Grover overshoots.
    ("sparse n=4 (M=12)", """4
0 1 2
-0 -1 -2"""),

    # 14. Moderate n=4 instance; harness computes M.
    ("mid-density n=4", """4
0 1 2
-0 1 -2
0 -1 -2
1 2 -3
-1 -2 3
0 -1 3"""),

    # 15. Larger n=4 with 7 clauses; harness computes M.
    ("random n=4 (7 clauses)", """4
0 1 2
0 -1 -2
-0 1 -2
-0 -1 2
0 1 -3
0 -1 3
1 2 -3"""),
]


def run_main(input_file):
    """Run `python main.py input_file` and return (stdout_lines, stderr, exit_code)."""
    r = subprocess.run(
        [sys.executable, "main.py", input_file],
        capture_output=True, text=True,
    )
    return r.stdout.strip().split("\n"), r.stderr, r.returncode


def check(idx, name, formula_text, tmpdir):
    """Run one test. Returns (passed, message)."""
    input_file = os.path.join(tmpdir, f"test_{idx:02d}.txt")
    with open(input_file, "w") as f:
        f.write(formula_text.strip() + "\n")

    n, clauses = parse(input_file)
    N = 2 ** n
    M_true, _ = count_satisfying(n, clauses)
    is_unsat = (M_true == 0)

    t0 = time.time()
    out, err, code = run_main(input_file)
    elapsed = time.time() - t0

    if code != 0:
        tail = err.strip().splitlines()[-1] if err.strip() else "<empty>"
        return False, f"exit {code} ({elapsed:.1f}s); stderr tail: {tail}"

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
            f"(tol {tolerance})"
        )

    return True, (
        f"M_true={M_true}, M_est={M_est}, dev={deviation}, "
        f"assignment={line1}  ({elapsed:.1f}s)"
    )


def main():
    print(f"Running {len(TESTS)} regression tests (this takes 5-10 minutes)...\n")

    with tempfile.TemporaryDirectory(prefix="qsat_tests_") as tmpdir:
        passed = 0
        for idx, (name, formula) in enumerate(TESTS, start=1):
            ok, msg = check(idx, name, formula, tmpdir)
            flag = "PASS" if ok else "FAIL"
            print(f"  [{flag}] {idx:2d}. {name:34s}  {msg}")
            if ok:
                passed += 1

    total = len(TESTS)
    print(f"\n{passed}/{total} tests passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
