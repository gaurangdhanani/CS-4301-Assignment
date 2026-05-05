"""Quantum oracle for 3-SAT: per-clause sub-circuits and a full phase-flip oracle."""

from typing import List, Sequence, Tuple
from qiskit import QuantumCircuit

Literal = Tuple[int, bool]
Clause = List[Literal]


def mark_clause(
    qc: QuantumCircuit,
    clause: Clause,
    var_qubits: Sequence,
    clause_ancilla,
) -> None:
    """Set `clause_ancilla` to |1> iff the basis state on `var_qubits` satisfies `clause`.

    Reversible: variable qubits are returned to their original state.
    Assumes `clause_ancilla` starts in |0>.

    Handles three special cases:
      * repeated literals are deduplicated;
      * a clause containing both x_i and ¬x_i is a tautology — ancilla just flips to 1;
      * any of 1, 2, or 3 distinct literals is supported (Qiskit's mcx handles any count).
    """
    # 1. Deduplicate. (x0 ∨ x0 ∨ x1) is equivalent to (x0 ∨ x1).
    distinct: List[Literal] = list(set(clause))

    # 2. Tautology check: same variable appears both positive and negated.
    seen_vars = {v for v, _ in distinct}
    is_tautology = any(
        (v, False) in distinct and (v, True) in distinct
        for v in seen_vars
    )
    if is_tautology:
        qc.x(clause_ancilla)
        return

    # 3. Apply X to qubits backing POSITIVE literals.
    #    After these flips, "all controls = 1" exactly captures the unsat case.
    flip_targets = [var_qubits[v] for v, neg in distinct if not neg]
    for q in flip_targets:
        qc.x(q)

    # 4. MCX from the literals' variable qubits to the ancilla.
    #    After this, ancilla = 1 iff the clause is UNSATISFIED.
    controls = [var_qubits[v] for v, _ in distinct]
    qc.mcx(controls, clause_ancilla)

    # 5. Invert the meaning: ancilla = 1 iff the clause is SATISFIED.
    qc.x(clause_ancilla)

    # 6. Uncompute the X gates on the variable qubits so they're returned unchanged.
    for q in flip_targets:
        qc.x(q)

def build_oracle(n: int, clauses: List[Clause]) -> QuantumCircuit:
    """Construct the phase-flip oracle for a 3-SAT instance.

    Qubit layout (on the returned circuit):
      qubits 0 .. n-1         : variable qubits
      qubits n .. n+m-1       : clause ancillas (one per clause), clean on entry/exit
      qubit  n+m              : phase-kickback target, clean on entry/exit

    Returns a QuantumCircuit. Convert to a gate via .to_gate(label="oracle")
    when appending into a larger circuit.
    """
    m = len(clauses)
    var_qubits = list(range(n))
    clause_ancillas = list(range(n, n + m))
    target = n + m

    qc = QuantumCircuit(n + m + 1, name="oracle")

    # 1. Initialize target to |−⟩.
    qc.x(target)
    qc.h(target)

    # 2. Compute clause ancillas.
    for i, clause in enumerate(clauses):
        mark_clause(qc, clause, var_qubits, clause_ancillas[i])

    # 3. Phase kickback: |−⟩ on the target picks up a −1 iff all clause ancillas are 1.
    qc.mcx(clause_ancillas, target)

    # 4. Uncompute clause ancillas. Reverse order is the standard pattern.
    for i in reversed(range(m)):
        mark_clause(qc, clauses[i], var_qubits, clause_ancillas[i])

    # 5. Restore the target to |0⟩.
    qc.h(target)
    qc.x(target)

    return qc
