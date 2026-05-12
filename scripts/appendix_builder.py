#!/usr/bin/env python3
"""Generate the appendix-a / appendix-b / glossary HTML pages.

Same overall page shell as the chapter pages, but without chapter numbers
and with custom figure placement. SVG diagrams are rendered as inline
figures so they pick up the dark-mode inversion + click-to-zoom modal,
and a raster JPG hero opens the page.

Usage:
    appendix_builder.py aa   # builds dissertation/appendix-a.html
    appendix_builder.py bb   # builds dissertation/appendix-b.html
    appendix_builder.py gg   # builds dissertation/glossary.html
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Reuse parse_docx + slugify helpers
sys.path.insert(0, str(Path(__file__).parent))
from chapter_builder import parse_docx, slugify, SHELL_TEMPLATE, SIDEBAR

REPO = Path('/Users/bcantrell/Documents/sites/bradleycantrell.com')


CONFIGS = {
    'aa': {
        'docx': 'AA_Appendix.docx',
        'out': 'appendix-a.html',
        'title': 'Appendix A',
        'subtitle': 'Project Catalog',
        'hero_img': 'img/AA_Appendix/AA.jpg',
        'hero_caption': 'Psuedo Ecologies . Salt Flats | Bradley Cantrell',
        'running': 'Adaptive Epistemologies and Neo-Wilds &mdash; Appendix A',
        'active_href': 'appendix-a.html',
        # Figures: list of (after_para_index, src, caption)
        'figures': [
            # Two diagrams just before the H2 "Computational Practice Archive: Codebase"
            (483, 'img/AA_Appendix/chapter-map.svg',
             'Chapter Map | Bradley Cantrell'),
            (483, 'img/AA_Appendix/F-02_RefractionsIndex_v1_2.svg',
             'Refraction Index | Bradley Cantrell'),
            # File inventory diagram at the end of the codebase entries
            (519, 'img/AA_Appendix/file-inventory.svg',
             'File Inventory, Custom computational work in the archive, 2009&ndash;2017 | Bradley Cantrell'),
        ],
        # Paragraph indices to skip during rendering (placeholder text for
        # figures we have now relocated).
        'skip_paras': {489},
        # Prev / Next nav
        'prev': ('glossary.html', '', 'Glossary'),
        'next': ('appendix-b.html', '', 'Appendix B'),
    },
    'bb': {
        'docx': 'BB_Appendix.docx',
        'out': 'appendix-b.html',
        'title': 'Appendix B',
        'subtitle': 'Obstacles',
        'hero_img': 'img/BB_Appendix/BB.jpg',
        'hero_caption': 'Psuedo Ecologies . Migrations | Bradley Cantrell',
        'running': 'Adaptive Epistemologies and Neo-Wilds &mdash; Appendix B',
        'active_href': 'appendix-b.html',
        'figures': [
            # SVG near the end — just before the References heading.
            (55, 'img/BB_Appendix/F-B02_StructuralIncompatibility_v1.svg',
             'Structural Incompatibility | Bradley Cantrell'),
        ],
        'skip_paras': set(),
        'prev': ('appendix-a.html', '', 'Appendix A'),
        'next': ('../dissertation.html', '', 'Overview'),
    },
    'gg': {
        'docx': 'GG_Glossary.docx',
        'out': 'glossary.html',
        'title': 'Glossary',
        'subtitle': 'Adaptive Epistemologies and Neo-Wilds',
        'hero_img': 'img/GG_Glossary/GG.jpg',
        'hero_caption': 'Psuedo Ecologies . Riparian Corridor | Bradley Cantrell',
        'running': 'Adaptive Epistemologies and Neo-Wilds &mdash; Glossary',
        'active_href': 'glossary.html',
        'figures': [],
        'skip_paras': set(),
        'prev': ('13.html', '13', 'Vectors'),
        'next': ('appendix-a.html', '', 'Appendix A'),
    },
}


def render_heading(style: str, text: str) -> str:
    if style == 'Heading1':
        return ''  # title is in the hero
    if style == 'Heading2':
        return f'<h2 id="{slugify(text)}">{text}</h2>'
    if style == 'Heading3':
        return f'<h3 id="{slugify(text)}">{text}</h3>'
    return f'<p>{text}</p>'


def render_svg_figure(src: str, caption: str) -> str:
    """Inline SVG diagram with simple caption layout (matches chapter
    diagrams: inverted in CSS, opens in the pan/zoom modal on click)."""
    return (
        f'<figure class="ch-inline-figure ch-inline-figure--simple">\n'
        f'  <img src="{src}" alt="{caption}" loading="lazy">\n'
        f'  <figcaption>\n'
        f'    <span class="ch-inline-figure__caption">{caption}</span>\n'
        f'  </figcaption>\n'
        f'</figure>'
    )


def build_body(cfg, paras):
    refs_para = None
    for n, style, text in paras:
        if style == 'Heading2' and text.strip() == 'References' and refs_para is None:
            refs_para = n

    placements: dict[int, list[tuple]] = {}
    for after, src, caption in cfg['figures']:
        placements.setdefault(after, []).append((src, caption))

    parts = ['<article class="ch-content">']

    for n, style, text in paras:
        if refs_para and n >= refs_para:
            break
        if n in cfg['skip_paras']:
            # placeholder figure callout text we have replaced with the actual SVG
            continue
        # Skip the Heading1 (handled by hero) and the first Heading2 (handled by subtitle)
        if style == 'Heading1':
            continue
        if style == 'Heading2' and text.strip() == cfg['subtitle']:
            continue
        html = render_heading(style, text)
        if html:
            parts.append(html)
        for src, caption in placements.get(n, []):
            parts.append(render_svg_figure(src, caption))

    parts.append('</article>')

    # References aside if present
    if refs_para is not None:
        refs = ['<aside class="ch-references"><h2>References</h2>']
        for n, style, text in paras:
            if n < refs_para or n == refs_para:
                continue
            refs.append(f'<p>{text}</p>')
        refs.append('</aside>')
        parts.append(
            '<div style="max-width:var(--ch-content);margin:0 auto;padding:0 clamp(1.5rem,5vw,3rem);">\n'
            + '\n'.join(refs)
            + '\n</div>'
        )

    return '\n\n'.join(parts)


def build_section(key):
    cfg = CONFIGS[key]
    docx = REPO / 'dissertation_source' / 'docx' / cfg['docx']
    paras = parse_docx(docx)
    body = build_body(cfg, paras)

    # Build sidebar
    items = []
    for href, num, name in SIDEBAR:
        items.append(
            f'        <li><a href="{href}"><span class="ch-sidebar__num">{num}</span>{name}</a></li>'
        )
    items.append('        <li style="height:1px;background:var(--border);margin:0.75rem 0.5rem;"></li>')
    for href, name in [('glossary.html', 'Glossary'),
                       ('appendix-a.html', 'Appendix A'),
                       ('appendix-b.html', 'Appendix B')]:
        cls = ' class="active"' if href == cfg['active_href'] else ''
        items.append(
            f'        <li><a href="{href}"{cls}><span class="ch-sidebar__num">—</span>{name}</a></li>'
        )

    prev_href, prev_num, prev_title = cfg['prev']
    next_href, next_num, next_title = cfg['next']

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{cfg['title']} &mdash; Adaptive Epistemologies and Neo-Wilds &mdash; Bradley Cantrell</title>
  <link rel="icon" type="image/x-icon" href="/favicon.ico">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <link rel="stylesheet" href="/style.css">
  <link rel="stylesheet" href="chapter.css">
</head>
<body class="chapter-page page-dissertation" data-protected="false">

<nav>
  <div class="nav-name"><a href="/">Bradley <span>Cantrell</span></a></div>
  <ul class="nav-links">
    <li><a href="/work.html">Work</a></li>
    <li><a href="/writing.html">Writing</a></li>
    <li><a href="/teaching.html">Teaching</a></li>
    <li><a href="/lectures.html">Lectures</a></li>
    <li><a href="/dissertation.html" class="active">Dissertation</a></li>
    <li><a href="/awards.html">Awards</a></li>
    <li><a href="/about.html">About</a></li>
  </ul>
</nav>

<div class="chapter-layout">

  <aside class="ch-sidebar">
    <div class="ch-sidebar__diss">Adaptive Epistemologies<br>and Neo-Wilds</div>
    <div class="ch-sidebar__divider"></div>
    <ul class="ch-sidebar__nav">
{chr(10).join(items)}
    </ul>
  </aside>

  <main class="ch-main">
    <div class="ch-running">
      <span class="ch-running__text">{cfg['running']}</span>
    </div>

    <header class="ch-hero">
      <div class="ch-hero__bg" style="background-image: url('{cfg['hero_img']}'); background-position: center center;"></div>
      <div class="ch-hero__content">
        <div class="ch-hero__label">Adaptive Epistemologies and Neo-Wilds</div>
        <h1 class="ch-hero__title">{cfg['title']}</h1>
        <div class="ch-hero__subtitle">{cfg['subtitle']}</div>
        <div class="ch-hero__caption">{cfg['hero_caption']}</div>
      </div>
    </header>

    {body}

    <nav class="ch-nav"><a href="{prev_href}" class="ch-nav__item ch-nav__item--prev">
      <span class="ch-nav__label">← Previous</span>
      <span class="ch-nav__title">{prev_title}</span>
    </a><a href="{next_href}" class="ch-nav__item ch-nav__item--next">
      <span class="ch-nav__label">Next →</span>
      <span class="ch-nav__title">{next_title}</span>
    </a></nav>

    <footer class="ch-footer">
      <p>Bradley Cantrell &middot; <a href="/">bradleycantrell.com</a></p>
      <p><a href="/dissertation.html">&larr; Dissertation overview</a></p>
    </footer>
  </main>
</div>

<script src="chapter.js"></script>
</body>
</html>
'''
    out = REPO / 'dissertation' / cfg['out']
    out.write_text(html)
    print(f'  wrote {out} ({len(html)} bytes)')


def main():
    if len(sys.argv) > 1:
        keys = sys.argv[1:]
    else:
        keys = ['aa', 'bb', 'gg']
    for k in keys:
        if k not in CONFIGS:
            print(f'unknown: {k}')
            continue
        build_section(k)


if __name__ == '__main__':
    main()
