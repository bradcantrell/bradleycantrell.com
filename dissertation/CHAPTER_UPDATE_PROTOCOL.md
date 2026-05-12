# Dissertation Chapter Update Protocol

This document records the Chapter 01 implementation in enough detail to
repeat the same process across the remaining dissertation chapters.

## Goal

Each dissertation chapter HTML page should:

- keep the existing chapter-page structure and navigation
- replace all legacy body content with content derived from the source
  DOCX, PDF, and `Links` assets
- follow the Chapter 01 visual and interaction model
- preserve the dissertation site aesthetic while using the PDF as the
  canonical source for figure placement, quote overlays, and pacing
- keep all figures in PDF order and aligned with their figure numbers

## Source Hierarchy

For each chapter, use the sources in this order:

1. `dissertation_source/docx/*.docx`
   This is the canonical chapter text. The figure list at the end of the
   DOCX is the canonical checklist of required figures.
2. `dissertation_source/chapters_figures/<chapter folder>/<chapter>.pdf`
   This is the canonical source for:
   - which images are hero images
   - which images have quotes overlaid
   - how full-width figures are sequenced in the chapter
   - how quotes and figure labels are positioned visually
3. `dissertation_source/chapters_figures/<chapter folder>/Links/*`
   This is the canonical source for figure assets. These should be
   staged into the web image folders and optimized for web delivery.

## Required Page Structure

Every dissertation chapter page should use:

- `<body class="chapter-page page-dissertation">`

This is important. The `page-dissertation` class prevents global
`style.css` section rules from constraining quote-image sections.
Without it, inline hero sections may fail to span correctly.

## Chapter 01 Implementation Pattern

Chapter 01 is now the reference implementation.

### Hero figure

The top hero uses:

- the actual figure image from the chapter asset folder
- a live HTML quote overlay
- the official figure-list caption text

For Chapter 01:

- `Figure 01_01` is the top hero
- quote is live HTML, not burned into the image
- caption text is:
  `Figure 01_01  The Mississippi River at dawn, aerial from 35,000 ft | Photo by Varun Ranganathan`

### Standard inline figures

Use normal `<figure class="ch-inline-figure">` or
`<figure class="ch-inline-figure ch-inline-figure--simple">` when the
PDF does not treat the image as a full-width quote plate.

Rules:

- include every figure listed in the DOCX figure list
- keep figures in the same sequence they appear in the PDF and in figure
  number order
- do not generate descriptive captions
- use only the official figure number and figure-list caption text
- keep SVG inversion only for actual `.svg` assets
- leave raster images un-inverted
- if the figure name includes `diagram` or `map`, keep it in the text
  flow as a standard inline figure rather than converting it to a
  full-width plate
- diagrams and maps should remain enlargeable through the shared figure
  modal behavior

### Inline quote-image panels

Use full-width quote-image sections when the PDF shows an image with an
overlaid quote.

For Chapter 01, these are:

- `Figure 01_04`
- `Figure 01_05`
- `Figure 01_07`
- `Figure 01_10`

These use:

- `<section class="ch-quote-panel">`
- a background image in `.ch-quote-panel__img`
- a framed quote box in `.ch-quote-panel__content`
- a left-aligned wrapped figure label block in
  `.ch-quote-panel__caption`

Important structural rule:

- quote panels must sit as siblings between `article.ch-content`
  sections, not nested inside the text column when they are meant to
  read as full-width plates

Behavior rule:

- any figure shown in the PDF with a quote overlaid should be treated as
  a full-width inline quote-image panel with parallax
- quote-overlay figures should not be converted to standard text-column
  figures unless the PDF clearly treats them that way

If they remain nested inside the article flow, they visually collapse
back toward the text column even when the CSS is otherwise correct.

## Figure Inclusion Checklist

For each chapter:

1. Extract the figure list from the end of the DOCX.
2. Confirm that every figure listed appears in the chapter HTML.
3. Confirm that figures appear in the same order as the PDF and in
   ascending figure-number order.
4. Confirm that each figure uses the correct figure-list caption text.
5. Confirm that figures shown as quote-overlay plates in the PDF are not
   rendered as standard column-width figures.
6. Confirm that figures with `diagram` or `map` in the figure name stay
   in the text flow and can be enlarged.
7. Confirm that no unlisted figures are inserted unless there is a clear
   chapter-specific reason and the user approves it.

For Chapter 01, all figures `01_01` through `01_10` are now present.

## Caption Rules

Use only the official figure text from the chapter figure list.

Do not:

- add generated descriptive blurbs
- add AI-written summaries
- add secondary narrative text under figures unless it exists in the
  official source

For quote-image panels:

- figure number and caption text should be left aligned
- caption block should have bounded width and wrap instead of colliding
  with the quote box
