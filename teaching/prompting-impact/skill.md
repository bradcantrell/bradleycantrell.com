# Ecological Assessment — Tennessee River Corridor

**Model skill.** To use, paste the body of this file into your model's chat window and tell it you are working from this skill. If your tool reads skill files, save this as `SKILL.md` and prepend the frontmatter below:

```
---
name: ecological-assessment
description: Produce a live environmental web map + a defensible ecological assessment of your reach of the Tennessee River corridor using real-time data.
---
```

---

Use this skill to conduct an **ecological assessment** of your quad on the Tennessee River corridor. The deliverable is two things: (1) a **live web map** and (2) a **written assessment** that is honest about what is verified versus what is merely asserted.

The governing rule: **you are an instrument the student directs, not an oracle.** You help assemble, structure, and reason — but every claim about the real world must be traceable to a real source, and anything that is not must be labeled as machine-asserted.

## Your reach

Your quad is in `site-NN-your-name.kml`, in your Session 2 folder. Paste or attach that KML. The KMZ in Session 1 is a zipped copy of the same file and cannot be pasted. Each quad is **2 km along the river × 4 km into the land**, and it is **rotated to follow the river**, so its bounding box is about twice its area. Take the four corners and the center point from the KML, never from memory. You can see every quad on the corridor map at **prompting-impact.pages.dev**.

## Workflow

1. **Reach + question** — locate your quad and state the ecological question you are asking about it.
2. **Live data** — fetch every source on the data sources page into `data/`. Anything you did not just fetch is machine-asserted.
3. **Map** — build a single-file Leaflet web map that plots the data.
4. **Assessment** — for Assignment 2 this is the source assessment in `source-assessment.md`: one table and five short sections.
5. **Verification ledger** — separate every claim into *live-verified* vs *machine-asserted*.

## Data sources

Every endpoint, with a working query and the trap in each one, is on the data sources page:
**https://bradleycantrell.com/teaching/prompting-impact/data-sources.html**

Fetch from that page, not from memory. All of the sources are keyless. Five rules catch most of the mistakes.

- **The river gauge is NWPS `knot1`, not USGS.** The USGS Tennessee River sites in Knox County serve no live data. Flood stages are action 817, minor 820, moderate 825, major 830 ft. It is one point in the water, so say how far it is from the quad.
- **Ask the flood model at the channel point, the center and the four corners, and keep the cell with the most water.** It works on cells about 5 km across, its river can sit a whole cell away from the real channel, and a cell off its river returns almost nothing. Record the cell the response names, and never label that cell as the quad.
- **Query species by the quad's bounding box, then keep only points inside the four corners.** A radius search reaches far past the quad.
- **Mind units and sentinels.** The gauge reports feet. 3DEP reports meters unless you ask for feet, so ask. A FEMA value of −9999 means no value, not an elevation.
- **Show FEMA flood zones with the image export.** Feature queries over a whole quad often time out.

## Map template

For Assignment 2, start from `dashboard-starter.html`. It already reads the gauge, the weather, air quality, the flood model at the cell that carries the river and species clipped to the quad, and it shows the measured against modeled gap without picking a winner. Fill its config block from the KML, then add one layer at a time and say which lines changed. `map-template.html` is the simpler map from the first week. Keep everything `https` and keyless so it works from a plain browser.

## Assessment structure

Assignment 2 hands in the source assessment, built with the table and the five short sections in `source-assessment.md`. It covers the tiers of authority, the six dimensions, the weakest link rule, and the three forms of divergence.

The module assessment in `assessment.md` is the larger document assembled across all three assignments, and you return to it at the end of the third.

Every factual sentence must point to either a live source or be marked machine-asserted.

## Verification ledger (required)

Two columns:

| live-verified | machine-asserted |
|---|---|
| pulled from a real API/record, with source + timestamp | stated without a source — suspect until checked |

Before submitting, classify every claim in the assessment into one column. If a claim cannot be verified, it goes in the machine-asserted column and is treated as suspect, not fact.

## Disclosure (course policy)

State which tools were used, which data sources fed the work, and how outputs were produced, modified, or rejected. Transparency is the design ethic — invisible AI use is not permitted.
