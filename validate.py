"""Implementation checks, not historical validation. No credentials are read."""
from pathlib import Path
import json
import numpy as np
import geopandas as gpd
import rasterio
from PIL import Image
from build_map import CRS, W, H, T

O=Path(__file__).resolve().parent/'outputs'
report={}
for name in ['landscape_classes.tif','evidence_provenance.tif','satellite_style_rgb.tif']:
    with rasterio.open(O/name) as f:
        assert f.crs.to_string()==CRS
        assert f.shape==(H,W) and f.transform==T
        report[name]={'shape':list(f.shape),'bands':f.count,'crs':str(f.crs),'bytes':(O/name).stat().st_size}
with rasterio.open(O/'landscape_classes.tif') as f: classes=f.read(1)
with rasterio.open(O/'evidence_provenance.tif') as f: prov=f.read(1)
assert set(np.unique(prov))=={0,1,2,3,4}
assert np.array_equal(classes>0,prov>0)
assert 19 not in np.unique(classes), 'Modern urban class must not survive'
assert (prov==3).sum()>100000, 'Everglades override missing or unexpectedly tiny'
assert (prov==4).sum()>1000, 'Kissimmee evidence missing'
s=gpd.read_file(O/'historical_sites.geojson')
assert len(s)==10
assert s.loc[s.name.str.startswith('San Anton'),'temporal_confidence'].iloc[0]=='inactive'
assert s.loc[s.name=='Calos / Mound Key','temporal_confidence'].iloc[0]=='uncertain'
assert s['source'].str.startswith('https://').all()
assert not s.name.str.contains('San Luis|Castillo|Santa Elena').any()
assert s.geometry.is_valid.all()
layers=gpd.list_layers(O/'reconstruction.gpkg')['name'].tolist()
assert set(layers)=={'historical_sites','davis1967_reference','kissimmee_1954_reference','river_course_proxies','everglades_generalized_proxy'}
report['geopackage_layers']=layers
for name in ['Florida_circa_1600.png','Florida_circa_1600_preview.jpg','Evidence_provenance.png']:
    with Image.open(O/name) as im:
        im.verify()
    with Image.open(O/name) as im: report[name]={'pixels':list(im.size)}
assert report['Florida_circa_1600.png']['pixels']==[6000,6300]
report['validation']='PASS: structure, CRS, coverage, class handling, site status, image integrity; no scientific accuracy certification'
(O/'validation_report.json').write_text(json.dumps(report,indent=2))
print(report['validation'])