- longer captions should stack naturally in the left caption column

## Quote Rules

For images that include overlaid quotes in the PDF:

- quotes should be recreated as live HTML, not burned into the image
- quote text should be smaller than the attribution
- attribution should remain in the smaller sans-serif treatment used by
  the opener
- quote box styling should match the Chapter 01 opener

Chapter 01 quote treatment now uses the same visual grammar for:

- the top hero
- all inline quote-image panels

## Layout and CSS Rules

The core chapter styles live in:

- [`/Users/bcantrell/Documents/sites/bradleycantrell.com/dissertation/chapter.css`](/Users/bcantrell/Documents/sites/bradleycantrell.com/dissertation/chapter.css)

### Quote-panel rules established in Chapter 01

`.ch-quote-panel` now behaves like a hero-like spread:

- same chapter-width canvas as the opener
- same hero height variables:
  - `--ch-hero-h`
  - `--ch-hero-min`
- background image bleeds past the container with `inset: -10%`
- image crop is left-anchored
- overlay gradient matches the opener

`.ch-quote-panel__content`

- right-aligned framed quote box
- same blur, border, and shadow logic as the opener

`.ch-quote-panel__caption`

- left-aligned
- bounded width
- wraps long text
- does not overlap the quote box

### Important global CSS conflict

Global site CSS in [`/Users/bcantrell/Documents/sites/bradleycantrell.com/style.css`](/Users/bcantrell/Documents/sites/bradleycantrell.com/style.css)
contains two rules that interfere with dissertation quote panels:

1. `section { max-width: var(--max); margin: 0 auto; padding: ... }`
2. `body:not(.page-dissertation) section { background: ... !important; backdrop-filter: ... }`

Because quote-image plates are plain `section` elements, this global CSS
can keep them from spanning correctly unless the page body includes:

- `page-dissertation`

The chapter CSS also explicitly clears inherited section constraints on
`.ch-quote-panel`.

## Image Asset Rules

Raster images are produced by `scripts/optimize_chapter_images.py` from a
canonical source (either `dissertation_source/.../Links/<file>` or the
existing legacy file). All chapter figures follow this naming and sizing
convention:

- filename: `figure_<chapter>_<NN>.<ext>` (e.g. `figure_07_03.svg`,
  `figure_07_02.jpg`)
- a `figure_<chapter>_<NN>@2x.<ext>` retina variant is produced
  whenever the source is large enough to support a meaningfully larger
  image
- SVG diagrams are kept as SVG (single file, no @2x) and rendered with
  an in-page pan/zoom viewer (see Modal rules)

Target sizes:

- hero / quote-spread (full-width raster): `2400px` @ 1x, `4800px` @ 2x,
  JPG quality 82, progressive
- inline / backdrop figures: `1600px` @ 1x, `3200px` @ 2x

The active dissertation image folders live under:

- `dissertation/img/<chapter folder>/`

Use chapter-specific web image folders consistently. Do not commit
source-scale (10–100 MB) PNGs into these folders; the optimizer reads
the high-res source from `dissertation_source/` and writes only the
web-ready assets.

### Running the optimizer

For a single chapter:

```sh
python scripts/rename_chapter_figures.py <NN>
```

This script:

1. Parses the chapter HTML to find every figure reference (hero,
   quote-panel, backdrop, inline)
2. Resolves each ref's old src to the best available source — preferring
   `dissertation_source/<chapter>/Links/<basename>`, then versioned
   `<stem>_v<N>.svg` variants, then the legacy file
3. Runs `optimize_chapter_images.py` to write the new figure_NN_NN.*
   files
4. Rewrites the HTML to use the new filenames

The script is idempotent: re-running on a chapter that has already been
processed only handles any newly-added figure refs.

## Motion / Parallax Rules

The shared chapter interaction script lives at:

- [`/Users/bcantrell/Documents/sites/bradleycantrell.com/dissertation/chapter.js`](/Users/bcantrell/Documents/sites/bradleycantrell.com/dissertation/chapter.js)

Chapter 01 established the parallax pattern:

- top hero image scrolls upward slightly slower than the page
- backdrop figures use the same motion
- inline quote-image panels now use the same motion

This behavior is now shared through `chapter.js` and should not be
duplicated as one-off inline scripts in chapter HTML files.

Current parallax targets:

- `.ch-hero__bg`
- `.ch-backdrop__img`
- `.ch-quote-panel__img`

## Print / Modal Rules

Shared chapter interactions also include:

- print button injection
- print-image fallbacks for background-image sections
- image enlargement modal for non-hero inline figures, with two modes:
  - **raster figures** open in the standard `<img>` modal
  - **SVG diagrams** open in a pan/zoom modal backed by
    [`svg-pan-zoom`](dissertation/svg-pan-zoom.min.js), with `+ / − /
    reset` controls, scroll-wheel zoom, click-and-drag pan, and a
    dedicated close button. The SVG markup is fetched inline so labels
    stay crisp at any zoom level.

