"""Quantum counting via phase estimation on the Grover operator G."""

import math
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFT
from qiskit_aer import AerSimulator

from grover import diffuser


def _build_grover_operator(n: int, oracle: QuantumCircuit) -> QuantumCircuit:
    """Build the Grover iterate G = D · O as a single circuit on (n + m + 1) qubits."""
    work_total = oracle.num_qubits
    G = QuantumCircuit(work_total, name="G")
    G.append(oracle.to_gate(label="oracle"), range(work_total))
    G.append(diffuser(n).to_gate(label="diffuser"), range(n))
    return G


def quantum_count(
    n: int,
    oracle: QuantumCircuit,
    t: int = 7,
    shots: int = 1024,
) -> float:
    """Estimate the number of satisfying assignments via phase estimation on G.

    Args:
        n: number of variable qubits.
        oracle: phase-flip oracle (QuantumCircuit) acting on n + m + 1 qubits;
            must leave all ancillas clean.
        t: number of counting qubits.  Default 7 gives ε ≈ 0.01·N for N ≤ 16.
        shots: number of measurement shots.

    Returns:
        M_estimate (float in [0, N]).
    """
    work_total = oracle.num_qubits
    total = t + work_total
    N = 2 ** n

    # Build Grover operator and its 1-controlled version.
    G_circuit = _build_grover_operator(n, oracle)
    cG = G_circuit.to_gate(label="G").control(1)

    qc = QuantumCircuit(total, t)

    # Counting qubits → uniform superposition.
    qc.h(range(t))
    # Variable qubits in the work register → uniform superposition.
    # Var qubits live at indices [t, t + n).  Clause ancillas and target stay |0⟩.
    qc.h(range(t, t + n))

    # Apply controlled-G^(2^j) from counting qubit j (just by repeating cG).
    work_qubits = list(range(t, t + work_total))
    for j in range(t):
        applied_to = [j] + work_qubits
        for _ in range(2 ** j):
            qc.append(cG, applied_to)

    # Inverse QFT on the counting register.
    qc.append(QFT(t, inverse=True, do_swaps=True), range(t))

    qc.measure(range(t), range(t))

    sim = AerSimulator()
    tqc = transpile(qc, sim)
    counts = sim.run(tqc, shots=shots).result().get_counts()

    if not counts:
        return 0.0

    # Most-frequent outcome → integer y → M.
    most_freq = max(counts, key=counts.get)
    y = int(most_freq, 2)

    theta = math.pi * y / (2 ** t)
    M_estimate = N * math.sin(theta) ** 2
    return max(0.0, min(float(N), M_estimate))
