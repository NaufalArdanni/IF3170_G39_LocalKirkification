"""Command-line entry point: ``uv run mejiro-express <command>``."""

import argparse
from collections.abc import Sequence
from pathlib import Path

from mejiro_express import data, demo, visualize


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser with its three sub-commands."""
    parser = argparse.ArgumentParser(
        prog="mejiro-express",
        description="Local search for container loading (Tugas Besar 1 IF3170 AI).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="write a random problem instance as JSON")
    gen.add_argument("--n", type=int, default=30, help="number of packages")
    gen.add_argument("--seed", type=int, default=2026, help="seed of the generator")
    gen.add_argument(
        "--output",
        type=Path,
        default=data.DATA_PATH,
        help="where to write the instance (default: data/packages.json)",
    )

    sub.add_parser("run", help="run every experiment and write output/*.json")
    sub.add_parser("visualize", help="render output/*.json into output/plots/")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run one sub-command and return the process exit code."""
    args = build_parser().parse_args(argv)
    if args.command == "generate":
        path = data.generate(path=args.output, n=args.n, seed=args.seed)
        print(f"written to {path}")
    elif args.command == "run":
        demo.main()
    else:
        visualize.main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
