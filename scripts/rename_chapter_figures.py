#!/usr/bin/env python3
"""Rename a chapter's existing figures into the figure_NN_NN.* convention.

For each chapter, this script:
  1. Parses the chapter HTML to find every figure reference, capturing its
     figure number, img src, and structural role (hero, quote-spread,
     no-quote spread, or inline).
  2. Resolves each img src to the highest-resolution source available
     (preferring dissertation_source/.../Links/<name> over the existing
     dissertation/img/<chapter>/<name>).
  3. Runs optimize_chapter_images.py against a generated mapping JSON to
     produce figure_NN_NN.* outputs.
  4. Rewrites the chapter HTML so every old src is replaced with the new
     figure_NN_NN.* path.

Usage:
  rename_chapter_figures.py <chapter NN> [--dry-run]
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path('/Users/bcantrell/Documents/sites/bradleycantrell.com')

CHAPTER_FOLDERS = {
    '01': '01_territory',
    '02': '02_adaptive_epistemologies',
    '03': '03_refractions',
    '04': '04_ecology_practice',
    '05': '05_tools',
    '06': '06_models',
    '07': '07_technogeographies',
    '08': '08_landscape_medium',
    '09': '09_interactions',
    '10': '10_generational_robots',
    '11': '11_cocreation',
    '12': '12_synoptic',
    '13': '13_vectors',
}

# Map ch NN to its source folder name in dissertation_source/chapters_figures/
# (slash-separated names with spaces preserved as filesystem entries).
SOURCE_FOLDERS = {
    '01': '01_Territory_A_Formed_Condition Folder',
    '02': '02_Adaptive_Epistemologies Folder',
    '03': '03_Refractions Folder',
    '04': '04_Ecology of Practice Folder',
    '05': '05_Tools Folder',
    '06': '06_Models Folder',
    '07': '07_Technogeographies Folder',
    '08': '08_Landscape as Medium Folder',
    '09': '09_Interactions Folder',
    '10': '10_Generational_Robots Folder',
    '11': '11_CoCreation Folder',
    '12': '12_Synoptic_Views Folder',
    '13': '13_Vectors Folder',
}


def parse_chapter_figures(html_path: Path, chapter: str):
    """Yield dicts {label, src, role, html_pos} for figures in the chapter HTML.

    Roles:
      hero          : <header class="ch-hero">
      quote-spread  : <section class="ch-quote-panel"> (no --no-quote modifier)
      quote-spread  : <section class="ch-quote-panel ch-quote-panel--no-quote">
                      (still raster; treated the same)
      inline        : <figure class="ch-inline-figure">  / --simple
      diagram       : same as inline but src ends in .svg
    """
    html = html_path.read_text()
    results = []

    fignum_rx = re.compile(r'Figure (\d{1,2}_\d{1,2})')
    # 1) Hero
    m = re.search(
        r'<header class="ch-hero">.*?<div class="ch-hero__bg"[^>]*background-image:\s*url\(\'([^\']+)\'',
        html,
        re.S,
    )
    if m:
        src = m.group(1)
        # Hero figure number is always NN_01 (first figure).
        results.append({'label': f'{chapter}_01', 'src': src, 'role': 'hero'})

    # 2) Quote panels (in order)
    # We need each panel's figure number which comes from its
    # ch-quote-panel__caption-title block.
    panel_rx = re.compile(
        r'<section class="ch-quote-panel[^"]*">.*?</section>', re.S
    )
    for panel_match in panel_rx.finditer(html):
        panel = panel_match.group(0)
        bg = re.search(r"ch-quote-panel__img[^>]*url\('([^']+)'", panel)
        num = re.search(r'Figure (\d{1,2}_\d{1,2})', panel)
        if bg and num:
            results.append({
                'label': num.group(1),
                'src': bg.group(1),
                'role': 'quote-spread',
            })

    # 2b) Atmospheric backdrop sections (chapters 02-03 use these).
    # The top-level container is exactly `<div class="ch-backdrop">` (or with a
    # variant modifier). Match only that, not child elements like
    # `ch-backdrop__img` whose names also start with "ch-backdrop".
    backdrop_open_rx = re.compile(
        r'<div class="ch-backdrop(?:[\s|"][^"]*)?"(?:[^>]*)>', re.S
    )
    opens = [m.start() for m in backdrop_open_rx.finditer(html) if m.group(0).startswith('<div class="ch-backdrop"') or re.match(r'<div class="ch-backdrop(?:--[a-z]+)?"', m.group(0))]
    for start in opens:
        # Read forward until the next top-level backdrop OR a sibling section/article.
        next_boundary = min(
            (p for p in [
                html.find('<section', start + 1),
                html.find('<article', start + 1),
                html.find('<div class="ch-backdrop"', start + 1),
                html.find('<nav class="ch-nav"', start + 1),
                len(html),
            ] if p > start),
            default=len(html),
        )
        block = html[start:next_boundary]
        bg = re.search(r"ch-backdrop__img[^>]*url\('([^']+)'", block)
        num = re.search(r'Figure (\d{1,2}_\d{1,2})', block)
        if bg and num:
            results.append({
                'label': num.group(1),
                'src': bg.group(1),
                'role': 'quote-spread',
            })

    # 3) Inline figures (in order)
    fig_rx = re.compile(r'<figure class="ch-inline-figure[^"]*">.*?</figure>', re.S)
    for f_match in fig_rx.finditer(html):
        fig = f_match.group(0)
        src = re.search(r'<img[^>]*\bsrc="([^"]+)"', fig)
        num = re.search(r'Figure (\d{1,2}_\d{1,2})', fig)
        if src and num:
            is_svg = src.group(1).lower().endswith('.svg')
            results.append({
                'label': num.group(1),
                'src': src.group(1),
                'role': 'diagram' if is_svg else 'inline',
            })

    # Canonicalize labels: ensure two-digit chapter and minor (e.g. 10_1 -> 10_01)
    for r in results:
        major, minor = r['label'].split('_')
        r['label'] = f'{int(major):02d}_{int(minor):02d}'
    # Return ALL occurrences (dedupe is done downstream when picking the
    # canonical source for the optimizer).
    return results


EXT_ORDER = ['.svg', '.png', '.jpg', '.jpeg', '.tif', '.tiff']


def resolve_source(src_in_html: str, chapter: str) -> Path | None:
    """Find the best available source file for this figure.

    Preference order:
      1. dissertation_source/.../<chapter>/Links/<basename>  (exact filename)
      2. dissertation_source/.../<chapter>/Links/<stem>.<ext>  (same stem,
         preferring svg > png > jpg)
      3. dissertation_source/.../<chapter>/Links/<stem>_v*.<ext>  (versioned
         updates of vector diagrams; pick the one with the highest v number,
         again preferring .svg over rasters)
      4. dissertation/img/<chapter>/<basename>  (legacy fallback)
    """
    basename = Path(src_in_html).name
    stem = Path(src_in_html).stem

    source_links = REPO / 'dissertation_source' / 'chapters_figures' / SOURCE_FOLDERS[chapter] / 'Links'
    legacy_img = REPO / 'dissertation' / 'img' / CHAPTER_FOLDERS[chapter]

    if source_links.exists():
        # 1. exact basename
        cand = source_links / basename
        if cand.exists():
            return cand
        # 2. same stem, any extension (preferred order)
        for ext in EXT_ORDER:
            cand = source_links / f'{stem}{ext}'
            if cand.exists():
                return cand
        # 3. stem with a _vN... suffix (e.g. foo -> foo_v2, foo_v3_spread)
        candidates = []
        rx = re.compile(re.escape(stem) + r'_v\d+', re.IGNORECASE)
        for f in source_links.iterdir():
            if f.is_file() and rx.match(f.stem) and f.suffix.lower() != '.ai':
                candidates.append(f)
        if candidates:
            # Prefer svg, then highest version number
            def sort_key(p):
                ext_rank = EXT_ORDER.index(p.suffix.lower()) if p.suffix.lower() in EXT_ORDER else len(EXT_ORDER)
                vmatch = re.search(r'_v(\d+)', p.stem)
                vnum = int(vmatch.group(1)) if vmatch else 0
                # lower ext_rank is preferred, higher vnum is preferred
                return (ext_rank, -vnum)
            candidates.sort(key=sort_key)
            return candidates[0]

    # 4. legacy fallbacks
    cand = legacy_img / basename
    if cand.exists():
        return cand
    # The whole-repo legacy: src may be img/hero_quotes/NN.jpg, img/<other_chapter>/...
    # Try the explicit dissertation/<src_in_html> path.
    cand = REPO / 'dissertation' / src_in_html
    if cand.exists():
        return cand
    return None


def build_mapping(figures, chapter):
    """Build optimizer mapping JSON.

    For each figure label, pick the canonical source by priority:
       inline/diagram > quote-spread > hero
    Inline figures generally point at the real figure asset, while heroes
    sometimes point at a decorative hero-quote image.
    """
    # Already-renamed pattern (idempotent re-runs should skip these).
    already_pat = re.compile(r'^figure_\d{2}_\d{2}(\@2x)?\.[a-z]+$', re.I)
    ROLE_PRIORITY = {'inline': 3, 'diagram': 3, 'quote-spread': 2, 'hero': 1}

    by_label: dict[str, list[dict]] = {}
    for fig in figures:
        if already_pat.match(Path(fig['src']).name):
            continue
        by_label.setdefault(fig['label'], []).append(fig)

    mapping = {}
    unresolved = []
    for label, items in by_label.items():
        # Order by descending priority, then by parse order
        items.sort(key=lambda f: -ROLE_PRIORITY.get(f['role'], 0))
        for fig in items:
            src = resolve_source(fig['src'], chapter)
            if src is None:
                continue
            role = fig['role']
            if src.suffix.lower() == '.svg':
                role = 'diagram'
            mapping[label] = {'src': str(src), 'role': role}
            break
        else:
            unresolved.append((label, items[0]['src']))
    return mapping, unresolved


def rewrite_html(html_path: Path, figures, chapter):
    """Replace every fig['src'] in the HTML with the new figure_NN_NN.* path.

    Iterates ALL parsed figure occurrences (not just deduped). Each unique
    old src gets replaced once. Chooses the new extension based on which
    output file exists in the chapter image folder.
    """
    html = html_path.read_text()
    chapter_folder = CHAPTER_FOLDERS[chapter]
    folder_url = f'img/{chapter_folder}/'
    out_dir = REPO / 'dissertation' / 'img' / chapter_folder

    seen_old: set[str] = set()
    for fig in figures:
        label = fig['label']
        old_src = fig['src']
        if old_src in seen_old:
            continue
        seen_old.add(old_src)
        new_svg = out_dir / f'figure_{label}.svg'
        new_jpg = out_dir / f'figure_{label}.jpg'
        if new_svg.exists():
            new_name = f'figure_{label}.svg'
        elif new_jpg.exists():
            new_name = f'figure_{label}.jpg'
        else:
            continue
        new_src = f'{folder_url}{new_name}'
        html = html.replace(old_src, new_src)
    html_path.write_text(html)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('chapter')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    ch = args.chapter
    if ch not in CHAPTER_FOLDERS:
        sys.exit(f'unknown chapter {ch!r}')

    html_path = REPO / 'dissertation' / f'{ch}.html'
    figures = parse_chapter_figures(html_path, ch)
    print(f'Chapter {ch}: found {len(figures)} figures')

    mapping, unresolved = build_mapping(figures, ch)
    for fig in figures:
        info = mapping.get(fig['label'])
        if info:
            print(f"  {fig['label']:>6}  {info['role']:<13}  src={Path(info['src']).name}")
        else:
            print(f"  {fig['label']:>6}  UNRESOLVED  src={fig['src']}")
    if unresolved and not args.dry_run:
        print(f'\n!! {len(unresolved)} figures could not be resolved; aborting.')
        for label, src in unresolved:
            print(f'   {label}: {src}')
        sys.exit(2)

    mapping_path = REPO / '.claude' / f'tmp_ch{ch}_mapping.json'
    mapping_path.parent.mkdir(exist_ok=True)
    mapping_path.write_text(json.dumps(mapping, indent=2))

    if args.dry_run:
        print(f'\n(dry-run) wrote mapping to {mapping_path}')
        return 0

    # Run optimizer (always co-located with this script)
    script = Path(__file__).parent / 'optimize_chapter_images.py'
    subprocess.run(
        ['/tmp/diss_env/bin/python', str(script), ch, str(mapping_path)],
        check=True,
    )

    # Rewrite HTML
    rewrite_html(html_path, figures, ch)
    print(f'\nRewrote {html_path}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
