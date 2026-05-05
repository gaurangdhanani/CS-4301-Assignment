"""Classical reference implementation: evaluate assignments and brute-force count.

Used purely for testing and as ground truth against which to validate the
quantum oracle, Grover search, and quantum counting on small instances.
"""

from typing import List, Optional, Tuple, Union

Literal = Tuple[int, bool]
Clause = List[Literal]
Assignment = Union[str, List[int], Tuple[int, ...]]


def _to_bits(assignment: Assignment) -> List[int]:
    """Normalize an assignment in any accepted format to a list of 0/1 ints."""
    if isinstance(assignment, str):
        bits = [int(ch) for ch in assignment]
    else:
        bits = [int(b) for b in assignment]
    if any(b not in (0, 1) for b in bits):
        raise ValueError(f"assignment must contain only 0 and 1, got {assignment!r}")
    return bits


def evaluate(assignment: Assignment, clauses: List[Clause]) -> bool:
    """Return True iff `assignment` satisfies every clause.

    Bit i of the assignment is the value of variable x_i.
    """
    bits = _to_bits(assignment)
    for clause in clauses:
        satisfied = False
        for var_idx, is_negated in clause:
            if var_idx >= len(bits):
                raise ValueError(
                    f"variable index {var_idx} exceeds assignment length {len(bits)}"
                )
            value = bits[var_idx]
            # A literal is true if: positive and value=1, or negated and value=0.
            if (not is_negated and value == 1) or (is_negated and value == 0):
                satisfied = True
                break
        if not satisfied:
            return False
    return True


def _int_to_assignment(i: int, n: int) -> str:
    """Convert integer i in [0, 2^n) to an n-character string where character k
    is the value of x_k (i.e. bit k of i)."""
    return "".join(str((i >> k) & 1) for k in range(n))


def count_satisfying(
    n: int, clauses: List[Clause]
) -> Tuple[int, Optional[str]]:
    """Brute-force count the satisfying assignments.

    Returns (count, example) where `example` is one satisfying assignment as a
    string, or None if the formula is unsatisfiable.
    """
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")

    count = 0
    example: Optional[str] = None
    for i in range(1 << n):
        candidate = _int_to_assignment(i, n)
        if evaluate(candidate, clauses):
            count += 1
            if example is None:
                example = candidate
    return count, example
