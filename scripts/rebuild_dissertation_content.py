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
    desc: str = "",
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
  </figcaption>
</figure>
""".strip()


def build_backdrop(img_src: str, number: str, caption: str) -> str:
    return f"""
<div class="ch-backdrop">
  <div class="ch-backdrop__img" style="background-image: url('{img_src}')"></div>
  <div class="ch-backdrop__caption">
    <div class="ch-backdrop__caption-title"><span class="ch-inline-figure__num">{number}</span> <span class="ch-inline-figure__caption">{caption}</span></div>
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


def insert_after_heading_id(html: str, heading_id: str, block: str) -> str:
    pattern = re.compile(rf'(<h[23] id="{re.escape(heading_id)}">.*?</h[23]>)', re.S)
    match = pattern.search(html)
    if not match:
        raise RuntimeError(f"Could not find heading id: {heading_id}")
    insert_at = match.end()
    return html[:insert_at] + "\n\n" + block + html[insert_at:]


def apply_blocks(main_html: str, blocks: list[tuple[str, str]]) -> str:
    for heading_id, block in blocks:
        main_html = insert_after_heading_id(main_html, heading_id, block)
    return main_html


CHAPTER_HEROES = {
    "01.html": "img/hero_quotes/01.jpg",
    "02.html": "img/hero_quotes/02.jpg",
    "03.html": "img/hero_quotes/03.jpg",
    "04.html": "img/hero_quotes/04.jpg",
    "05.html": "img/hero_quotes/05.jpg",
    "06.html": "img/hero_quotes/06.jpg",
    "07.html": "img/hero_quotes/07.jpg",
    "08.html": "img/hero_quotes/08.jpg",
    "09.html": "img/hero_quotes/09.jpg",
    "10.html": "img/hero_quotes/10.jpg",
    "11.html": "img/hero_quotes/11.jpg",
    "12.html": "img/hero_quotes/12.jpg",
    "13.html": "img/hero_quotes/13.jpg",
}


