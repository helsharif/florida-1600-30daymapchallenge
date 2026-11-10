from pathlib import Path
import requests, json, hashlib
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parent
D=ROOT/'data'; D.mkdir(exist_ok=True)
def get(url,params=None):
    r=requests.get(url,params=params,timeout=120); r.raise_for_status(); return r
def arc(name,url):
    path=D/(name+'.geojson')
    if path.exists(): return
    meta=get(url,{'f':'json'}).json(); (D/(name+'_metadata.json')).write_text(json.dumps(meta,indent=2))
    ids=get(url+'/query',{'where':'1=1','returnIdsOnly':'true','f':'json'}).json()['objectIds']
    features=[]
    for i in range(0,len(ids),200):
        j=get(url+'/query',{'objectIds':','.join(map(str,ids[i:i+200])),'outFields':'*','outSR':4326,'f':'geojson'}).json()
        features.extend(j['features'])
    assert len(features)==len(ids)
    path.write_text(json.dumps({'type':'FeatureCollection','features':features}))
    print(name,len(features),flush=True)
if __name__=='__main__':
    arc('davis1967','https://sagittarius.at.geoplan.ufl.edu/arcgis/rest/services/fgdl/Davis_1967_Vegetation/MapServer/0')
    arc('kissimmee1954','https://services1.arcgis.com/sDAPyc2rGRn7vf9B/arcgis/rest/services/VEG_KISSIMMEE_RIVER_1952_1954/FeatureServer/0')
    for name in ['land','lakes','rivers_lake_centerlines']:
        f=D/('ne_10m_'+name+'.zip')
        if not f.exists():
            f.write_bytes(get('https://naturalearth.s3.amazonaws.com/10m_physical/'+f.name).content)
        print(name,f.stat().st_size,flush=True)
    manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in D.iterdir() if p.is_file()}
    (D/'sha256.json').write_text(json.dumps(manifest,indent=2))
