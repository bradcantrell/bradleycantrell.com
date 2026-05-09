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
    "07.html": "img/07_technogeographies/230718_SherwoodEngineering_Neom_View04.jpg",
    "08.html": "img/08_landscape_medium/230223-NEOM LotL_hires_spreads_Page_020.jpg",
    "09.html": "img/09_interactions/DJI_20231027111713_0047.JPG",
    "10.html": "img/10_generational_robots/10_WildernessCreator.jpg",
    "11.html": "img/11_cocreation/08_Figure01_AlgorithmicCultivation.jpg",
    "12.html": "img/12_synoptic/aerial-fog-point-living-shoreline-restoration-usfws.jpg",
    "13.html": "img/13_vectors/river-delta-satellite-PRINT.jpg",
}


CHAPTER_BLOCKS = {
    "01.html": [
        (
            "the-infrastructural-field",
            build_inline_figure(
                "img/01_territory/01_Mississippi_River_Watershed.png",
                "Figure 01_06",
                "Map of Mississippi River Watershed",
                "Map of Mississippi River Watershed",
                "The watershed-scale territorial field that underpins the chapter's argument.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "defining-the-formed-condition",
            build_inline_figure(
                "img/01_territory/01_OrphicPromethean.png",
                "Figure 01_03",
                "Orphic and Promethean Diagram",
                "Orphic and Promethean Diagram",
                "A diagrammatic pairing of extractive and attentive modes of environmental inquiry.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "the-failure-of-static-approaches",
            build_inline_figure(
                "img/01_territory/01_Figure_StaticVsAdaptive.png",
                "Figure 01_08",
                "Static vs Adaptive Diagram",
                "Static vs Adaptive Diagram",
                "A compact comparison between fixed infrastructure logics and adaptive territorial practice.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "synthetic-ground-and-coupled-ecologies",
            build_inline_figure(
                "img/01_territory/01_Pseudo_Ecologies.png",
                "Figure 01_10",
                "Pseudo Ecologies",
                "Pseudo Ecologies",
                "A study of constructed ecological fields and the territorial interfaces they produce.",
            ),
        ),
    ],
    "02.html": [
        (
            "the-selection-of-knowledge",
            build_inline_figure(
                "img/02_adaptive_epistemologies/02_AdaptiveEpistemologyCycle.png",
                "Figure 02_02",
                "The Adaptive Epistemology Cycle Diagram",
                "Adaptive Epistemology Cycle Diagram",
                "The dissertation's core learning loop, moving from proposition to sensing, revision, and renewed action.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "adaptive-management-and-its-limits",
            build_inline_figure(
                "img/02_adaptive_epistemologies/02_AMvsAE.png",
                "Figure 02_05",
                "Adaptive Management vs Adaptive Epistemology Diagram",
                "Adaptive Management vs Adaptive Epistemology Diagram",
                "A distinction between managerial feedback and the wider epistemological position developed in the dissertation.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "machine-intelligence-and-distributed-knowledge",
            build_inline_figure(
                "img/02_adaptive_epistemologies/230718_SherwoodEngineering_Neom_View01.jpg",
                "Figure 02_10",
                "Landscapes of the Line",
                "NEOM Landscapes of the Line concept study",
                "A project-scale test bed for distributed sensing, machine knowledge, and large territorial propositions.",
            ),
        ),
        (
            "adaptive-epistemology-in-practice",
            build_inline_figure(
                "img/02_adaptive_epistemologies/02_SixFrameworks.png",
                "Figure 02_07",
                "Six Frameworks Diagram",
                "Six Frameworks Diagram",
                "The six-part framework that organizes adaptive epistemology across the dissertation.",
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
                "Practice Refraction Framework Diagram",
                "Practice Refraction Framework Diagram",
                "A visual account of how projects, methods, and reflective loops refract through practice.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "case-study-and-comparative-project-analysis",
            build_inline_figure(
                "img/03_refractions/03_RefractionMethodology.png",
                "Figure 03_07",
                "Refraction as Method Diagram",
                "Refraction as Method Diagram",
                "The chapter's methodological argument translated into a compact diagrammatic sequence.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "communities-of-practice-and-collaborative-inquiry",
            build_inline_figure(
                "img/03_refractions/model_typologies.jpg",
                "Figure 03_10",
                "Model Typologies from Practice Research Symposium 5",
                "Model Typologies from Practice Research Symposium 5",
                "A comparative view of modeling approaches assembled through collaborative design research.",
            ),
        ),
        (
            "autoethnography-and-reflective-practice",
            build_inline_figure(
                "img/03_refractions/03_StructureOfRefraction.png",
                "Figure 03_11",
                "The Structure of Refraction Diagram",
                "The Structure of Refraction Diagram",
                "A framework for understanding how practice reflects, bends, and reconstitutes knowledge.",
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
                "Core Collateral Scaffolding Diagram",
                "Core Collateral Scaffolding Diagram",
                "A map of the supporting structures, institutions, and collaborations that hold practice together.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "process-driven-urban-and-territorial-design",
            build_inline_figure(
                "img/04_ecology_practice/04_EcologyOfPracticeDiagram.png",
                "Figure 04_06",
                "Ecology of Practice Diagram",
                "Ecology of Practice Diagram",
                "A diagrammatic summary of the practice ecology that this chapter names and traces.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "rivers-in-the-laboratory",
            build_inline_figure(
                "img/04_ecology_practice/beach-renourishment-dredge-virginia-beach-2013.jpg",
                "Figure 04_05",
                "USACE dredge pipe delivering sand for beach renourishment, Virginia Beach (2013)",
                "USACE beach renourishment infrastructure in Virginia Beach",
                "A field image that grounds the chapter's discussion of extraction, delivery, and sediment infrastructures.",
            ),
        ),
    ],
    "05.html": [
        (
            "the-practice-as-research-instrument-1",
            build_inline_figure(
                "img/05_tools/03_Figure07_Timeline-v3.png",
                "Figure 05_15",
                "Project Timeline Diagram",
                "Project Timeline Diagram",
                "A longitudinal view of the practice trajectory that structures the chapter's narrative.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "learning-to-see-20052012",
            build_inline_figure(
                "img/05_tools/thresholds_slides_Page_05.jpg",
                "Figure 05_07",
                "Thresholds Installation, Louisiana State University College of Art and Design",
                "Thresholds Installation at Louisiana State University",
                "An early responsive installation that established sensing, visualization, and feedback as design media.",
            ),
        ),
        (
            "learning-to-touch-20122016",
            build_inline_figure(
                "img/05_tools/DredgeFest40.jpg",
                "Figure 05_32",
                "Robotic Sediment Gates, Dredgefest 2014, Louisiana State University",
                "Robotic Sediment Gates at Dredgefest 2014",
                "A prototype from the chapter's middle period, where sediment choreography becomes an instrument of inquiry.",
            ),
        ),
        (
            "learning-to-code-20162020",
            build_inline_figure(
                "img/05_tools/device_layout_003.jpg",
                "Figure 05_20",
                "Algorithmic Cultivation Section Layout",
                "Algorithmic Cultivation section layout",
                "A design drawing that situates sensors, robotics, and wetware inside a coupled experimental apparatus.",
            ),
        ),
        (
            "learning-to-let-go-20172025",
            build_inline_figure(
                "img/05_tools/20210904_Eco_Management_View05-01.jpg",
                "Figure 05_51",
                "NEOM Eco-Management Concepts",
                "NEOM Eco-Management Concepts",
                "A later territorial study where adaptive management logics are scaled to large synthetic landscapes.",
            ),
        ),
    ],
    "06.html": [
        (
            "the-mississippi-river-basin-model-mrbm-field-to-the-lab",
            build_inline_figure(
                "img/06_models/250408_ArchD Landscape_Mississippi River Watershed.jpg",
                "Figure 06_02",
                "Map of Mississippi River Watershed",
                "Map of Mississippi River Watershed",
                "A watershed-scale view that frames the Mississippi River Basin Model in its territorial context.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "the-mississippi-river-basin-model-mrbm-field-to-the-lab",
            build_inline_figure(
                "img/06_models/miss-river-basin-model-vicksburg-tower-upstream.jpg",
                "Figure 06_06",
                "Mississippi River Basin Model, Tower View Downstream",
                "Mississippi River Basin Model tower view",
                "One of the chapter's key views into the Mississippi River Basin Model as an epistemic machine.",
            ),
        ),
        (
            "the-seine-long-anthropogenic-histories",
            build_inline_figure(
                "img/06_models/250408_ArchD Landscape_Seine River Watershed.jpg",
                "Figure 06_19",
                "Map of Seine River Watershed",
                "Map of Seine River Watershed",
                "The Seine basin as a long anthropogenic territory organized through hydraulic knowledge.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "the-rhine-hybrid-modeling-cultures",
            build_inline_figure(
                "img/06_models/250408_ArchD Potrait_Rhine River Watershed.jpg",
                "Figure 06_20",
                "Map of Rhine River Watershed",
                "Map of Rhine River Watershed",
                "A basin portrait for the hybrid modeling cultures discussed in the Rhine section.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "looking-forward-in-fluvial-modeling-and-for-design",
            build_inline_figure(
                "img/06_models/04_Figure_FluvialModelingParadigms.png",
                "Figure 06_26",
                "Fluvial Modeling Paradigms Diagram",
                "Fluvial Modeling Paradigms Diagram",
                "A summary diagram connecting the chapter's historical model traditions to contemporary design questions.",
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
                "The Datafied Territory Diagram",
                "The Datafied Territory Diagram",
                "A diagram showing how sensing infrastructures reorganize territory as a computational field.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "autonomy-through-infrastructure",
            build_inline_figure(
                "img/07_technogeographies/07_Figure04_AutonomyGradient.png",
                "Figure 07_03",
                "The Autonomy Gradient Diagram",
                "The Autonomy Gradient Diagram",
                "A spectrum of delegated agency that anchors the chapter's discussion of designed wildness.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "defining-neo-wilds",
            build_backdrop(
                "img/07_technogeographies/240772_SherwoodEngineering_NeomTestPlots_View03.jpg",
                "Figure 07_05  NEOM Technical Study, Test Plots",
                "Bradley Cantrell, Adam Mekies, Sherwood Design Engineers, Arqui 9",
            ),
        ),
        (
            "technogeographies-1",
            build_inline_figure(
                "img/07_technogeographies/07_SixFrameworks_Technogeographies.png",
                "Figure 07_08",
                "Six Frameworks Diagram, Technogeographies",
                "Six Frameworks Diagram, Technogeographies",
                "The technogeographic strand of the dissertation's larger adaptive epistemology framework.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "when-the-instruments-disagree",
            build_inline_figure(
                "img/07_technogeographies/07_Figure05_TemporalMismatch.png",
                "Figure 07_06",
                "Temporal Mismatch Diagram",
                "Temporal Mismatch Diagram",
                "A diagram of asynchronous environmental rhythms, sensing lags, and the politics of timing.",
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
                "Sediment choreography combs, Dredgefest 2014, Louisiana State University",
                "Sediment choreography combs at Dredgefest 2014",
                "A physical modeling setup that foregrounds sediment behavior as an active medium of design inquiry.",
            ),
        ),
        (
            "landscape-as-epistemic-thing",
            build_inline_figure(
                "img/08_landscape_medium/08_AssembledTerritory.png",
                "Figure 08_04",
                "Territory as Assemblage Diagram",
                "Territory as Assemblage Diagram",
                "A diagram of landscape as a composed but evolving assemblage rather than a fixed object.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "landscape-as-the-model",
            build_inline_figure(
                "img/08_landscape_medium/08_AbstractedEvolvedLandscapes.png",
                "Figure 08_09",
                "Abstracted and Evolved Landscapes Diagram",
                "Abstracted and Evolved Landscapes Diagram",
                "A comparison between abstracted models and landscapes that continue to evolve as experiments.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "toward-an-evaluative-framework",
            build_inline_figure(
                "img/08_landscape_medium/08_SixFrameworks_Wetware.png",
                "Figure 08_10",
                "Six Frameworks Diagram, Coupled Ecologies + Wetware",
                "Six Frameworks Diagram, Coupled Ecologies + Wetware",
                "A framework view tying landscape-as-medium to wetware and coupled ecologies.",
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
                "Wetware diagram",
                "Wetware diagram",
                "Biology as a knowledge-producing medium, coupled to computational sensing.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "territorial-wetware",
            build_backdrop(
                "img/09_interactions/09_Forestation_Regions_Processes.png",
                "Figure 09_03  NEOM Forestation Study Aerial Diagram",
                "Bradley Cantrell, Adam Mekies, Sherwood Design Engineers",
            ),
        ),
        (
            "ethics-and-political-ecologies-of-wetware",
            build_inline_figure(
                "img/09_interactions/SiteImage_01_SMALL_Map.jpg",
                "Figure 09_05",
                "Map of Pocomoke Sound, Chesapeake Bay",
                "Map of Pocomoke Sound, Chesapeake Bay",
                "Source figure adapted from the dissertation chapter materials.",
            ),
        ),
        (
            "wetware-and-adaptive-epistemologies",
            build_inline_figure(
                "img/09_interactions/09_SixFrameworks_Ch09_CoupledEcologies.png",
                "Figure 09_06",
                "Six Frameworks Diagram, Wetware + Technogeographies + Coupled Ecologies",
                "Six Frameworks Diagram",
                "Framework diagram locating Wetware within the dissertation's broader adaptive epistemology.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
    ],
    "10.html": [
        (
            "why-slowness-matters-now",
            build_inline_figure(
                "img/10_generational_robots/10_WildernessCreator.jpg",
                "Figure 10_01",
                "Wilderness Creator Diagram from Designing Autonomy",
                "Wilderness Creator Diagram from Designing Autonomy",
                "A speculative diagram for long-duration autonomy and robotic stewardship in changing landscapes.",
            ),
        ),
        (
            "active-sensing-and-robot-ecologies",
            build_inline_figure(
                "img/10_generational_robots/10_GenerationalKnowledge.png",
                "Figure 10_03",
                "Generational Knowledge Diagram",
                "Generational Knowledge Diagram",
                "A model for how robotic systems inherit, preserve, and extend environmental knowledge through time.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "multi-robot-ecologies",
            build_inline_figure(
                "img/10_generational_robots/10_SixFrameworks_GenerationalRobotics.png",
                "Figure 10_06",
                "Six Frameworks Diagram, Wetware + Technogeographies + Coupled Ecologies + Generational Robotics",
                "Six Frameworks Diagram, Generational Robotics",
                "The chapter's place inside the wider dissertation framework, with temporal continuity foregrounded.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "robotic-companions-for-reflexive-stewardship",
            build_inline_figure(
                "img/10_generational_robots/10_SimondonEvolution.png",
                "Figure 10_02",
                "Abstract to Applied Diagram",
                "Abstract to Applied Diagram",
                "A transition diagram linking theoretical autonomy to situated robotic companionship and care.",
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
                "Third Intelligence Diagram",
                "Third Intelligence Diagram",
                "A diagram positioning intelligence as distributed across organisms, machines, and design practices.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "multi-species-communication",
            build_inline_figure(
                "img/11_cocreation/atta-cephalotes-leafcutter-ant.jpg",
                "Biological Study",
                "Leafcutter ant collective behavior",
                "Leafcutter ant collective behavior",
                "A biological reference point for the chapter's discussion of intelligence emerging from distributed actors.",
            ),
        ),
        (
            "distributed-authorship",
            build_inline_figure(
                "img/11_cocreation/11_DistributedAuthorship.png",
                "Figure 11_04",
                "Distributed Authorship Diagram",
                "Distributed Authorship Diagram",
                "A framework for understanding how agency and authorship spread across human and non-human contributors.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "the-cultivant",
            build_inline_figure(
                "img/11_cocreation/11_Cultivant.png",
                "Figure 11_06",
                "The Cultivant Diagram",
                "The Cultivant Diagram",
                "A diagrammatic account of cultivation as a co-creative relation among systems, organisms, and designers.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "responsibility-in-distributed-systems",
            build_inline_figure(
                "img/11_cocreation/11_ThreeStancesTowardAI.png",
                "Figure 11_07",
                "Three Stances Toward AI in Design Practice",
                "Three Stances Toward AI in Design Practice",
                "A structured comparison of design positions toward AI, control, and shared responsibility.",
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
                "Adaptive Epistemology at the Territorial Scale Diagram",
                "Adaptive Epistemology at the Territorial Scale Diagram",
                "A synoptic diagram showing how the dissertation's frameworks circulate across territorial design practice.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "six-concepts-one-framework",
            build_inline_figure(
                "img/12_synoptic/12_UnevenTerrain.png",
                "Figure 12_03",
                "The Uneven Terrain Diagram",
                "The Uneven Terrain Diagram",
                "A diagram of asymmetry, partial knowledge, and the uneven ground on which adaptive design proceeds.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "for-ecology",
            build_inline_figure(
                "img/12_synoptic/temperate-forest-drone-PRINT.jpg",
                "Figure 12_04",
                "Pseudo-Ecologies, Forests Study",
                "Pseudo-Ecologies, Forests Study",
                "A forest-scale view that extends the dissertation's synthetic ecologies beyond deltaic terrain.",
            ),
        ),
        (
            "coda-landscapes-of-becoming",
            build_inline_figure(
                "img/12_synoptic/12_PluralityAsStructuralCommitment.png",
                "Figure 12_05",
                "Plurality as Structural Commitment",
                "Plurality as Structural Commitment",
                "A concluding diagram arguing for plurality as a built-in condition of environmental design practice.",
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
                "Pseudo-Regions, Frozen Islands",
                "Pseudo-Regions, Frozen Islands",
                "A pseudo-regional study used to open the chapter's concluding set of territorial vectors.",
            ),
        ),
        (
            "six-vectors-directions-not-conclusions",
            build_inline_figure(
                "img/13_vectors/13_SixVectors.png",
                "Figure 13_03",
                "Six Vectors Diagram",
                "Six Vectors Diagram",
                "A concluding diagram that gathers the dissertation into six directional commitments rather than a closed ending.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "the-neo-wild",
            build_inline_figure(
                "img/13_vectors/13_SensingPolitics.png",
                "Figure 13_05",
                "Politics of Sensing Diagram",
                "Politics of Sensing Diagram",
                "A final argument that sensing is never neutral and always participates in territorial politics.",
                extra_class="ch-inline-figure--simple",
            ),
        ),
        (
            "what-the-place-knows",
            build_inline_figure(
                "img/13_vectors/desert-satellite-PRINT.jpg",
                "Figure 13_04",
                "Pseudo-Regions, Arid",
                "Pseudo-Regions, Arid",
                "A closing territorial study that reinforces place-based knowledge as a situated and plural condition.",
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
