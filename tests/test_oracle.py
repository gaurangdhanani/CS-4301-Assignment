"""Test build_oracle: satisfying states get phase-flipped, ancillas remain clean."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from oracle import build_oracle
from parser import parse
from classical import evaluate

n, clauses = parse("tests/inputs/example.txt")
m = len(clauses)
total = n + m + 1

oracle = build_oracle(n, clauses)
print(f"Oracle: {oracle.num_qubits} qubits, depth {oracle.depth()}")

# Wrap: H on every var qubit, then apply the oracle.
qc = QuantumCircuit(total)
for k in range(n):
    qc.h(k)
qc.compose(oracle, qubits=range(total), inplace=True)

sv = Statevector.from_instruction(qc).data
amp = 1.0 / np.sqrt(2 ** n)

print("\n  var | amplitude  | satisfying | sign ok?")
all_ok = True
for x in range(2 ** n):
    var_str = "".join(str((x >> k) & 1) for k in range(n))
    is_sat = evaluate(var_str, clauses)
    expected = -amp if is_sat else +amp
    a = sv[x].real
    ok = np.isclose(a, expected, atol=1e-9)
    if not ok:
        all_ok = False
    flag = "ok " if ok else "BAD"
    print(f"  {var_str} | {a:+.4f}    | {str(is_sat):5}      | [{flag}]")

# Anywhere the ancillas (qubits n..total-1) are non-zero, the amplitude must be ~0.
threshold = 1e-9
ancilla_leak = False
for i in range(2 ** total):
    if abs(sv[i]) > threshold and (i >> n) != 0:
        ancilla_leak = True
        print(f"  LEAK: index {i} has amplitude {sv[i]} with non-zero ancillas")

print(f"\nVariable amplitudes: {'PASS' if all_ok else 'FAIL'}")
print(f"Ancilla cleanliness:  {'PASS' if not ancilla_leak else 'FAIL'}")

# Confirm the gate version matches the circuit version.
qc2 = QuantumCircuit(total)
for k in range(n):
    qc2.h(k)
qc2.append(oracle.to_gate(label="oracle"), range(total))
sv2 = Statevector.from_instruction(qc2).data
print(f"Gate version matches:  {'PASS' if np.allclose(sv, sv2) else 'FAIL'}")
