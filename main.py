"""Entry point: parse a 3-SAT input file, run quantum counting and Grover search,
and print a satisfying assignment plus an estimate of the number of solutions."""

import sys


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_file>", file=sys.stderr)
        sys.exit(1)
    input_path = sys.argv[1]
    # TODO: parse, build oracle, run counting, run Grover, print results.
    print(f"(stub) would process: {input_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
