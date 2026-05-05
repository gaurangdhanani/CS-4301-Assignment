"""Grover's search: diffuser and end-to-end search routine."""

import math
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


def diffuser(n: int) -> QuantumCircuit:
    """Standard Grover diffuser (inversion about the mean) on n qubits.

    Implements: H^⊗n · X^⊗n · MCZ · X^⊗n · H^⊗n.

    Returns a QuantumCircuit. Convert to a Gate via .to_gate(label="diffuser")
    when appending to a larger circuit.
    """
    if n < 1:
        raise ValueError(f"diffuser needs at least 1 qubit, got {n}")

    qc = QuantumCircuit(n, name="diffuser")

    qc.h(range(n))
    qc.x(range(n))

    # Multi-controlled Z: phase flip iff every qubit is |1⟩.
    if n == 1:
        qc.z(0)
    else:
        qc.h(n - 1)
        qc.mcx(list(range(n - 1)), n - 1)
        qc.h(n - 1)

    qc.x(range(n))
    qc.h(range(n))

    return qc


def optimal_iterations(n: int, m_estimate: float) -> int:
    """Compute the optimal Grover iteration count given an estimate of M.

    Uses the standard formula k ≈ (π/4)·sqrt(N/M) − 1/2 and rounds.
    Returns 0 when the formula prefers no iterations (e.g. when M is large
    relative to N).
    """
    if m_estimate <= 0:
        return 0
    N = 2 ** n
    if m_estimate >= N:
        return 0
    k_real = (math.pi / 4) * math.sqrt(N / m_estimate) - 0.5
    return max(0, round(k_real))


def grover_search(n: int, oracle, k: int, shots: int = 1024) -> dict:
    """Run Grover's search with k iterations.

    Args:
        n: number of variable qubits.
        oracle: a phase-flip oracle as a QuantumCircuit or Gate. Must act on
            all (n + clause_ancillas + 1) qubits with all ancillas clean on
            entry and exit. The first n qubits must be the variable register.
        k: number of Grover iterations.
        shots: number of measurement shots.

    Returns:
        A counts dict whose keys are bitstrings in **our** convention:
        position k of the string is the value of x_k. (Qiskit's default
        right-to-left ordering is reversed for you.)
    """
    if isinstance(oracle, QuantumCircuit):
        total = oracle.num_qubits
        oracle_gate = oracle.to_gate(label="oracle")
    else:
        total = oracle.num_qubits
        oracle_gate = oracle

    diff_gate = diffuser(n).to_gate(label="diffuser")

    qc = QuantumCircuit(total, n)
    qc.h(range(n))  # uniform superposition on var qubits; ancillas stay |0⟩.

    for _ in range(k):
        qc.append(oracle_gate, range(total))
        qc.append(diff_gate, range(n))

    qc.measure(range(n), range(n))

    sim = AerSimulator()
    tqc = transpile(qc, sim)
    qiskit_counts = sim.run(tqc, shots=shots).result().get_counts()

    # Reverse each key so position k of the string is the value of x_k.
    counts: dict = {}
    for qstr, hits in qiskit_counts.items():
        our_str = qstr[::-1]
        counts[our_str] = counts.get(our_str, 0) + hits
    return counts
