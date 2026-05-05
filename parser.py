"""Read a 3-SAT input file and produce a clean internal representation."""

from typing import List, Tuple

# A literal is (variable_index, is_negated).
Literal = Tuple[int, bool]
# A clause is a list of three literals.
Clause = List[Literal]


def _parse_literal(token: str) -> Literal:
    """Parse a single token like '0', '2', or '-0' into (var_index, is_negated).

    We must inspect the leading '-' before calling int(), because int('-0') == 0
    silently loses the negation on variable 0.
    """
    token = token.strip()
    if not token:
        raise ValueError("empty literal")

    is_negated = token.startswith("-")
    digits = token[1:] if is_negated else token

    if not digits.isdigit():
        raise ValueError(f"literal {token!r} is not an integer")

    return int(digits), is_negated


def parse(filename: str) -> Tuple[int, List[Clause]]:
    """Read a 3-SAT instance from a file.

    Returns (n, clauses) where n is the number of variables and each clause is
    a list of three (var_index, is_negated) tuples.

    Raises ValueError with a readable message on malformed input.
    """
    with open(filename, "r") as f:
        # Strip whitespace and drop blank lines.
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        raise ValueError(f"input file {filename!r} is empty")

    # Line 1: the variable count.
    try:
        n = int(lines[0])
    except ValueError:
        raise ValueError(
            f"first line must be an integer (number of variables), got {lines[0]!r}"
        )
    if n < 1:
        raise ValueError(f"number of variables must be >= 1, got {n}")

    # Remaining lines: clauses.
    clauses: List[Clause] = []
    for line_no, line in enumerate(lines[1:], start=2):
        tokens = line.split()
        if len(tokens) != 3:
            raise ValueError(
                f"line {line_no}: expected 3 literals, got {len(tokens)}: {line!r}"
            )

        clause: Clause = []
        for tok in tokens:
            try:
                var, neg = _parse_literal(tok)
            except ValueError as e:
                raise ValueError(f"line {line_no}: {e}") from None

            if not (0 <= var < n):
                raise ValueError(
                    f"line {line_no}: variable index {var} out of range [0, {n})"
                )
            clause.append((var, neg))

        clauses.append(clause)

    return n, clauses
