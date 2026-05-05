"""Test diffuser: with a one-marked-state oracle on n=2, one Grover iteration
yields the marked state with probability 1."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from grover import diffuser


def make_marker_oracle(n, marked_int):
    """A trivial oracle that phase-flips exactly one marked basis state."""
    qc = QuantumCircuit(n, name=f"mark_{marked_int}")
    bits = [(marked_int >> k) & 1 for k in range(n)]

    # Map |marked⟩ to |11..1⟩ by flipping qubits where the marked bit is 0.
    for k, b in enumerate(bits):
        if b == 0:
            qc.x(k)

    # Multi-controlled Z on |11..1⟩.
    if n == 1:
        qc.z(0)
    else:
        qc.h(n - 1)
        qc.mcx(list(range(n - 1)), n - 1)
        qc.h(n - 1)

    # Uncompute the X flips.
    for k, b in enumerate(bits):
        if b == 0:
            qc.x(k)

    return qc


sim = AerSimulator()
n = 2
shots = 1000
all_ok = True

print(f"Grover (oracle + diffuser, 1 iteration) on n={n}, {shots} shots\n")
for marked in range(2 ** n):
    oracle = make_marker_oracle(n, marked)
    diff = diffuser(n)

    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    qc.append(oracle.to_gate(), range(n))
    qc.append(diff.to_gate(), range(n))
    qc.measure(range(n), range(n))

    tqc = transpile(qc, sim)
    counts = sim.run(tqc, shots=shots).result().get_counts()

    expected = format(marked, f"0{n}b")
    hits = counts.get(expected, 0)

    ok = hits == shots
    if not ok:
        all_ok = False
    flag = "ok " if ok else "BAD"
    print(f"  [{flag}] marked={marked} (Qiskit string '{expected}'): {hits}/{shots} hits")
    print(f"        counts: {counts}")

print(f"\n{'PASS' if all_ok else 'FAIL'}")
