"""Exhaustive test for mark_clause.

For each chosen clause, simulates every classical input as a basis state and
checks that (a) the ancilla matches the classical evaluator and (b) the
variable qubits are returned unchanged.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

from oracle import mark_clause
from classical import evaluate

sim = AerSimulator()


def run_one(clause, n, assignment_str):
    """Encode `assignment_str` on var qubits, apply mark_clause, measure everything."""
    # Qubits 0..n-1 are variables; qubit n is the ancilla.
    qc = QuantumCircuit(n + 1, n + 1)

    # Encode the classical input.
    for k, bit in enumerate(assignment_str):
        if bit == "1":
            qc.x(k)

    mark_clause(qc, clause, list(range(n)), n)

    for k in range(n + 1):
        qc.measure(k, k)

    counts = sim.run(qc, shots=1).result().get_counts()
    raw = next(iter(counts))
    # Qiskit's bitstring has classical bit 0 on the RIGHT. Reverse so position k = bit k.
    aligned = raw[::-1]
    return aligned[:n], int(aligned[n])


def check(clause, n, name):
    print(f"\n{name}")
    all_ok = True
    for i in range(2 ** n):
        a = "".join(str((i >> k) & 1) for k in range(n))
        var_after, anc = run_one(clause, n, a)
        expected = 1 if evaluate(a, [clause]) else 0
        ok = (anc == expected) and (var_after == a)
        if not ok:
            all_ok = False
        flag = "ok " if ok else "BAD"
        print(f"  [{flag}] input={a}  ancilla={anc}  expected={expected}  vars_after={var_after}")
    print(f"  --> {'PASS' if all_ok else 'FAIL'}")
    return all_ok


results = [
    check([(0, False), (1, True),  (2, False)], 3, "x0 OR ¬x1 OR x2"),
    check([(0, True),  (1, True),  (2, True)],  3, "¬x0 OR ¬x1 OR ¬x2"),
    check([(0, False), (0, False), (1, False)], 2, "x0 OR x0 OR x1  (repeated variable)"),
    check([(0, False), (0, True),  (1, False)], 2, "x0 OR ¬x0 OR x1 (tautology)"),
]

print("\n" + ("ALL PASS" if all(results) else "SOME FAILED"))
