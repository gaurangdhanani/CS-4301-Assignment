# Quantum 3-SAT

Find a satisfying assignment and estimate the number of solutions for a
3-SAT formula using Grover's search and quantum counting on the Qiskit
Aer simulator.

## Requirements

- Python 3.10 or higher
- Qiskit and Qiskit Aer

Install with:

​```bash
pip install qiskit qiskit-aer
​```

## Run

​```bash
python main.py <input_file>
​```

For example:

​```bash
python main.py tests/inputs/example.txt
​```

## Input format

A plain text file:

- Line 1: an integer `n`, the number of Boolean variables.
- Each remaining line: three space-separated literals describing one
  clause, in the form `±x ±y ±z`, where each integer is a variable index
  in `{0, 1, ..., n-1}` and a leading `-` denotes negation.

For example, `0 -1 2` represents `x_0 ∨ ¬x_1 ∨ x_2`. Note that `-0` is
interpreted as `¬x_0` (the parser preserves the sign even on zero).

## Output format

Two lines on stdout:

- Line 1: a satisfying assignment as a binary string of length `n`. The
  `i`-th character is the value of variable `x_i`. If the formula is
  unsatisfiable, this line instead reads
  `No satisfying assignment exists`.
- Line 2: the rounded estimate of the number of satisfying assignments,
  or `0` if unsatisfiable.

Progress and debug messages are sent to stderr, so stdout is always
clean.

## Example

Input file `example.txt`:

​```
3
0 1 2
-0 1 2
0 -1 2
​```

Run:

​```bash
python main.py example.txt
​```

Expected output (the assignment may be any of the five satisfying
ones — `001`, `011`, `101`, `110`, `111`):

​```
001
5
​```

## Project layout

| File           | Role                                                 |
|----------------|------------------------------------------------------|
| `main.py`      | CLI entry point                                      |
| `parser.py`    | Reads the input file into an internal representation |
| `classical.py` | Brute-force evaluator and counter (reference)        |
| `oracle.py`    | Per-clause sub-circuit and full phase-flip oracle    |
| `grover.py`    | Grover diffuser, search routine, optimal-k formula   |
| `counting.py`  | Quantum counting via phase estimation on `G`         |
| `tests/`       | Unit tests, regression suite, and small input files  |

## Testing

The project ships with a single regression suite that contains 15 test cases inlined as Python strings. The harness writes each formula to a temp file, runs `main.py` against it, and verifies the result against a brute-force classical counter.

Run all tests with one command:

```bash
python tests/run_all.py
```

Each test prints a one-line summary; the script exits with status 0 if every test passes, 1 otherwise. Coverage includes:

- single-variable cases (n=1) for both polarities
- the `-0` parsing edge case
- unsatisfiable formulas (n=1 and n=2)
- tautologies (single-clause and multi-clause)
- clauses with repeated and self-cancelling literals
- forced unique solutions (n=4, M=1)
- sparse formulas with many solutions (high M, where Grover overshoots)
- the spec example and several random n=3 / n=4 instances

Total runtime is roughly 5–10 minutes on a laptop; the n=4 cases dominate.

Individual unit tests for the building blocks are also available:

```bash
python tests/test_mark_clause.py
python tests/test_oracle.py
python tests/test_diffuser.py
python tests/test_grover.py
python tests/test_counting.py
```

## Versions tested

- Python: 3.13.12
- Qiskit: 2.4.1
- qiskit-aer: 0.17.2

Check yours with:

​```bash
python -c "import qiskit, qiskit_aer; print(qiskit.__version__, qiskit_aer.__version__)"
python --version
​```

## Practical limits

The Aer state-vector simulator is limited to roughly 25–30 qubits. The
full pipeline uses `n + m + 1 + t` qubits, where `n` is the number of
variables, `m` is the number of clauses, and `t` is the number of
counting qubits (default 7 for `n ≤ 4`, scaling as `n + 3`). In practice
this code handles instances up to about `n = 5` with a modest number of
clauses; beyond that the simulator either runs out of memory or takes
too long.