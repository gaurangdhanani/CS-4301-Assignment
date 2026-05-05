# Quantum 3-SAT

Grover's search and quantum counting for 3-SAT, using Qiskit and the Aer simulator.

## Environment
- Python: 
- Qiskit:
- qiskit-aer:

## Install
```bash
pip install qiskit qiskit-aer
```

## Run
```bash
python main.py path/to/input.txt
```

(Output format and example will be added later.)

## Testing

The repository ships with a small regression suite that runs `main.py` against
several inputs (the spec example, an unsatisfiable instance, a tautology, and
two random instances) and verifies the output classically.

Run all tests:

```bash
python tests/run_tests.py
```

Each test prints a one-line summary; the script exits with status 0 if every
test passes, 1 otherwise. Total runtime is roughly 1–2 minutes on a laptop
because of the Aer simulator workload for the n=4 case.

Individual unit tests for the building blocks (parser, classical evaluator,
oracle, diffuser, Grover, quantum counting) are also under `tests/`:

```bash
python tests/test_mark_clause.py
python tests/test_oracle.py
python tests/test_diffuser.py
python tests/test_grover.py
python tests/test_counting.py
```