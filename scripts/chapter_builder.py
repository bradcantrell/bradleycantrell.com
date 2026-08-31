#!/usr/bin/env python3
"""Generate a dissertation chapter HTML body from a chapter config.

A config is a dict with the following shape:

    {
      'chapter': '08',
      'folder': '08_landscape_medium',
      'docx': '08_Landscape_as_Medium.docx',
      'title': 'Landscape as Medium',
      'subtitle': 'The Model and the Site',
      'hero': {
          'figure': '08_01',
          'caption': 'Wetlands in the Pocomoke Sound, ...',
          'quote': '"The play of form ..."',
          'quote_source': 'Ursula K. Le Guin, <em>The Lathe of Heaven</em> (1971)',
      },
      'prev': ('07', 'Technogeographies'),
      'next': ('09', 'A Shifting Model'),
      'sidebar_diss': 'Adaptive Epistemologies<br>and Neo-Wilds',
      # Figures placed AFTER a given paragraph number (1-indexed, matching the
      # DOCX paragraph stream). Hero (figure 0) is implicit and not listed.
      'figures': [
          # (after_para, label, role, caption, [optional quote_text],
          #  [optional quote_source])
          (14, '08_02', 'quote-spread',
           'NEOM Technical Study, ...',
           '"Medium design ..."',
           'Keller Easterling, <em>Medium Design</em>'),
          (28, '08_04', 'diagram',
           'Territory as Assemblage Diagram | Bradley Cantrell'),
          ...
      ],
    }

Roles:
    'hero'         - implicit, baked into the hero header
    'quote-spread' - <section class="ch-quote-panel"> with overlay quote
    'no-quote'     - <section class="ch-quote-panel ch-quote-panel--no-quote">
    'inline'       - <figure class="ch-inline-figure">  (raster)
    'diagram'      - <figure class="ch-inline-figure ch-inline-figure--simple">
                     (SVG; uses simple caption layout)

The builder reads the DOCX, walks paragraphs, emits headings as <h2>/<h3>,
emits regular paragraphs as <p>, and inserts figure HTML at the requested
boundaries. It groups content into multiple <article class="ch-content">
sections — articles break and reopen around quote-spread panels (so those
panels become siblings of the article column, matching the chapter 01-07
visual pattern).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

REPO = Path('/Users/bcantrell/Documents/sites/bradleycantrell.com')
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

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

# Sidebar entries — chapter labels as they appear in the chapter nav.
SIDEBAR = [
    ('01.html', '01', 'Territory'),
    ('02.html', '02', 'Adaptive Epistemologies'),
    ('03.html', '03', 'Refractions'),
    ('04.html', '04', 'Ecology of Practice'),
    ('05.html', '05', 'Tools'),
    ('06.html', '06', 'Models'),
    ('07.html', '07', 'Technogeographies'),
    ('08.html', '08', 'Landscape as Medium'),
    ('09.html', '09', 'A Shifting Model'),
    ('10.html', '10', 'Generational Robots'),
    ('11.html', '11', 'Co-Creation'),
    ('12.html', '12', 'Synoptic View'),
    ('13.html', '13', 'Vectors'),
]


def parse_docx(path: Path):
    """Return list of (n, style, text) for each non-empty paragraph."""
    z = zipfile.ZipFile(path)
    xml = z.read('word/document.xml').decode('utf-8')
    root = ET.fromstring(xml)
    paras = []
    n = 0
    for p in root.iter(W + 'p'):
        style = p.find(W + 'pPr/' + W + 'pStyle')
        style_val = style.get(W + 'val') if (style is not None and style.get(W + 'val')) else ''
        runs = []
        for r in p.iter(W + 'r'):
            is_italic = False
            rpr = r.find(W + 'rPr')
            if rpr is not None and rpr.find(W + 'i') is not None:
                is_italic = True
            for t in r.iter(W + 't'):
                txt = t.text or ''
                runs.append(('i', txt) if is_italic else ('p', txt))
        if not runs:
            continue
        # Render with <em> markers
        out = ''
        for kind, t in runs:
            out += f'<em>{t}</em>' if kind == 'i' else t
        text = out.strip()
        if not text:
            continue
        # collapse runs of <em></em> joins
        text = re.sub(r'</em>(\s*)<em>', r'\1', text)
        n += 1
        paras.append((n, style_val, text))
    return paras


def slugify(s: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def render_heading(style: str, text: str) -> str:
    if style == 'Heading1':
        return ''  # title is in the hero
    if style == 'Heading2':
        return f'<h2 id="{slugify(text)}">{text}</h2>'
    if style == 'Heading3':
        return f'<h3 id="{slugify(text)}">{text}</h3>'
    return f'<p>{text}</p>'


def render_inline_figure(label, role, caption, folder):
    """Inline figure inside an article column."""
    classes = 'ch-inline-figure'
    if role == 'diagram':
        classes += ' ch-inline-figure--simple'
    ext_svg = (REPO / 'dissertation' / 'img' / folder / f'figure_{label}.svg').exists()
    ext = 'svg' if ext_svg else 'jpg'
    src = f'img/{folder}/figure_{label}.{ext}'
    # Use srcset for retina if @2x.jpg exists
    srcset_attr = ''
    if ext == 'jpg' and (REPO / 'dissertation' / 'img' / folder / f'figure_{label}@2x.jpg').exists():
        srcset_attr = f' srcset="img/{folder}/figure_{label}@2x.jpg 2x"'
    return (
        f'<figure class="{classes}">\n'
        f'  <img src="{src}"{srcset_attr} alt="Figure {label} — {caption}" loading="lazy">\n'
        f'  <figcaption>\n'
        f'    <span class="ch-inline-figure__num">Figure {label}</span>\n'
        f'    <span class="ch-inline-figure__caption">{caption}</span>\n'
        f'  </figcaption>\n'
        f'</figure>'
    )


def render_quote_panel(label, caption, folder, quote_text, quote_source):
    """Full-width <section class="ch-quote-panel"> sibling of articles."""
    src = f'img/{folder}/figure_{label}.jpg'
    return (
        f'<section class="ch-quote-panel">\n'
        f'  <div class="ch-quote-panel__img" style="background-image: url(\'{src}\'); background-position: center center;"></div>\n'
        f'  <div class="ch-quote-panel__content">\n'
        f'    <p class="ch-quote-panel__text">{quote_text}</p>\n'
        f'    <p class="ch-quote-panel__source">{quote_source}</p>\n'
        f'  </div>\n'
        f'  <div class="ch-quote-panel__caption">\n'
        f'    <div class="ch-quote-panel__caption-title"><span class="ch-inline-figure__num">Figure {label}</span> <span class="ch-inline-figure__caption">{caption}</span></div>\n'
        f'  </div>\n'
        f'</section>'
    )


def render_no_quote_panel(label, caption, folder):
    src = f'img/{folder}/figure_{label}.jpg'
    return (
        f'<section class="ch-quote-panel ch-quote-panel--no-quote">\n'
        f'  <div class="ch-quote-panel__img" style="background-image: url(\'{src}\'); background-position: center center;"></div>\n'
        f'  <div class="ch-quote-panel__caption">\n'
        f'    <div class="ch-quote-panel__caption-title"><span class="ch-inline-figure__num">Figure {label}</span> <span class="ch-inline-figure__caption">{caption}</span></div>\n'
        f'  </div>\n'
        f'</section>'
    )


def build_body(config, paras):
    """Stream the body HTML from paragraphs + figure placements."""
    chapter = config['chapter']
    folder = CHAPTER_FOLDERS[chapter]

    # Map after_para -> list of figure specs
    placements: dict[int, list[tuple]] = {}
    for spec in config['figures']:
        after = spec[0]
        placements.setdefault(after, []).append(spec[1:])

    parts = []
    in_article = False

    def open_article():
        nonlocal in_article
        if not in_article:
            parts.append('<article class="ch-content">')
            in_article = True

    def close_article():
        nonlocal in_article
        if in_article:
            parts.append('</article>')
            in_article = False

    # Identify the paragraph index where References starts. Everything from
    # that point gets emitted into the references aside.
    refs_para = None
    figs_para = None
    for n, style, text in paras:
        if style == 'Heading2' and text.strip() == 'References' and refs_para is None:
            refs_para = n
        if style == 'Heading2' and text.strip() == 'Figures' and figs_para is None:
            figs_para = n

    for n, style, text in paras:
        if refs_para and n >= refs_para:
            break
        # Body content
        if style.startswith('Heading'):
            open_article()
            html = render_heading(style, text)
            if html:
                parts.append(html)
        else:
            open_article()
            parts.append(f'<p>{text}</p>')

        # Insert any figures scheduled after this paragraph
        for spec in placements.get(n, []):
            role = spec[1]
            if role in ('quote-spread', 'no-quote'):
                # Break out of article so this is a sibling
                close_article()
                if role == 'quote-spread':
                    label, _, caption, qtext, qsource = spec
                    parts.append(render_quote_panel(label, caption, folder, qtext, qsource))
                else:
                    label, _, caption = spec[:3]
                    parts.append(render_no_quote_panel(label, caption, folder))
            else:
                open_article()
                label, _, caption = spec[:3]
                parts.append(render_inline_figure(label, role, caption, folder))

    close_article()

    # References aside
    if refs_para is not None:
        refs = ['<aside class="ch-references"><h2>References</h2>']
        for n, style, text in paras:
            if n < refs_para:
                continue
            if figs_para and n >= figs_para:
                break
            if n == refs_para:
                continue  # the heading itself
            refs.append(f'<p>{text}</p>')
        refs.append('</aside>')
        parts.append(
            '<div style="max-width:var(--ch-content);margin:0 auto;padding:0 clamp(1.5rem,5vw,3rem);">\n'
            + '\n'.join(refs)
            + '\n</div>'
        )

    # Figures aside
    if figs_para is not None:
        figs = ['<aside class="ch-references"><h2>Figures</h2>']
        for n, style, text in paras:
            if n < figs_para or n == figs_para:
                continue
            m = re.match(r'^Figure (\d+_\d+)\s*\.\s*(.+)$', text)
            if m:
                # Canonicalize to two-digit minor
                major, minor = m.group(1).split('_')
                label = f'{int(major):02d}_{int(minor):02d}'
                figs.append(f'<p><strong>Figure {label}</strong> . {m.group(2)}</p>')
            else:
                figs.append(f'<p>{text}</p>')
        figs.append('</aside>')
        parts.append(
            '<div style="max-width:var(--ch-content);margin:0 auto;padding:0 clamp(1.5rem,5vw,3rem);">\n'
            + '\n'.join(figs)
            + '\n</div>'
        )

    return '\n\n'.join(parts)


SHELL_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ch {chapter}: {title} — Adaptive Epistemologies and Neo-Wilds — Bradley Cantrell</title>
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
    <li><a href="/press.html">Press</a></li>
    <li><a href="/dissertation.html" class="active">Dissertation</a></li>
    <li><a href="/awards.html">Awards</a></li>
    <li><a href="/about.html">About</a></li>
  </ul>
</nav>

<div class="chapter-layout">

  <aside class="ch-sidebar">
    <div class="ch-sidebar__diss">{sidebar_diss}</div>
    <div class="ch-sidebar__divider"></div>
    <ul class="ch-sidebar__nav">
{sidebar_items}
        <li style="height:1px;background:var(--border);margin:0.75rem 0.5rem;"></li>
        <li><a href="glossary.html"><span class="ch-sidebar__num">—</span>Glossary</a></li>
        <li><a href="appendix-a.html"><span class="ch-sidebar__num">—</span>Appendix A</a></li>
        <li><a href="appendix-b.html"><span class="ch-sidebar__num">—</span>Appendix B</a></li>
    </ul>
  </aside>

  <main class="ch-main">
    <div class="ch-running">
      <span class="ch-running__text">Adaptive Epistemologies and Neo-Wilds &mdash; Chapter {chapter}</span>
    </div>

    <header class="ch-hero">
      <div class="ch-hero__bg" style="background-image: url('img/{folder}/figure_{hero_label}.jpg'); background-position: center center;"></div>
      <div class="ch-hero__content">
        <div class="ch-hero__label">Adaptive Epistemologies and Neo-Wilds</div>
        <div class="ch-hero__num">Chapter {chapter}</div>
        <h1 class="ch-hero__title">{title}</h1>
        <div class="ch-hero__subtitle">{subtitle}</div>
        <div class="ch-hero__caption">Figure {hero_label}  {hero_caption}</div>
      </div>
      <aside class="ch-hero__quote-box">
        <p class="ch-hero__quote-text">{hero_quote}</p>
        <p class="ch-hero__quote-source">{hero_quote_source}</p>
      </aside>
    </header>

    {body}

    <nav class="ch-nav"><a href="{prev_href}" class="ch-nav__item ch-nav__item--prev">
      <span class="ch-nav__label">← Previous</span>
      <span class="ch-nav__title">Ch {prev_num}: {prev_title}</span>
    </a><a href="{next_href}" class="ch-nav__item ch-nav__item--next">
      <span class="ch-nav__label">Next →</span>
      <span class="ch-nav__title">Ch {next_num}: {next_title}</span>
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


def build_chapter(config):
    chapter = config['chapter']
    folder = CHAPTER_FOLDERS[chapter]
    docx = REPO / 'dissertation_source' / 'docx' / config['docx']
    paras = parse_docx(docx)
    body = build_body(config, paras)

    # Build sidebar items
    sidebar_items = []
    for href, num, name in SIDEBAR:
        cls = ' class="active"' if num == chapter else ''
        sidebar_items.append(
            f'        <li><a href="{href}"{cls}><span class="ch-sidebar__num">{num}</span>{name}</a></li>'
        )

    prev_num, prev_title = config['prev']
    next_num, next_title = config['next']

    html = SHELL_TEMPLATE.format(
        chapter=chapter,
        title=config['title'],
        subtitle=config['subtitle'],
        sidebar_diss=config.get('sidebar_diss', 'Adaptive Epistemologies<br>and Neo-Wilds'),
        sidebar_items='\n'.join(sidebar_items),
        folder=folder,
        hero_label=config['hero']['figure'],
        hero_caption=config['hero']['caption'],
        hero_quote=config['hero']['quote'],
        hero_quote_source=config['hero']['quote_source'],
        body=body,
        prev_href=f'{prev_num}.html',
        prev_num=prev_num,
        prev_title=prev_title,
        next_href=f'{next_num}.html' if next_num != 'glossary' else 'glossary.html',
        next_num=next_num,
        next_title=next_title,
    )

    out = REPO / 'dissertation' / f'{chapter}.html'
    out.write_text(html)
    print(f'  wrote {out} ({len(html)} bytes)')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('config', help='path to chapter config JSON')
    args = ap.parse_args()
    config = json.loads(Path(args.config).read_text())
    build_chapter(config)


if __name__ == '__main__':
    sys.exit(main() or 0)
