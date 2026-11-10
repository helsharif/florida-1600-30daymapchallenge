# Day 10: Prompting Only

This project was produced through a conversation with OpenAI Codex for [#30DayMapChallenge 2026, Day 10](https://30daymapchallenge.com/#2026-themes). The human contribution was the project brief, historical/visual requirements, output location, and publishing direction. The agent performed the source research, implementation, rendering, visual review, corrections and repository preparation.

## Brief, summarized

Create a geographically defensible, satellite-style map of Florida circa 1565–1600. Include Indigenous communities and managed landscapes, appropriate Spanish colonial sites, natural ecosystems and predevelopment hydrology. Distinguish known, approximate and disputed features; avoid anachronistic missions or invented village footprints. Use Python and established geospatial libraries, export a high-resolution PNG and geospatial outputs, and document assumptions. Prioritize a statewide minimum viable reconstruction.

Requested title: **Florida, circa 1600 — At the Dawn of Spanish Colonization**.

## How the agent implemented the brief

1. Researched institutional ecological and archaeological sources.
2. Downloaded FGDL's Davis vegetation layer, SFWMD's pre-channelization Kissimmee layer, and generalized context geography.
3. Inspected SFWMD's predevelopment report. Because its original GIS database was not retrieved, registered the published Everglades figure approximately and made that limitation explicit.
4. Built projected raster classes and an independent evidence-provenance layer.
5. Added a selected historical-site table with sources and separate spatial/temporal confidence.
6. Rendered reproducible procedural textures, labels and explanatory notes in Python.
7. Inspected the preview, corrected label overlaps and verified output structure.
8. Prepared a public repository with the source code and compact shareable outputs, excluding credentials and large regeneration products.

No text-to-image model generated the map geometry. No OpenAI API key is needed to rerun it. The code is an artifact of the prompting process; rerunning the artifact performs deterministic GIS/rendering operations, not another AI conversation. This distinction makes the published result reproducible without an AI subscription.

## What the result does not establish

The map is not an independently peer-reviewed historical reconstruction. It remains a regional interpretation constrained by incomplete evidence. Its fine texture is illustrative, its baseline vegetation is temporally imperfect, and its Everglades registration requires replacement with native historical GIS for greater precision. The limitations and next research steps are in [METHODOLOGY.md](METHODOLOGY.md).
