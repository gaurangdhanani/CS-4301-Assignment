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
