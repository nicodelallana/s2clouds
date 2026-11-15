"""Command line interface for s2clouds."""

import argparse
import sys
from pathlib import Path
from typing import Sequence

from s2clouds import __version__
from s2clouds.io_stac import (
    crop_scene_bands,
    get_stac_item,
    load_scene_config,
)


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

    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # Subcommand: download
    download_parser = subparsers.add_parser(
        "download",
        help="Download and crop Sentinel-2 bands from STAC COG assets",
    )
    download_parser.add_argument(
        "--config",
        "-c",
        required=True,
        type=Path,
        help="Path to TOML scene configuration file",
    )
    download_parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("data/crop.tif"),
        help="Destination path for cropped GeoTIFF",
    )

    return parser


def handle_download(args: argparse.Namespace) -> int:
    """Execute download subcommand."""
    config = load_scene_config(args.config)
    scene_cfg = config["scene"]
    roi_cfg = config["roi"]
    bands_cfg = config.get("bands", {})

    item_id = scene_cfg["id"]
    collection = scene_cfg.get("collection", "sentinel-2-l2a")
    stac_url = scene_cfg.get("stac_url", "https://earth-search.aws.element84.com/v1")
    bands = bands_cfg.get("names", ["B02", "B03", "B04"])
    bbox = tuple(roi_cfg["bbox"])

    print(f"Fetching STAC metadata for item '{item_id}'...")
    item = get_stac_item(item_id, collection=collection, stac_url=stac_url)

    print(f"Downloading and cropping bands {bands} to {args.output}...")
    saved_path = crop_scene_bands(item, bands, bbox, args.output)
    print(f"Successfully saved crop to {saved_path}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.subcommand == "download":
        return handle_download(args)

    if args.subcommand is None:
        parser.print_help()
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
