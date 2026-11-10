# Methodology and uncertainty

## Scope and date

Target: Florida around **1600**, with clearly labeled earlier contact context. This is a regional, historically informed reconstruction, not a literal view of a specific day, season or hydrologic state. The title requested for the project is retained; Spanish colonization had already been underway for several decades by this date. Indigenous occupation and landscape management long predate it.

The deliverable is a credible starting map with an auditable workflow. It does not achieve a fully validated statewide 1600 vegetation or channel reconstruction. The distinction is visible on the plate and retained in the data. No generative image model, Google imagery, modern imagery with roads erased, or paid API was used.

## Spatial inputs and transformations

| Input | Use | Temporal / spatial limitation |
|---|---|---|
| [UF GeoPlan / FGDL, Davis 1967 natural vegetation](https://sagittarius.at.geoplan.ufl.edu/arcgis/rest/services/fgdl/Davis_1967_Vegetation/MapServer/0) | Statewide vegetation polygons; 1,357 records downloaded and count-checked | 1967 natural-community map, not a 1600 survey; broad classes and generalized boundaries |
| [SFWMD, Zahina et al. 2007, HESM-02](https://www.sfwmd.gov/sites/default/files/documents/pdvd2_techpubhesm-02_june2007.pdf), Fig. 15, printed p.37 | Predrainage Okeechobee–Everglades landscape proxy, overriding Davis where the published figure supplies a class | Figure-derived regional registration, not the original PDLD GIS; predevelopment primarily anchored to 19th-century evidence, not 1600 |
| [SFWMD Kissimmee pre-channelization vegetation 1952–1954](https://services1.arcgis.com/sDAPyc2rGRn7vf9B/arcgis/rest/services/VEG_KISSIMMEE_RIVER_1952_1954/FeatureServer/0) | Wetland and open-water polygons supersede Davis locally | Before channelization, but after earlier regional alterations; does not prove 1600 river positions |
| [Natural Earth 1:10m physical data](https://www.naturalearthdata.com/downloads/10m-physical-vectors/) | Context land, selected generalized St. Johns and Suwannee river lines | Modern generalized reference, not historical shoreline or channel data; “1:10m” means 1:10 million, not 10-metre resolution |

FNAI's [Florida Forever Conservation Needs Assessment technical report](https://www.fnai.org/PDFs/TechReport_v51_withapps.pdf) also uses Davis to identify potential historical pinelands. That supports treating the classes as ecological context; it does not validate this map for 1600. The [GeoPlan description](https://www.geoplan.ufl.edu/agol/ADA/maps/Davis_1967_Vegetation/Davis%20Vegetation%20Map%20%281967%29.html) identifies the statewide layer as 1967 vegetation and cautions that its classes are generalized.

All vectors are projected to **NAD83(HARN) / Florida GDL Albers, EPSG:3087**. The common grid has 250 m cells. Published geometry is retained in the GeoPackage; the rendering grid is not a new accuracy standard. Invalid source geometry is repaired before rasterization. No present-day political boundary is presented as a 1600 frontier.

### Recovering the Everglades regional proxy

The native SFWMD PDLD geodatabase was not located in the accessible public services during this build. Instead, the workflow renders Figure 15 at 144 dpi and classifies its legend colors inside the main map frame. The published 40-mile scale bar gives approximately 314 m per source pixel. A manually selected northern Lake Okeechobee reference anchors a north-up UTM 17N registration, then the image classes are reprojected to the output grid. Full parameters are in `data/everglades_registration.json`.

This is an **approximate registration**, without a fitted network of surveyed control points or independent georeferencing RMSE. Allow roughly 5 km for regional positional interpretation; this is an analyst caution, not a measured confidence interval. Sharp boundaries should not be read literally. No local shoreline or lake-level inference should be made from it. Its purpose is to depict an extensive wetland basin instead of modern drained land. Fine tree-island stippling is not treated as mapped tree islands; broad long-hydroperiod and ridge/slough classes are combined.

### Replacing altered landscapes

Eleven Davis polygons have an urban class. Their raster cells receive the nearest nonurban, nonwater Davis class, separately marked with provenance code 2. This is a transparent, low-confidence interpolation, not evidence that the historical vegetation was identical to its neighbor. No hidden smoothing or fabricated farm geometry repairs these areas. Historical Indigenous clearings cannot be recovered by this operation.

In the Kissimmee layer, open water, aquatic vegetation, broadleaf marsh, wet prairie, miscellaneous wetlands, and wetland forest/shrub categories are used. Human-made structures, modern uplands of uncertain use, unknowns and bare-ground categories are not used as historical restoration evidence. The raw source attributes remain available. Canals, dams, urban grids and road layers are never imported.

## Hydrology and coastlines

The Everglades override reintroduces a regional predrainage wetland pattern, and the Kissimmee input supplies pre-channelization water/floodplain evidence. Remaining lakes and wetland corridors follow the generalized Davis layer. Natural Earth river lines are used only for the St. Johns and Suwannee; modern reservoir data are not inserted. Lake Seminole is deliberately excluded.

There is **no statewide reconstruction of preengineering river meanders, lake levels, floodplain inundation or 1600 tidal inlets**. No terrain inundation model or relative-sea-level adjustment was attempted. Coastal shading is a distance-to-land visual gradient, not bathymetry, water depth, reef position or water clarity. The coastline is a generalized proxy assembled from the ecological source geometry and modern context; barrier islands and estuaries can differ materially from 1600.

[NOAA's shoreline mapping history](https://shoreline.noaa.gov/history.html) begins centuries after this target date. [USGS research integrating paleoecology and hydrologic models](https://www.usgs.gov/publications/estimating-late-19th-century-hydrology-greater-everglades-ecosystem-integration) demonstrates that even 19th-century Everglades water conditions require inference and model assessment. These sources inform the limitations; their datasets were **not** spatially incorporated. Nor is the 19th-century reference assumed to be unchanged since 1600.

## Human geography and chronological screening

Coordinates are rounded public site or locality locators, not excavation centroids, parcel boundaries, or settlement footprints. “Supported location” refers to the site identification at regional map scale. It does not establish continuous occupation in exactly 1600. Spatial and temporal confidence are separate fields.

| Feature | Treatment and evidence |
|---|---|
| Anhaica | Indigenous town. [Florida Division of Historical Resources](https://dos.fl.gov/historical/archaeology/projects/hernando-de-soto-1539-1540-winter-encampment-at-anhaica-apalachee/) identifies the archaeological contact site and reports reoccupation after de Soto. The later 1633 mission is not mapped. |
| Tocobaga / Safety Harbor | Indigenous town at a supported archaeological locality; exact 1600 extent and population remain uncertain. [Pinellas County interpretation](https://pinellas.gov/tocobaga-temple-mound/) supports village, mound and plaza evidence. |
| Calos / Mound Key | Hollow marker and explicit date caveat. [Florida Museum archaeological summary](https://www.floridamuseum.ufl.edu/science/investigating-the-calusa/) identifies the Calusa capital and its early-1600s return after the 1569 abandonment. No assertion of certain occupancy in exactly 1600. |
| Tequesta | Approximate Miami River village locality; not the modern town of Tequesta. [City of Miami archaeological context](https://www.miami.gov/Planning-Zoning-Land-Use/Historic-Preservation) associates the river-mouth archaeology with the village. |
| San Agustín | Colonial town, established 1565; marker refers to the mainland town after 1572, not the initial encampment. [Florida Museum chronology](https://www.floridamuseum.ufl.edu/staugustine/timeline/disasters-and-rebuilding/) documents repeated destruction and rebuilding. No stone Castillo or modern street grid. |
| Nombre de Dios | Timucua mission community, established by 1587; named in a nearby-site callout to avoid crowding. [Florida Museum](https://www.floridamuseum.ufl.edu/staugustine/timeline/the-church-and-the-missions/). |
| San Juan del Puerto | Late-16th-century mission at an Indigenous community on Fort George Island. [NPS](https://www.nps.gov/timu/learn/historyculture/missions_fgi.htm) discusses its location and cites Pareja's 1599 letter to the Crown. NPS and other summaries differ on foundation timing, so no exact foundation year is assigned on the map. |
| San Sebastián | Documented by 1587 south of St. Augustine; approximate locality, named only in the callout. [Museum of Florida History](https://museumoffloridahistory.com/explore/exhibits/permanent-exhibits/la-florida/forever-changed-phase-2/the-first-spanish-period/missions/). |
| Fort San Antón de Carlos | Included as inactive in the reference table, not as an active map symbol. [Florida Museum chronology](https://www.floridamuseum.ufl.edu/rrc/learn/) dates the Spanish withdrawal to 1569. |
| De Soto landing | Earlier event labeled 1539, with an open triangle indicating the broad Tampa Bay area. The coordinate is not a claimed exact landing point. [NPS interpretation](https://www.nps.gov/articles/desoto.htm). |

The selected set is intentionally incomplete. San Antonio de Enacape and other possible early mission locations require additional locality/date review before inclusion. Santa Elena is outside Florida. Later inland mission networks, San Luis, and the stone Castillo are excluded. No continuous expedition path is drawn: connecting known endpoints would invent intervening route precision. Earlier Spanish outposts at Tocobaga and Tequesta are not portrayed as operating in 1600. Ponce de León's debated landing is not assigned a point.

Pineland is omitted from active sites rather than treating its later documentary identification as proof of exact 1600 occupation. The [2023 archaeological study](https://doi.org/10.1371/journal.pone.0295906) reports the absence of identified intact post-1500 deposits while recognizing isolated European trade objects. This is an example of why a known archaeological site is not automatically a securely dated town for this map.

Colonial records are consulted through archaeological publications and institutional histories, not a new transcription or exhaustive archival review. The NPS cites Francisco Pareja to the Crown, 8 March 1599, AGI 54-5-20/6; Mound Key research evaluates Spanish descriptions against excavated evidence. These are traceable documentary foundations, with their interpretation distinguished from direct contemporary observation by the mapmaker.

### Human modification without fabricated footprints

Indigenous farming, burning, shell construction, managed waterways and travel shaped Florida. The agricultural landscapes of Apalachee and Timucua communities must not be generalized to the Calusa, whose political economy centered on aquatic resources. [Thompson et al. (2020), Ancient engineering of fish capture and storage](https://pmc.ncbi.nlm.nih.gov/articles/PMC7165460/) provides direct archaeological evidence of Calusa watercourts. These facts motivate site labels and explanatory text. Individual crop fields, burns, trails, mound outlines and settlement building patterns are **not drawn** without mapped evidence. At statewide scale many would be subpixel anyway. No claim of pristine wilderness is intended.

## Visual synthesis

Land-cover classes are assigned muted natural colors and modulated by deterministic multiscale noise (seed 1600). Water receives subdued variation; sea-edge color uses distance to land. The result evokes a satellite basemap with readable hybrid-style labels, while keeping geometry controlled by the spatial layers. Texture is not remotely sensed reflectance, measured canopy structure, tree-island geometry, topographic relief, or evidence of a particular season. The rendering is therefore satellite-style rather than scientifically photorealistic at local scale.

Separate symbols distinguish Indigenous towns, colonial towns and mission communities. Open symbols and text identify temporal or locality uncertainty; the main text explains that marker size does not represent settlement area. Cultural labels are broad orientation labels, not ethnic boundary polygons. Modern waterbody and ecological names are explicitly identified as orientation aids.

## Audit and next improvements

`validate.py` checks raster CRS, bounds and dimensions; verifies class/provenance coverage, output image dimensions, layer availability and chronological status; and records source-registration diagnostics. Visual review is required for layout. These checks validate implementation, not historical truth.

Highest priorities for a research-grade revision:

1. Obtain the native SFWMD PDLD/NSM historical geography and replace the approximate figure registration.
2. Incorporate statewide soils, geomorphology and independently assessed potential-natural vegetation; validate urban infill instead of nearest-neighbor assignment.
3. Develop an explicit shoreline/estuary model with regional relative-sea-level and sedimentary evidence; reconstruct engineered river reaches from historical surveys.
4. Review sites and documented landscape management with specialist archaeologists and relevant Indigenous communities; add local mapped evidence without publishing sensitive locations.
5. Register documented expedition corridors as uncertain areas, rather than precise lines; research remaining circa-1600 mission localities.

Sources accessed 10 November 2026. Data layers are retained with source attribution. Natural Earth is public domain. Consult the originating agencies' metadata for their respective data-use conditions; no blanket license for third-party source material is asserted.
