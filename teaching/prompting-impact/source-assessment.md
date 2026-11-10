# Assessing the Quality of Sources
### Assignment 2 · the assessment template

**Due Thursday, November 12, 2026 · 1200 EST.** Hand this in as `source-assessment.md`.

A source is not good or bad in the abstract. It is good or bad for a claim you are making about your quad, the 2 km by 4 km rectangle assigned to you on the Tennessee River corridor. A global flood model is excellent for screening a continent and useless for telling you what the water is doing at your quad. The judgment is always relative to the question.

So this assessment does not ask whether your data is verified. It asks you to characterize the quality of every source you used, and then to say which of your claims that quality can actually support.

---

## 1. Tiers of authority

Rank each source by who operates it and what they answer for. This corridor has five tiers. The last one is where any claim you could not trace belongs.

**Tier 1 · Instrumented by an agency that answers for it.**
The stage and flow gauge at Knoxville, reported through the National Water Prediction Service and forecast by the Lower Mississippi River Forecast Center. NWS warnings. A physical instrument, in the water, whose readings a forecast center is accountable for.

**Tier 2 · Modeled or derived, with stated method.**
Open-Meteo weather and air quality. The Open-Meteo flood model, which is GloFAS at a 5 km cell. NLCD land cover. FEMA flood zones. These are products of a documented method applied to data. They carry the assumptions of that method, and the assumptions are usually the thing that matters.

**Tier 3 · Volunteer and crowdsourced.**
iNaturalist. eBird. Community air sensors. Enormously valuable and unevenly distributed. A record is where someone with a phone happened to walk.

**Tier 4 · Archival and historical.**
McClung photographs. Old maps. Engineering records. Not measurements, but evidence. A 1920 photograph of a riverbank is a real observation by a real observer, and it is also one frame, chosen by someone, at one moment.

**Tier 5 · Machine assertion with no source.**
Anything an AI model told you that you could not trace. It can be useful as a hypothesis. It cannot support a claim about the world.

---

## 2. Six dimensions

For every source, characterize it on these. Two sentences each is enough.

**Authority.** Who produced it, under what mandate, and do they answer for errors. A dam operator reporting its own gate setting is not the same as a global model inferring discharge from terrain and rainfall.

**Method.** Measured, modeled, derived, observed, or recalled. Write which one. Most disagreements between sources are method disagreements wearing a numbers costume.

**Resolution.** Spatial and temporal grain against your quad. A point gauge is exact at one place. The flood model is a 5 km cell updated daily. A 25 km species radius is coarser than your quad spatially. Say which axis fails.

**Latency and currency.** Realtime, hourly, daily, annual, or frozen at a single vintage, which for the land cover layer means one date rather than a trend. This determines what question the source can answer now.

**Fitness for your question.** The only dimension that is about you. Can this source answer what you asked of your quad, or does it answer a neighboring question at a different scale.

**Stated error.** Is an uncertainty given, or is the number presented bare. A source that publishes its error bars is easier to trust than one that does not, even when the error is large.

---

## 3. The weakest link

A claim inherits the quality of the weakest source in the chain that produced it.

If you write that the river at your quad sits at 811.6 ft, and that number came from a gauge four kilometers upstream in a different hydraulic reach, your claim is only as strong as that spatial transfer, not as strong as the gauge. The instrument is excellent. The transfer is not.

Do this to your own sentences. For each claim, name every source it passed through, then find the weakest one. That is the quality of the claim, and it is usually lower than the student expects.

---

## 4. A worked example, already in your data

Two numbers for the flow of the same river exist in the set you were given.

The NWPS gauge at Knoxville reports **55.3 kcfs**, which is about 1,566 cubic meters per second. It is an instrumented observation in the water, the reading when this was written on November 10, 2026, at a reach whose flow is set by dams.

The Open-Meteo flood model, queried at the same coordinates, reports **266 cubic meters per second**.

A factor of 5.9.

Neither number is a lie. GloFAS runs one value per 5 km cell per day from a global hydrological model driven by weather reanalysis, and it has no way of knowing what the Tennessee Valley Authority released through the dams upstream this morning. At this reach, the release schedule is most of the flow. The gauge measures one point, continuously, in the channel. Both are correct about the thing each one measures, and they disagree about the river.

At least three explanations fit. The release schedule upstream. The 5 km cell, which cannot resolve a channel. The weather forcing behind the model, which is a reanalysis of a grid rather than this valley's rain gauges. Which one is right is a question you can test, and that is the work.

Write the paragraph explaining that gap. It is the clearest exercise in source quality in this corridor, and you have both endpoints.

---

## 5. Three forms of divergence

When two sources give incompatible accounts of the same thing, the gap between them is information, about the sources, about the reach, or about both. Naming the form is most of the work, and there are three.

**Calibration divergence.** The same variable read at different resolutions. A point gauge against a gridded flood model. A reanalysis cell against your own coordinates. The mismatch tells you the scale at which the process is actually working.

**Modality divergence.** Your own reading and a technical source register different dimensions of one thing. The bank you traced against a land cover class. A photograph against a species list. The gap between them is the thing's full complexity.

**Intentional divergence.** Sources built by institutions with different mandates answer different questions. A FEMA flood zone is drawn for insurance. An NWS flood category is drawn for warning. Put them side by side and you see what each was built to see.

Do not choose, and do not average. A disagreement is not an error to settle by picking a preferred source. It is evidence about the river or about the instruments, and usually both. Ask what each source could be seeing that the other cannot, and what you would go measure to tell the explanations apart.

---

## 6. What you hand in

One table and one page of prose. The table comes first, above the prose.

The table, one row per source you actually used. Do not list sources you looked at and discarded.

| source | tier | method | resolution | latency | what it can answer | what it cannot |
|---|---|---|---|---|---|---|
| | | | | | | |

The table carries method, resolution, latency and fitness. Authority is the tier column. Stated error belongs in the prose, where it needs a sentence rather than a cell.

Then five short sections.

**What I built and why.** The question, the layers, and the dashboard. One paragraph.

**Source assessment.** Two or three sources that changed how you read your quad. Name the dimension that made the difference, resolution or method or latency, not just a general impression.

**Where the claim weakens.** Apply the weakest link rule to three of your own claims. Name the chain, name the weak source, and state what the claim is actually worth.

**Where the sources disagree.** Two disagreements, each with both readings, its form, what it suggests, and what would test it. First the required gap, the NWPS gauge against the Open-Meteo flood model, including the ratio between them. Then one disagreement of your own that involves the layer you made.

**What I would trust less next time.** One honest paragraph. A source you used confidently and now would not.

---

## 7. What makes this hard

The temptation is to rank sources once and reuse the ranking. The gauge is the best source in your set and it cannot by itself tell you what is happening at your quad. iNaturalist is the weakest in method and it is the only source that knows a species is present.

Quality is not a ranking. It is a fit between a source and a question, and the whole skill is being honest about which fit you have.
