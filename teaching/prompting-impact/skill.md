# Ecological Assessment — Knoxville Living Systems

**Claude skill.** To use, paste the body of this file into Claude (chat) and tell it you are working from this skill. If you use Claude Code instead, save this as `SKILL.md` and prepend the frontmatter below:

```
---
name: ecological-assessment
description: Produce a live environmental web map + a defensible ecological assessment of a Knoxville living system using real-time data.
---
```

---

Use this skill to conduct an **ecological assessment** of a Knoxville site. The deliverable is two things: (1) a **live web map** and (2) a **written assessment** that is honest about what is verified versus what is merely asserted.

The governing rule: **you are an instrument the student directs, not an oracle.** You help assemble, structure, and reason — but every claim about the real world must be traceable to a real source, and anything that is not must be labeled as machine-asserted.

## Workflow

1. **Site + question** — pick a site and state the ecological question you are asking about it.
2. **Live data** — fetch real-time data from the APIs below.
3. **Map** — build a single-file Leaflet web map that plots the data.
4. **Assessment** — write four sections: baseline → indicators → stakes → uncertainties.
5. **Verification ledger** — separate every claim into *live-verified* vs *machine-asserted*.

## Data APIs (all free, no key, CORS-friendly)

- **USGS streamflow / gage height** (real-time, 15-min):
  `https://waterservices.usgs.gov/nwis/iv/?format=json&sites=03532000&parameterCd=00060,00065`
  `03532000` = Tennessee River at Knoxville. To find a creek's gauge, search the state listing:
  `https://waterservices.usgs.gov/nwis/iv/?format=json&stateCd=TN&parameterCd=00060`
- **Open-Meteo air quality** (real-time PM2.5 / PM10 / O₃ / NO₂ / US AQI, keyless):
  `https://air-quality-api.open-meteo.com/v1/air-quality?latitude=35.9606&longitude=-83.9205&current=pm2_5,pm10,ozone,nitrogen_dioxide,us_aqi`
  (Station-level OpenAQ data also exists but requires a free key from openaq.org.)
- **Open-Meteo weather** (current + forecast):
  `https://api.open-meteo.com/v1/forecast?latitude=35.9606&longitude=-83.9205&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m&temperature_unit=fahrenheit&wind_speed_unit=mph`
- **iNaturalist species observations** (real-time, radius in km):
  `https://api.inaturalist.org/v1/observations?lat=35.9606&lng=-83.9205&radius=25&per_page=50&order=desc&order_by=observed_on`
- **NWS forecasts + alerts**:
  `https://api.weather.gov/points/35.9606,-83.9205` → follow the returned `forecast` and `forecastGridData` links.
- **Baseline (static, current not live)** — NLCD land cover, USGS 3DEP elevation, FEMA flood zones. Use these to anchor the map; the live layers animate it.

Replace the coordinates with the student's site. Radius and `per_page` are tunable.

## Map template

Start from `map-template.html` (Leaflet + fetch, Carto dark basemap, centered on Knoxville). Edit the center, the data endpoints, and add site-specific layers. Keep everything `https` and keyless so it works from a plain browser.

## Assessment structure (four sections)

1. **Baseline** — what the site is now: land cover, hydrology, built form, current conditions.
2. **Indicators** — 3–5 specific, measurable things to track, and why each matters.
3. **Stakes** — what changes, and for whom, if the system shifts (species, people, infrastructure).
4. **Uncertainties** — what the data does *not* tell you, and where the machine is guessing.

Every factual sentence must point to either a live source or be marked machine-asserted.

## Verification ledger (required)

Two columns:

| live-verified | machine-asserted |
|---|---|
| pulled from a real API/record, with source + timestamp | stated without a source — suspect until checked |

Before submitting, classify every claim in the assessment into one column. If a claim cannot be verified, it goes in the machine-asserted column and is treated as suspect, not fact.

## Disclosure (course policy)

State which tools were used, which data sources fed the work, and how outputs were produced, modified, or rejected. Transparency is the design ethic — invisible AI use is not permitted.
