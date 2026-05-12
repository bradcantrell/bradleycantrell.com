#!/usr/bin/env python3
"""Optimize and rename dissertation chapter images for the web.

Usage:
  optimize_chapter_images.py <chapter_n> <mapping.json>

The mapping JSON maps figure label -> source file path and figure role:

  {
    "07_01": { "src": "/abs/path/to/source.jpg", "role": "hero" },
    "07_03": { "src": "/abs/path/to/source.svg", "role": "diagram" }
  }

Roles:
  hero / quote-spread / inline   --> raster (jpg). Hero/quote use 2400/4800.
                                     Inline uses 1600/3200.
  diagram                        --> svg, copied verbatim, renamed.

Output goes into:
  dissertation/img/<chapter_folder>/figure_<NN>_<NN>.{jpg,svg}
  dissertation/img/<chapter_folder>/figure_<NN>_<NN>@2x.jpg
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageOps

Image.MAX_IMAGE_PIXELS = 400_000_000  # allow large NEOM source plates

REPO = Path("/Users/bcantrell/Documents/sites/bradleycantrell.com")

CHAPTER_FOLDERS = {
    "01": "01_territory",
    "02": "02_adaptive_epistemologies",
    "03": "03_refractions",
    "04": "04_ecology_practice",
    "05": "05_tools",
    "06": "06_models",
    "07": "07_technogeographies",
    "08": "08_landscape_medium",
    "09": "09_interactions",
    "10": "10_generational_robots",
    "11": "11_cocreation",
    "12": "12_synoptic",
    "13": "13_vectors",
}

SIZES = {
    "hero":         {"1x": 2400, "2x": 4800, "quality": 82},
    "quote-spread": {"1x": 2400, "2x": 4800, "quality": 82},
    "inline":       {"1x": 1600, "2x": 3200, "quality": 82},
}


def fit_width(img: Image.Image, target_w: int) -> Image.Image:
    """Resize to target_w preserving aspect; do not upscale beyond source."""
    if img.width <= target_w:
        return img.copy()
    ratio = target_w / img.width
    return img.resize((target_w, max(1, round(img.height * ratio))), Image.LANCZOS)


def save_jpg(img: Image.Image, out_path: Path, quality: int) -> None:
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.save(out_path, "JPEG", quality=quality, optimize=True, progressive=True)


def process_raster(src: Path, role: str, label: str, out_dir: Path) -> list[Path]:
    cfg = SIZES[role]
    written: list[Path] = []
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)
        # 1x
        one_x = fit_width(im, cfg["1x"])
        p1 = out_dir / f"figure_{label}.jpg"
        save_jpg(one_x, p1, cfg["quality"])
        written.append(p1)
        # 2x only when source can support a meaningfully larger asset
        if im.width > cfg["1x"]:
            two_x = fit_width(im, cfg["2x"])
            p2 = out_dir / f"figure_{label}@2x.jpg"
            save_jpg(two_x, p2, cfg["quality"])
            written.append(p2)
    return written


def process_svg(src: Path, label: str, out_dir: Path) -> list[Path]:
    out = out_dir / f"figure_{label}.svg"
    shutil.copyfile(src, out)
    return [out]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("chapter", help="Chapter number, e.g. 07")
    ap.add_argument("mapping", help="Path to mapping JSON")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.chapter not in CHAPTER_FOLDERS:
        sys.exit(f"unknown chapter '{args.chapter}'")

    out_dir = REPO / "dissertation" / "img" / CHAPTER_FOLDERS[args.chapter]
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(args.mapping) as f:
        mapping = json.load(f)

    for label, info in mapping.items():
        src = Path(info["src"])
        role = info["role"]
        if not src.exists():
            print(f"  MISS  {label}  src missing: {src}")
            continue
        print(f"  {label}  {role:<13}  src={src.name}")
        if args.dry_run:
            continue
        if src.suffix.lower() == ".svg" or role == "diagram":
            written = process_svg(src, label, out_dir)
        else:
            written = process_raster(src, role, label, out_dir)
        for p in written:
            size_kb = p.stat().st_size / 1024
            print(f"        -> {p.name}  ({size_kb:,.0f} KB)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