CHAPTER_BLOCKS = {
    "01.html": [
        (
            "the-infrastructural-field",
            build_inline_figure(
                "img/01_territory/01_Mississippi_River_Watershed.png",
                "Figure 01_06",
                "Map of Mississippi River Watershed | Bradley Cantrell",
                "Map of Mississippi River Watershed",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "defining-the-formed-condition",
            build_inline_figure(
                "img/01_territory/01_OrphicPromethean.png",
                "Figure 01_03",
                "Orphic and Promethean Diagram | Bradley Cantrell",
                "Orphic and Promethean Diagram",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "the-failure-of-static-approaches",
            build_inline_figure(
                "img/01_territory/01_Figure_StaticVsAdaptive.png",
                "Figure 01_08",
                "Static vs Adaptive Diagram | Bradley Cantrell",
                "Static vs Adaptive Diagram",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "synthetic-ground-and-coupled-ecologies",
            build_inline_figure(
                "img/01_territory/01_Pseudo_Ecologies.png",
                "Figure 01_10",
                "Pseudo Ecologies | Bradley Cantrell",
                "Pseudo Ecologies",
            ),
        ),
    ],
    "02.html": [
        (
            "the-selection-of-knowledge",
            build_inline_figure(
                "img/02_adaptive_epistemologies/02_AdaptiveEpistemologyCycle.png",
                "Figure 02_02",
                "The Adaptive Epistemology Cycle Diagram | Bradley Cantrell",
                "Adaptive Epistemology Cycle Diagram",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "adaptive-management-and-its-limits",
            build_inline_figure(
                "img/02_adaptive_epistemologies/02_AMvsAE.png",
                "Figure 02_05",
                "Adaptive Management vs Adaptive Epistemology Diagram | Bradley Cantrell",
                "Adaptive Management vs Adaptive Epistemology Diagram",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "machine-intelligence-and-distributed-knowledge",
            build_inline_figure(
                "img/02_adaptive_epistemologies/230718_SherwoodEngineering_Neom_View01.jpg",
                "Figure 02_10",
                "Landscapes of the Line | Adam Mekies and Bradley Cantrell + Sherwood Design Engineers + Arqui 9",
                "NEOM Landscapes of the Line concept study",
            ),
        ),
        (
            "adaptive-epistemology-in-practice",
            build_inline_figure(
                "img/02_adaptive_epistemologies/02_SixFrameworks.png",
                "Figure 02_07",
                "Six Frameworks Diagram | Bradley Cantrell",
                "Six Frameworks Diagram",
                extra_class="ch-inline-figure--simple",
            ),
        ),
    ],
    "03.html": [
        (
            "practice-based-research",
            build_inline_figure(
                "img/03_refractions/03_PracticeRefractionFramework.png",
                "Figure 03_04",
                "Practice Refraction Framework Diagram | Bradley Cantrell",
                "Practice Refraction Framework Diagram",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "case-study-and-comparative-project-analysis",
            build_inline_figure(
                "img/03_refractions/03_RefractionMethodology.png",
                "Figure 03_07",
                "Refraction as Method Diagram | Bradley Cantrell",
                "Refraction as Method Diagram",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "communities-of-practice-and-collaborative-inquiry",
            build_inline_figure(
                "img/03_refractions/model_typologies.jpg",
                "Figure 03_10",
                "Model Typologies from Practice Research Symposium 5 | Bradley Cantrell",
                "Model Typologies from Practice Research Symposium 5",
            ),
        ),
        (
            "autoethnography-and-reflective-practice",
            build_inline_figure(
                "img/03_refractions/03_StructureOfRefraction.png",
                "Figure 03_11",
                "The Structure of Refraction Diagram | Bradley Cantrell",
                "The Structure of Refraction Diagram",
                extra_class="ch-inline-figure--simple",
            ),
        ),
    ],
    "04.html": [
        (
            "tracings",
            build_inline_figure(
                "img/04_ecology_practice/04_CoreCollateralScaffolding.png",
                "Figure 04_04",
                "Core Collateral Scaffolding Diagram | Bradley Cantrell",
                "Core Collateral Scaffolding Diagram",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "process-driven-urban-and-territorial-design",
            build_inline_figure(
                "img/04_ecology_practice/04_EcologyOfPracticeDiagram.png",
                "Figure 04_06",
                "Ecology of Practice Diagram | Bradley Cantrell",
                "Ecology of Practice Diagram",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "rivers-in-the-laboratory",
            build_inline_figure(
                "img/04_ecology_practice/beach-renourishment-dredge-virginia-beach-2013.jpg",
                "Figure 04_05",
                "USACE dredge pipe delivering sand for beach renourishment, Virginia Beach (2013) | U.S. Army Corps of Engineers",
                "USACE beach renourishment infrastructure in Virginia Beach",
            ),
        ),
    ],
    "05.html": [
        (
            "the-practice-as-research-instrument-1",
            build_inline_figure(
                "img/05_tools/03_Figure07_Timeline-v3.png",
                "Figure 05_15",
                "Project Timeline Diagram | Bradley Cantrell",
                "Project Timeline Diagram",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "learning-to-see-20052012",
            build_inline_figure(
                "img/05_tools/thresholds_slides_Page_05.jpg",
                "Figure 05_07",
                "Thresholds Installation, Louisiana State University College of Art and Design | Bradley Cantrell",
                "Thresholds Installation at Louisiana State University",
            ),
        ),
        (
            "learning-to-touch-20122016",
            build_inline_figure(
                "img/05_tools/DredgeFest40.jpg",
                "Figure 05_32",
                "Robotic Sediment Gates, Dredgefest 2014, Louisiana State University | Bradley Cantrell, Justine Holzman, Prentiss Darden, David Merlin",
                "Robotic Sediment Gates at Dredgefest 2014",
            ),
        ),
        (
            "learning-to-code-20162020",
            build_inline_figure(
                "img/05_tools/device_layout_003.jpg",
                "Figure 05_20",
                "Algorithmic Cultivation Section Layout | Bradley Cantrell, Robin Dripps, Lucia Phinney, Emma Mendel",
                "Algorithmic Cultivation section layout",
            ),
        ),
        (
            "learning-to-let-go-20172025",
            build_inline_figure(
                "img/05_tools/20210904_Eco_Management_View05-01.jpg",
                "Figure 05_51",
                "NEOM Eco-Management Concepts | Bradley Cantrell, Adam Mekies + Sherwood Design Engineers",
                "NEOM Eco-Management Concepts",
            ),
        ),
    ],
    "06.html": [
        (
            "the-mississippi-river-basin-model-mrbm-field-to-the-lab",
            build_inline_figure(
                "img/06_models/250408_ArchD Landscape_Mississippi River Watershed.jpg",
                "Figure 06_02",
                "Map of Mississippi River Watershed | Bradley Cantrell, Madhura Vaze",
                "Map of Mississippi River Watershed",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "the-mississippi-river-basin-model-mrbm-field-to-the-lab",
            build_inline_figure(
                "img/06_models/miss-river-basin-model-vicksburg-tower-upstream.jpg",
                "Figure 06_06",
                "Mississippi River Basin Model, Tower View Downstream | United States Army Corps of Engineers, Library of Congress",
                "Mississippi River Basin Model tower view",
            ),
        ),
        (
            "the-seine-long-anthropogenic-histories",
            build_inline_figure(
                "img/06_models/250408_ArchD Landscape_Seine River Watershed.jpg",
                "Figure 06_19",
                "Map of Seine River Watershed | Bradley Cantrell, Madhura Vaze",
                "Map of Seine River Watershed",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "the-rhine-hybrid-modeling-cultures",
            build_inline_figure(
                "img/06_models/250408_ArchD Potrait_Rhine River Watershed.jpg",
                "Figure 06_20",
                "Map of Rhine River Watershed | Bradley Cantrell, Madhura Vaze",
                "Map of Rhine River Watershed",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "looking-forward-in-fluvial-modeling-and-for-design",
            build_inline_figure(
                "img/06_models/04_Figure_FluvialModelingParadigms.png",
                "Figure 06_26",
                "Fluvial Modeling Paradigms Diagram | Bradley Cantrell",
                "Fluvial Modeling Paradigms Diagram",
                extra_class="ch-inline-figure--simple",
            ),
        ),
    ],
    "07.html": [
        (
            "from-situated-landscapes-to-datafied-territories",
            build_inline_figure(
                "img/07_technogeographies/07_DatafiedTerritory.png",
                "Figure 07_04",
                "The Datafied Territory Diagram | Bradley Cantrell",
                "The Datafied Territory Diagram",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "autonomy-through-infrastructure",
            build_inline_figure(
                "img/07_technogeographies/07_Figure04_AutonomyGradient.png",
                "Figure 07_03",
                "The Autonomy Gradient Diagram | Bradley Cantrell",
                "The Autonomy Gradient Diagram",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "defining-neo-wilds",
            build_backdrop(
                "img/07_technogeographies/240772_SherwoodEngineering_NeomTestPlots_View03.jpg",
                "Figure 07_05",
                "NEOM Technical Study, Test Plots | Bradley Cantrell, Adam Mekies, Sherwood Design Engineers, Arqui 9",
            ),
        ),
        (
            "technogeographies-1",
            build_inline_figure(
                "img/07_technogeographies/07_SixFrameworks_Technogeographies.png",
                "Figure 07_08",
                "Six Frameworks Diagram, Technogeographies | Bradley Cantrell",
                "Six Frameworks Diagram, Technogeographies",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "when-the-instruments-disagree",
            build_inline_figure(
                "img/07_technogeographies/07_Figure05_TemporalMismatch.png",
                "Figure 07_06",
                "Temporal Mismatch Diagram | Bradley Cantrell",
                "Temporal Mismatch Diagram",
                extra_class="ch-inline-figure--simple",
            ),
        ),
    ],
    "08.html": [
        (
            "physical-models-as-bounded-experiments",
            build_inline_figure(
                "img/08_landscape_medium/04_sediment_model.jpg",
                "Figure 08_03",
                "Sediment choreography combs, Dredgefest 2014, Louisiana State University | Bradley Cantrell, Justine Holzman",
                "Sediment choreography combs at Dredgefest 2014",
            ),
        ),
        (
            "landscape-as-epistemic-thing",
            build_inline_figure(
                "img/08_landscape_medium/08_AssembledTerritory.png",
                "Figure 08_04",
                "Territory as Assemblage Diagram | Bradley Cantrell",
                "Territory as Assemblage Diagram",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "landscape-as-the-model",
            build_inline_figure(
                "img/08_landscape_medium/08_AbstractedEvolvedLandscapes.png",
                "Figure 08_09",
                "Abstracted and Evolved Landscapes Diagram | Bradley Cantrell",
                "Abstracted and Evolved Landscapes Diagram",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "toward-an-evaluative-framework",
            build_inline_figure(
                "img/08_landscape_medium/08_SixFrameworks_Wetware.png",
                "Figure 08_10",
                "Six Frameworks Diagram, Coupled Ecologies + Wetware | Bradley Cantrell",
                "Six Frameworks Diagram, Coupled Ecologies + Wetware",
                extra_class="ch-inline-figure--simple",
            ),
        ),
    ],
    "09.html": [
        (
            "wetware",
            build_inline_figure(
                "img/09_interactions/09_WetwareKnowledgeLoop.png",
                "Figure 09_02",
                "Wetware diagram | Bradley Cantrell",
                "Wetware diagram",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "territorial-wetware",
            build_backdrop(
                "img/09_interactions/09_Forestation_Regions_Processes.png",
                "Figure 09_03",
                "NEOM Forestation Study Aerial Diagram | Bradley Cantrell, Adam Mekies, Sherwood Design Engineers",
            ),
        ),
        (
            "ethics-and-political-ecologies-of-wetware",
            build_inline_figure(
                "img/09_interactions/SiteImage_01_SMALL_Map.jpg",
                "Figure 09_05",
                "Map of Pocomoke Sound, Chesapeake Bay | Bradley Cantrell, Sean Kois",
                "Map of Pocomoke Sound, Chesapeake Bay",
            ),
        ),
        (
            "wetware-and-adaptive-epistemologies",
            build_inline_figure(
                "img/09_interactions/09_SixFrameworks_Ch09_CoupledEcologies.png",
                "Figure 09_06",
                "Six Frameworks Diagram, Wetware + Technogeographies + Coupled Ecologies | Bradley Cantrell",
                "Six Frameworks Diagram",
                extra_class="ch-inline-figure--simple",
            ),
        ),
    ],
    "10.html": [
        (
            "why-slowness-matters-now",
            build_inline_figure(
                "img/10_generational_robots/10_WildernessCreator.jpg",
                "Figure 10_1",
                "Wilderness Creator Diagram from Designing Autonomy | Bradley Cantrell, Erle Ellis, Laura Jane Martin",
                "Wilderness Creator Diagram from Designing Autonomy",
            ),
        ),
        (
            "active-sensing-and-robot-ecologies",
            build_inline_figure(
                "img/10_generational_robots/10_GenerationalKnowledge.png",
                "Figure 10_3",
                "Generational Knowledge Diagram | Bradley Cantrell",
                "Generational Knowledge Diagram",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "multi-robot-ecologies",
            build_inline_figure(
                "img/10_generational_robots/10_SixFrameworks_GenerationalRobotics.png",
                "Figure 10_6",
                "Six Frameworks Diagram, Wetware + Technogeographies + Coupled Ecologies + Generational Robotics | Bradley Cantrell",
                "Six Frameworks Diagram, Generational Robotics",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "robotic-companions-for-reflexive-stewardship",
            build_inline_figure(
                "img/10_generational_robots/10_SimondonEvolution.png",
                "Figure 10_2",
                "Abstract to Applied Diagram | Bradley Cantrell",
                "Abstract to Applied Diagram",
                extra_class="ch-inline-figure--simple",
            ),
        ),
    ],
    "11.html": [
        (
            "forms-of-intelligence-in-landscape-systems",
            build_inline_figure(
                "img/11_cocreation/08_Figure03_ThirdIntelligence.png",
                "Figure 11_02",
                "Multiple Intelligences Diagram | Bradley Cantrell",
                "Third Intelligence Diagram",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "distributed-authorship",
            build_inline_figure(
                "img/11_cocreation/11_DistributedAuthorship.png",
                "Figure 11_04",
                "Distributed Authorship Diagram | Bradley Cantrell",
                "Distributed Authorship Diagram",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "the-cultivant",
            build_inline_figure(
                "img/11_cocreation/11_Cultivant.png",
                "Figure 11_06",
                "The Cultivant Diagram | Bradley Cantrell",
                "The Cultivant Diagram",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "responsibility-in-distributed-systems",
            build_inline_figure(
                "img/11_cocreation/11_ThreeStancesTowardAI.png",
                "Figure 11_07",
                "Three Stances Toward AI in Design Practice | Bradley Cantrell",
                "Three Stances Toward AI in Design Practice",
                extra_class="ch-inline-figure--simple",
            ),
        ),
    ],
    "12.html": [
        (
            "the-shape-of-the-argument",
            build_inline_figure(
                "img/12_synoptic/12_FrameworkCircuit.png",
                "Figure 12_02",
                "Adaptive Epistemology at the Territorial Scale Diagram | Bradley Cantrell",
                "Adaptive Epistemology at the Territorial Scale Diagram",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "six-concepts-one-framework",
            build_inline_figure(
                "img/12_synoptic/12_UnevenTerrain.png",
                "Figure 12_03",
                "The Uneven Terrain Diagram | Bradley Cantrell",
                "The Uneven Terrain Diagram",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "for-ecology",
            build_inline_figure(
                "img/12_synoptic/temperate-forest-drone-PRINT.jpg",
                "Figure 12_04",
                "Pseudo-Ecologies _ Forests | Bradley Cantrell",
                "Pseudo-Ecologies, Forests Study",
            ),
        ),
        (
            "coda-landscapes-of-becoming",
            build_inline_figure(
                "img/12_synoptic/12_PluralityAsStructuralCommitment.png",
                "Figure 12_05",
                "Plurality as Structural Commitment | Bradley Cantrell",
                "Plurality as Structural Commitment",
                extra_class="ch-inline-figure--simple",
            ),
        ),
    ],
    "13.html": [
        (
            "what-the-frameworks-give-us",
            build_inline_figure(
                "img/13_vectors/TECHGEO-01-4x.png",
                "Figure 13_01",
                "Pseudo-Regions _ frozen islands | Bradley Cantrell",
                "Pseudo-Regions, Frozen Islands",
            ),
        ),
        (
            "six-vectors-directions-not-conclusions",
            build_inline_figure(
                "img/13_vectors/13_SixVectors.png",
                "Figure 13_03",
                "Six Vectors Diaram | Bradley Cantrell",
                "Six Vectors Diagram",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "the-neo-wild",
            build_inline_figure(
                "img/13_vectors/13_SensingPolitics.png",
                "Figure 13_05",
                "Politics of Sensing Diagram | Bradley Cantrell",
                "Politics of Sensing Diagram",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "what-the-place-knows",
            build_inline_figure(
                "img/13_vectors/desert-satellite-PRINT.jpg",
                "Figure 13_04",
                "Pseudo-Regions _arid | Bradley Cantrell",
                "Pseudo-Regions, Arid",
            ),
        ),
    ],
}


def apply_chapter_enhancements(html_name: str, main_html: str) -> str:
    blocks = CHAPTER_BLOCKS.get(html_name)
    if not blocks:
        return main_html
    return apply_blocks(main_html, blocks)


def set_hero_image(page: str, img_src: str) -> str:
    hero_pattern = re.compile(
        r'<div class="ch-hero__bg(?: ch-hero__bg--generated)?"(?: style="background-image: url\(\'[^\']+\'\)")?></div>'
    )
    replacement = f'<div class="ch-hero__bg" style="background-image: url(\'{img_src}\')"></div>'
    updated, count = hero_pattern.subn(replacement, page, count=1)
    if count == 0:
        raise RuntimeError("Could not find hero background to replace")
    return updated


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

    hero_img = CHAPTER_HEROES.get(page_path.name)
    if hero_img:
        updated = set_hero_image(updated, hero_img)

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

        main_html = apply_chapter_enhancements(html_name, main_html)

        article_class = "ch-content ch-content--glossary" if html_name == "glossary.html" else "ch-content"
        body = build_articles(main_html, article_class=article_class)

        body += build_reference_block("References", refs_html)
        body += build_reference_block("Figures", figs_html)

        replace_page_content(page_path, body)


if __name__ == "__main__":
    main()
