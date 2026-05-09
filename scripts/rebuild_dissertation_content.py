#!/usr/bin/env python3

import re
import subprocess
from pathlib import Path


ROOT = Path("/Users/bcantrell/Documents/sites/bradleycantrell.com")
DOCX_DIR = ROOT / "dissertation_source" / "docx"
HTML_DIR = ROOT / "dissertation"

PAGE_MAP = {
    "01_Territory_A_Formed_Condition.docx": "01.html",
    "02_Adaptive_Epistemologies.docx": "02.html",
    "03_Refractions.docx": "03.html",
    "04_Ecology_of_Practice.docx": "04.html",
    "05_Tools.docx": "05.html",
    "06_Models.docx": "06.html",
    "07_Technogeographies.docx": "07.html",
    "08_Landscape_as_Medium.docx": "08.html",
    "09_Interactions.docx": "09.html",
    "10_Generational_Robots.docx": "10.html",
    "11_CoCreation.docx": "11.html",
    "12_Synoptic_Views.docx": "12.html",
    "13_Vectors.docx": "13.html",
    "AA_Appendix.docx": "appendix-a.html",
    "BB_Appendix.docx": "appendix-b.html",
    "GG_Glossary.docx": "glossary.html",
}


def render_docx(docx_path: Path) -> str:
    result = subprocess.run(
        ["pandoc", str(docx_path), "-t", "html"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def split_sections(html: str) -> tuple[str, str, str]:
    refs_marker = '<h2 id="references">References</h2>'
    figs_marker = '<h2 id="figures">Figures</h2>'

    main = html
    refs = ""
    figs = ""

    if refs_marker in main:
        main, refs = main.split(refs_marker, 1)
    if figs_marker in refs:
        refs, figs = refs.split(figs_marker, 1)
    elif figs_marker in main:
        main, figs = main.split(figs_marker, 1)

    return main.strip(), refs.strip(), figs.strip()


def cleanup_html(html: str) -> str:
    html = re.sub(
        r"\A\s*<h1\b[^>]*>.*?</h1>\s*<h2\b[^>]*>.*?</h2>\s*",
        "",
        html,
        flags=re.S,
    )
    html = re.sub(r'<h2 id="section[^"]*"></h2>\s*', "", html)
    html = re.sub(
        r'<h3 id="[^"]*"><em>(Reference:.*?)</em></h3>',
        r"<p><em>\1</em></p>",
        html,
        flags=re.S,
    )
    return html.strip()


def build_articles(main_html: str, article_class: str = "ch-content") -> str:
    chunks = [chunk.strip() for chunk in re.split(r"(?=<h2\b)", main_html) if chunk.strip()]
    if not chunks and main_html.strip():
        chunks = [main_html.strip()]

    return "\n\n".join(
        f'    <article class="{article_class}">\n{chunk}\n</article>'
        for chunk in chunks
    )


def build_reference_block(title: str, html: str) -> str:
    if not html.strip():
        return ""
    return (
        '\n\n    <div style="max-width:var(--ch-content);margin:0 auto;padding:0 clamp(1.5rem,5vw,3rem);">\n'
        f'      <aside class="ch-references"><h2>{title}</h2>\n{html}\n</aside>\n'
        "    </div>"
    )


def build_inline_figure(
    img_src: str,
    number: str,
    caption: str,
    alt: str,
    desc: str,
    extra_class: str = "",
) -> str:
    class_name = "ch-inline-figure"
    if extra_class:
        class_name += f" {extra_class}"
    return f"""
<figure class="{class_name}">
  <img src="{img_src}" alt="{alt}" loading="lazy">
  <figcaption>
    <span class="ch-inline-figure__num">{number}</span>
    <span class="ch-inline-figure__caption">{caption}</span>
    <p class="ch-inline-figure__desc">{desc}</p>
  </figcaption>
</figure>
""".strip()


def build_backdrop(img_src: str, title: str, credit: str) -> str:
    return f"""
<div class="ch-backdrop">
  <div class="ch-backdrop__img" style="background-image: url('{img_src}')"></div>
  <div class="ch-backdrop__caption">
    <div class="ch-backdrop__caption-title">{title}</div>
    <div class="ch-backdrop__caption-credit">{credit}</div>
  </div>
</div>
""".strip()


def insert_after_marker(html: str, marker: str, block: str, count: int = 1) -> str:
    if marker not in html:
        raise RuntimeError(f"Could not find marker: {marker[:80]}")

    updated = html
    for _ in range(count):
        index = updated.find(marker)
        if index == -1:
            raise RuntimeError(f"Could not find marker occurrence: {marker[:80]}")
        insert_at = index + len(marker)
        updated = updated[:insert_at] + "\n\n" + block + updated[insert_at:]
    return updated


def enhance_ch09_main(main_html: str) -> str:
    wetware_figure = build_inline_figure(
        "img/09_interactions/09_WetwareKnowledgeLoop.png",
        "Figure 09_02",
        "Wetware diagram",
        "Wetware diagram",
        "Biology as a knowledge-producing medium, coupled to computational sensing.",
        extra_class="ch-inline-figure--simple",
    )
    forestation_backdrop = build_backdrop(
        "img/09_interactions/09_Forestation_Regions_Processes.png",
        "Figure 09_03  NEOM Forestation Study Aerial Diagram",
        "Bradley Cantrell, Adam Mekies, Sherwood Design Engineers",
    )
    studio_figure = build_inline_figure(
        "img/09_interactions/LAR7020_S25_Module_III_Team04_Final Board_reexport_Page_1.jpg",
        "Figure 09_04",
        "Almost an Island, Prototyping the Bay Studio",
        "Almost an Island studio board",
        "University of Virginia studio work referenced in the chapter source materials.",
    )
    map_figure = build_inline_figure(
        "img/09_interactions/SiteImage_01_SMALL_Map.jpg",
        "Figure 09_05",
        "Map of Pocomoke Sound, Chesapeake Bay",
        "Map of Pocomoke Sound, Chesapeake Bay",
        "Source figure adapted from the dissertation chapter materials.",
    )
    frameworks_figure = build_inline_figure(
        "img/09_interactions/09_SixFrameworks_Ch09_CoupledEcologies.png",
        "Figure 09_06",
        "Six Frameworks Diagram, Wetware + Technogeographies + Coupled Ecologies",
        "Six Frameworks Diagram",
        "Framework diagram locating Wetware within the dissertation's broader adaptive epistemology.",
        extra_class="ch-inline-figure--simple",
    )

    main_html = insert_after_marker(main_html, '<h3 id="wetware">Wetware</h3>', wetware_figure)
    main_html = insert_after_marker(
        main_html,
        '<h3 id="territorial-wetware">Territorial Wetware</h3>',
        forestation_backdrop,
    )
    main_html = insert_after_marker(
        main_html,
        """<p>The <em>Prototyping the Bay</em> studio (2019–present) translates
these protocols into a pedagogical framework. Students working on
Chesapeake Bay island sites are required to frame their designs as
structured experiments with explicit hypotheses, monitoring regimes, and
revision triggers. A student proposing a living shoreline on Tangier
Island does not deliver a fixed design. They deliver a conditional
protocol, if accretion rates measured by sediment pins exceed a
threshold within two years, extend the shoreline treatment to adjacent
reaches, if wave energy monitoring indicates overwash frequency above a
specified return interval, deploy temporary breakwater modules and if
the planted Spartina fails to establish in the northern quadrant, test
alternative species tolerant of the measured salinity range. The design
is a script, not a blueprint. The studio’s assessment criteria reward
the quality of the adaptive logic, the clarity of hypotheses, the
specificity of monitoring commitments, the intelligence of conditional
responses, over the visual resolution of the final form.</p>""",
        studio_figure,
    )
    main_html = insert_after_marker(
        main_html,
        """<h3 id="ethics-and-political-ecologies-of-wetware">Ethics and Political
Ecologies of Wetware</h3>""",
        map_figure,
    )
    main_html = insert_after_marker(
        main_html,
        """<h3 id="wetware-and-adaptive-epistemologies">Wetware and Adaptive
Epistemologies</h3>""",
        frameworks_figure,
    )

    return main_html


def replace_page_content(page_path: Path, body_html: str) -> None:
    page = page_path.read_text()

    start_markers = []
    article_match = re.search(r'^\s*<article class="ch-content[^"]*">', page, flags=re.M)
    if article_match:
        start_markers.append(article_match.start())
    in_dev_match = re.search(r'^\s*<div class="ch-in-development">', page, flags=re.M)
    if in_dev_match:
        start_markers.append(in_dev_match.start())
    if not start_markers:
        raise RuntimeError(f"Could not find dissertation content start in {page_path}")

    start = min(start_markers)
    end_markers = []
    nav_match = re.search(r'^\s*<nav class="ch-nav">', page[start:], flags=re.M)
    if nav_match:
        end_markers.append(start + nav_match.start())
    footer_match = re.search(r'^\s*<footer class="ch-footer">', page[start:], flags=re.M)
    if footer_match:
        end_markers.append(start + footer_match.start())
    if not end_markers:
        raise RuntimeError(f"Could not find dissertation content boundary in {page_path}")
    end = min(end_markers)

    updated = page[:start] + body_html + "\n\n" + page[end:]

    if page_path.name == "09.html":
        updated = updated.replace(
            '<div class="ch-hero__bg ch-hero__bg--generated"></div>',
            '<div class="ch-hero__bg" style="background-image: url(\'img/09_interactions/DJI_20231027111713_0047.JPG\')"></div>',
        )

    page_path.write_text(updated)


def main() -> None:
    for docx_name, html_name in PAGE_MAP.items():
        docx_path = DOCX_DIR / docx_name
        page_path = HTML_DIR / html_name

        rendered = render_docx(docx_path)
        main_html, refs_html, figs_html = split_sections(rendered)
        main_html = cleanup_html(main_html)
        refs_html = cleanup_html(refs_html)
        figs_html = cleanup_html(figs_html)

        if html_name == "09.html":
            main_html = enhance_ch09_main(main_html)

        article_class = "ch-content ch-content--glossary" if html_name == "glossary.html" else "ch-content"
        body = build_articles(main_html, article_class=article_class)

        body += build_reference_block("References", refs_html)
        body += build_reference_block("Figures", figs_html)

        replace_page_content(page_path, body)


if __name__ == "__main__":
    main()
