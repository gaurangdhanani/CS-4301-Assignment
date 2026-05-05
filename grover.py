"""Grover's search: diffuser and end-to-end search routine."""

from qiskit import QuantumCircuit


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
