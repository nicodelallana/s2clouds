"""Command line interface for s2clouds."""

import argparse
import sys
from typing import Sequence

from s2clouds import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create command line arguments parser."""
    parser = argparse.ArgumentParser(
        prog="s2clouds",
        description="Cloud height estimation from Sentinel-2 inter-band parallax.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)
    _ = args
    return 0


if __name__ == "__main__":
    sys.exit(main())