This includes:

- standard inline figures
- diagrams and maps in the text flow
- print fallbacks for quote-overlay panels, not just heroes and
  backdrops

These behaviors are already in `chapter.js` and should be preserved
across chapters. The `svg-pan-zoom` library is lazy-loaded the first
time an SVG figure is enlarged, so no per-page `<script>` tag is needed.

## Workflow For Remaining Chapters

There are two modes of chapter work:

### Mode A — restage figures only (idempotent)

Use when the chapter body is already correct and only the figure
references need to be brought in line with the new naming + sizing
convention. This is what `rename_chapter_figures.py` automates:

```sh
python scripts/rename_chapter_figures.py <NN>
```

The script parses the chapter HTML, resolves each old image src against
the canonical sources in `dissertation_source/`, runs the optimizer,
and rewrites every reference (hero, quote panel, backdrop, inline,
diagram) to `figure_NN_NN.{jpg,svg}`. It can be re-run safely.

### Mode B — full DOCX-driven rebuild

Use when the chapter body needs to be regenerated from the canonical
DOCX (e.g. after content edits). Chapter 07 is the reference for this
workflow:

1. Open the chapter DOCX and extract the body text with heading levels.
2. Extract the figure list from the end of the DOCX.
3. Open the chapter PDF and identify:
   - hero image
   - any quote-overlay spreads (full-width image + overlaid pull quote)
   - any backdrop / inline diagram pacing
   - exact figure order through the chapter
4. Build a mapping JSON of `figure_label -> {src, role}` and run
   `scripts/optimize_chapter_images.py <NN> mapping.json` to stage the
   `figure_NN_NN.{jpg,svg}` assets.
5. Author the chapter HTML body fresh:
   - keep the existing page shell (`<head>`, `<nav>`, sidebar, password
     gate, prev/next nav, footer)
   - place `<figure class="ch-inline-figure">` blocks inline in the
     correct paragraphs
   - place `<section class="ch-quote-panel">` blocks as siblings of
     `<article class="ch-content">` for quote-overlay spreads
   - use `<section class="ch-quote-panel ch-quote-panel--no-quote">`
     for full-bleed image plates with no overlaid quote
   - keep `diagram` and `map` figures in the text flow; they will pick
     up the SVG pan/zoom modal automatically
6. Use only the official figure-list text for captions.
7. Confirm `<body class="chapter-page page-dissertation">`.
8. Confirm parallax works through the shared `chapter.js`, not inline
   custom scripts.

## Chapter 01-Specific Notes

Chapter 01 now includes:

- hero:
  - `Figure 01_01`
- standard inline figures:
  - `Figure 01_02`
  - `Figure 01_03`
  - `Figure 01_06`
  - `Figure 01_08`
  - `Figure 01_09`
- full-width quote-image panels:
  - `Figure 01_04`
  - `Figure 01_05`
  - `Figure 01_07`
  - `Figure 01_10`

This should be treated as the visual and structural reference chapter
for the rest of the dissertation.

## Verification Checklist

Before considering a chapter complete:

- all figures from the DOCX figure list are present
- no required images are missing
- figure order matches the PDF and the figure numbering sequence
- quote-image plates match the PDF treatment
- any figure with a PDF quote overlay is a full-width quote-image panel
  with parallax
- any figure with `diagram` or `map` in its figure name remains in the
  text flow
- figure captions use only official figure-list text
- large raster assets are optimized
- SVG inversion applies only to SVG files
- quote panels span correctly and do not inherit global section
  constraints
- quote captions do not overlap the quote box
- parallax motion applies to the opener and any inline quote-image
  panels
- standard inline figures can be enlarged
- diagrams and maps can be enlarged
- print button and modal behavior still work
- print preview includes quote-overlay panels, not just the first hero

## Files Changed During Chapter 01 Pattern Development

The current reusable behavior depends on these files:

- [`/Users/bcantrell/Documents/sites/bradleycantrell.com/dissertation/01.html`](/Users/bcantrell/Documents/sites/bradleycantrell.com/dissertation/01.html)
- [`/Users/bcantrell/Documents/sites/bradleycantrell.com/dissertation/chapter.css`](/Users/bcantrell/Documents/sites/bradleycantrell.com/dissertation/chapter.css)
- [`/Users/bcantrell/Documents/sites/bradleycantrell.com/dissertation/chapter.js`](/Users/bcantrell/Documents/sites/bradleycantrell.com/dissertation/chapter.js)

If the remaining chapters are rebuilt programmatically, the generator
should reproduce the same rules instead of relying on Chapter 01-only
manual structure.
