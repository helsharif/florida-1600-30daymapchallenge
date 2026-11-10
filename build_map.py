"""Florida c.1600: evidence-led regional reconstruction, not historical imagery.
Run from any directory. No credentials or paid API required.
"""
from pathlib import Path
import json, hashlib, importlib.metadata
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.features import rasterize, shapes
from rasterio.transform import from_origin
from rasterio.warp import reproject, Resampling
from pyproj import Transformer
from scipy.ndimage import gaussian_filter, distance_transform_edt
from shapely.geometry import Point, box, shape
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
from PIL import Image
import pymupdf
from fetch_data import get, arc

ROOT=Path(__file__).resolve().parent; D=ROOT/'data'; O=ROOT/'outputs'; O.mkdir(exist_ok=True)
CRS='EPSG:3087'; RES=250; SEED=1600
# Florida GDL Albers, metres; no Web Mercator area/scale distortion.
X0,Y0,X1,Y1=-25000,15000,900000,845000
W=int((X1-X0)/RES); H=int((Y1-Y0)/RES); T=from_origin(X0,Y1,RES,RES)
extent=(X0,X1,Y0,Y1)
proj=Transformer.from_crs(4326,CRS,always_xy=True)
def xy(lon,lat): return proj.transform(lon,lat)
def burn(g,values=1,dtype='uint8'):
    if np.isscalar(values): values=[values]*len(g)
    pairs=[(a,int(b)) for a,b in zip(g.geometry,values) if a is not None and not a.is_empty]
    return rasterize(pairs,out_shape=(H,W),transform=T,fill=0,dtype=dtype)
def tif(name,arr,nodata=None,**tags):
    a=arr if arr.ndim==3 else arr[None]
    with rasterio.open(O/name,'w',driver='GTiff',height=H,width=W,count=a.shape[0],dtype=a.dtype,crs=CRS,transform=T,compress='deflate',tiled=True,nodata=nodata) as f:
        f.write(a); f.update_tags(reconstruction='Interpretive circa-1600 regional proxy; not observed imagery',**tags)
        f.build_overviews([2,4,8,16],Resampling.nearest)

def prepare_everglades():
    """Recover generalized classes from published Fig.15, not native PDLD GIS.
    One geographic anchor and published scale; no claim of survey accuracy.
    """
    p=D/'sfwmd2007.pdf'
    if not p.exists(): p.write_bytes(get('https://www.sfwmd.gov/sites/default/files/documents/pdvd2_techpubhesm-02_june2007.pdf').content)
    doc=pymupdf.open(p); pix=doc[52].get_pixmap(matrix=pymupdf.Matrix(2,2),alpha=False)
    a=np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width,3)
    # Exact source colours sampled from legend, with distance tolerance for JPEG artefacts.
    legend=[(842,240,18),(909,240,8),(932,240,16),(956,240,20),
            (1003,240,21),(1025,240,17),(1048,240,13),(1070,240,3),(1093,240,5)]
    colors=np.array([np.median(a[y-3:y+3,x-3:x+3],axis=(0,1)) for y,x,c in legend])
    crop=a[370:1080,635:992].astype('float32')
    dist=np.sum((crop[:,:,None,:]-colors[None,None,:,:])**2,axis=3)
    idx=np.argmin(dist,axis=2); src=np.array([c for y,x,c in legend],np.uint8)[idx]
    src[np.min(dist,axis=2)>55**2]=0
    # 40 statute miles / 205 source pixels. Anchor: northern Lake Okeechobee.
    s=64373.76/205; ux,uy=Transformer.from_crs(4326,26917,always_xy=True).transform(-80.83,27.20)
    st=from_origin(ux+(635-796)*s,uy-(370-380)*s,s,s)
    out=np.zeros((H,W),np.uint8)
    reproject(src,out,src_transform=st,src_crs='EPSG:26917',dst_transform=T,dst_crs=CRS,resampling=Resampling.nearest)
    # Remove isolated rendering specks; internal ridge/slough dots are absorbed into marsh matrix.
    from scipy.ndimage import label
    lab,n=label(out>0); sizes=np.bincount(lab.ravel()); out[sizes[lab]<40]=0
    (D/'everglades_registration.json').write_text(json.dumps({
      'source':'SFWMD HESM-02 (2007), Figure 15, printed p.37 / PDF index52',
      'method':'Manual north-lake anchor + published scale; assumed north-up UTM17N',
      'anchor_image_xy':[796,380],'anchor_lonlat':[-80.83,27.20],
      'metres_per_pixel':s,'crop_xyxy':[635,370,992,1080],
      'positional_uncertainty':'Unvalidated regional registration; allow roughly 5 km, not a statistical confidence interval',
      'limitations':'Generalized marsh classes only; not native PDLD, not a c.1600 observation; source ridge/slough texture not resolved.'},indent=2))
    return out

def make_sites():
    # Publicly interpreted site-centre coordinates, deliberately rounded; never excavation boundaries.
    rows=[
      ('Anhaica',-84.270,30.438,'Indigenous','supported','supported','Apalachee town; reoccupied after 1540; no Spanish mission in 1600.','https://dos.fl.gov/historical/archaeology/projects/hernando-de-soto-1539-1540-winter-encampment-at-anhaica-apalachee/'),
      ('Tocobaga / Safety Harbor',-82.677,28.014,'Indigenous','supported','approximate','Archaeological town identified with Tocobaga; exact 1600 population and extent unknown.','https://pinellas.gov/tocobaga-temple-mound/'),
      ('Calos / Mound Key',-81.865,26.418,'Indigenous','supported','uncertain','Calusa capital; abandoned in 1569, reestablished early 1600s. Occupancy in exactly 1600 uncertain.','https://www.floridamuseum.ufl.edu/science/investigating-the-calusa/'),
      ('Tequesta',-80.190,25.768,'Indigenous','approximate','approximate','Miami River mouth village area; not the modern municipality of Tequesta.','https://www.miami.gov/Planning-Zoning-Land-Use/Historic-Preservation'),
      ('San Agustin',-81.312,29.891,'Spanish','supported','supported','Founded 1565; mainland town from 1572. Regional locator, not 1565 encampment or later stone Castillo.','https://www.floridamuseum.ufl.edu/staugustine/timeline/disasters-and-rebuilding/'),
      ('Nombre de Dios',-81.314,29.905,'Mission','supported','supported','Timucua mission community established by 1587; site locator, not a church footprint.','https://www.floridamuseum.ufl.edu/staugustine/timeline/the-church-and-the-missions/'),
      ('San Juan del Puerto',-81.440,30.442,'Mission','supported','supported','Mission at Timucua community on Fort George Island, documented by late 1500s.','https://www.nps.gov/timu/learn/historyculture/missions_fgi.htm'),
      ('San Sebastian',-81.325,29.865,'Mission','approximate','supported','Mission south of St Augustine established by 1587; locality is schematic, not a verified site coordinate.','https://museumoffloridahistory.com/explore/exhibits/permanent-exhibits/la-florida/forever-changed-phase-2/the-first-spanish-period/missions/'),
      ('San Anton de Carlos (1566-1569)',-81.865,26.418,'Former Spanish','supported','inactive','Withdrawn 1569; retained only in historical reference layer, not active map symbols.','https://www.floridamuseum.ufl.edu/rrc/learn/'),
      ('De Soto landing area (1539)',-82.600,27.600,'Earlier expedition','disputed','inactive','Tampa Bay regional reference only; exact landing unresolved. No route geometry inferred.','https://www.nps.gov/articles/desoto.htm'),
    ]
    out=[]
    for name,lon,lat,kind,loc,date,note,url in rows:
        out.append(dict(name=name,longitude=lon,latitude=lat,kind=kind,location_confidence=loc,temporal_confidence=date,reference_year=1600,coordinate_method='Rounded public site/locality locator; not surveyed',notes=note,source=url,geometry=Point(lon,lat)))
    g=gpd.GeoDataFrame(out,crs=4326)
    g.to_file(O/'historical_sites.geojson',driver='GeoJSON')
    g.drop(columns='geometry').to_csv(O/'historical_sites.csv',index=False)
    return g.to_crs(CRS)

def main():
    print('Rasterizing statewide vegetation',flush=True)
    dav=gpd.read_file(D/'davis1967.geojson').to_crs(CRS); dav.geometry=dav.geometry.make_valid()
    codes={'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'12':12,'13':13,'14':14,'15':15,'16':16,'16a':20,'16b':20,'17':17,'w':18,'u':19}
    cls=burn(dav,dav.TYPE.map(codes))
    provenance=np.where(cls>0,1,0).astype('uint8')
    land=gpd.read_file(D/'ne_10m_land.zip',bbox=(-89,24,-79,32))
    land.geometry=land.geometry.make_valid()
    land=land.clip(box(-89,24,-79,32)).to_crs(CRS)
    lm=burn(land)>0
    # Generalized modern land fills only small gaps inside Florida bbox; no arbitrary southern wetland fill.
    context=lm & (cls==0)
    urban=cls==19
    valid=(cls>0)&(cls!=18)&(cls!=19)
    nearest=distance_transform_edt(~valid,return_distances=False,return_indices=True)
    cls[urban]=cls[tuple(nearest[:,urban])]; provenance[urban]=2
    del nearest
    eg=prepare_everglades(); use=eg>0
    cls[use]=eg[use]; provenance[use]=3
    print('Applying pre-channelization Kissimmee wetlands',flush=True)
    k=gpd.read_file(D/'kissimmee1954.geojson').to_crs(CRS)
    def kc(s):
        s=str(s).lower()
        if any(v in s for v in ['canal','ditch','pasture','agric','urban','road']): return 0
        if any(v in s for v in ['river','water','aquatic','broadleaf marsh','wetland herb']): return 18 if ('river' in s or 'water' in s) else 16
        if 'cypress' in s: return 7
        if any(v in s for v in ['swamp','wetland forest','wetland shrub','willow']): return 8
        if any(v in s for v in ['marsh','wet prairie','miscellaneous wetland']): return 16
        return 0
    k['render_class']=k.BCODE_GROUP_DESC.map(kc)
    kb=burn(k[k.render_class>0],k.loc[k.render_class>0,'render_class']); use=kb>0
    cls[use]=kb[use]; provenance[use]=4
    k.to_file(O/'reconstruction.gpkg',layer='kissimmee_1954_reference',driver='GPKG')
    sites=make_sites(); sites.to_file(O/'reconstruction.gpkg',layer='historical_sites',driver='GPKG')
    # Source water polygons retained: modern reservoirs never inserted.
    rivers=gpd.read_file(D/'ne_10m_rivers_lake_centerlines.zip',bbox=(-88,24,-79.5,31.2)).to_crs(CRS)
    rivers=rivers[rivers['name'].isin(['Saint Johns','Suwannee']) & (rivers.featurecla=='River')].copy()
    rivers['caveat']='Generalized modern river course as regional proxy; no circa-1600 channel survey'
    rivers.to_file(O/'reconstruction.gpkg',layer='river_course_proxies',driver='GPKG')
    dav['source_year']=1967; dav['caveat']='Natural vegetation proxy, not observed circa-1600 cover'
    dav.to_file(O/'reconstruction.gpkg',layer='davis1967_reference',driver='GPKG')
    ep=[{'geometry':shape(geom),'class_id':val,'caveat':'SFWMD2007 Fig15 approximate registration; not native GIS'} for geom,val in shapes(eg,mask=eg>0,transform=T)]
    gpd.GeoDataFrame(ep,crs=CRS).to_file(O/'reconstruction.gpkg',layer='everglades_generalized_proxy',driver='GPKG')
    tif('landscape_classes.tif',cls,0,class_lookup='See class_legend.json; raster cell 250 m does not imply 250 m historical accuracy')
    tif('evidence_provenance.tif',provenance,0,codes='1 Davis1967 proxy; 2 urban nearest-neighbour infill; 3 SFWMD2007 figure registration; 4 Kissimmee1954 wetland/water proxy')
    print('Rendering deterministic satellite-style textures',flush=True)
    palette={0:(13,41,55),1:(150,151,113),2:(74,100,66),3:(58,91,58),4:(52,78,46),5:(111,119,78),6:(104,116,72),7:(45,73,57),8:(38,65,48),9:(44,83,63),12:(45,73,43),13:(116,126,74),14:(81,104,77),15:(64,94,58),16:(92,111,72),17:(123,133,93),18:(31,66,65),20:(97,110,63),21:(111,122,77)}
    lut=np.zeros((256,3),np.float32)
    for n,c in palette.items(): lut[n]=c
    rgb=lut[cls]; rgb[context]=[34,49,45]
    rng=np.random.default_rng(SEED)
    noise=np.zeros((H,W),np.float32)
    for sigma,weight in [(0.6,0.035),(2,0.035),(8,0.04),(28,0.035),(95,0.025)]:
        q=gaussian_filter(rng.normal(size=(H,W)).astype('float32'),sigma)
        q/=max(q.std(),0.00001); noise+=q*weight
    # A texture is a visual cue, NOT a mapped canopy, field, tree island or DEM.
    terrain=(cls>0)&(cls!=18)
    rgb[terrain]*=(1+noise[terrain,None])
    # Water brightness based only on distance from land; never presented as bathymetry.
    ocean=(cls==0)&(~context)
    distance=distance_transform_edt(~(terrain|context)).astype('float32')*RES
    near=np.exp(-distance/15000)
    rgb[ocean]=np.array([12,38,53])+near[ocean,None]*np.array([16,31,24])
    rgb[ocean]*=(1+noise[ocean,None]*0.07)
    rgb[cls==18]*=(1+noise[cls==18,None]*0.13)
    rgb=np.clip(rgb,0,255).astype('uint8')
    tif('satellite_style_rgb.tif',rgb.transpose(2,0,1),rendering='Procedural colour texture, not spectral reflectance, bathymetry or measured tree cover',seed=str(SEED))
    labels={n:next((row.DESCRIPT for row in dav.itertuples() if codes[row.TYPE]==n),{21:'Medium-hydroperiod marsh'}.get(n,'Unknown')) for n in palette}
    labels[0]='Outside reconstruction'; labels[20]='Generalized long-hydroperiod / ridge-and-slough marsh'; labels[21]='Medium-hydroperiod marsh'
    (O/'class_legend.json').write_text(json.dumps({str(k):{'name':labels[k],'rgb':list(v)} for k,v in palette.items()},indent=2))
    render(rgb,sites,rivers,provenance)
    manifest={'seed':SEED,'crs':CRS,'resolution_m':RES,'shape':[H,W],'class_pixels':{str(int(n)):int((cls==n).sum()) for n in np.unique(cls)},'provenance_pixels':{str(int(n)):int((provenance==n).sum()) for n in np.unique(provenance)},'versions':{n:importlib.metadata.version(n) for n in ['numpy','geopandas','rasterio','scipy','matplotlib','shapely','pyproj','pillow','pymupdf']}}
    manifest['inputs_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in D.iterdir() if p.suffix in ['.geojson','.zip','.pdf','.json'] and p.name!='sha256.json'}
    (O/'build_manifest.json').write_text(json.dumps(manifest,indent=2))
    print('Finished',flush=True)

def render(rgb,sites,rivers,provenance):
    plt.rcParams.update({'font.family':'DejaVu Sans','text.color':'#e9eeeb'})
    fig=plt.figure(figsize=(20,21),facecolor='#0b202b')
    ax=fig.add_axes([.025,.135,.95,.765]); ax.set_facecolor('#0d2937')
    ax.imshow(rgb,extent=extent,origin='upper',interpolation='bilinear',zorder=0)
    ax.set_xlim(X0,X1); ax.set_ylim(Y0,Y1); ax.set_aspect('equal'); ax.set_axis_off()
    rivers.plot(ax=ax,color='#789c98',linewidth=.55,alpha=.7,zorder=2)
    halo=[pe.withStroke(linewidth=3,foreground='#142e2b',alpha=.95)]
    def txt(lon,lat,s,size=11,color='#e9eeeb',**kw):
        x,y=xy(lon,lat); return ax.text(x,y,s,fontsize=size,color=color,path_effects=halo,zorder=6,**kw)
    # Familiar water labels are modern orientation aids, not claimed 1600 toponyms.
    for lon,lat,s,sz,rot in [(-85.5,27.9,'G U L F   O F   M E X I C O',16,0),(-79.9,27.5,'A T L A N T I C   O C E A N',15,90),(-81.13,24.68,'F L O R I D A   K E Y S',10,12),(-80.75,27.02,'Lake\nOkeechobee',9,0),(-81.26,26.03,'B I G   C Y P R E S S',9,0),(-80.63,26.14,'E V E R G L A D E S',11,80)]:
        txt(lon,lat,s,sz,'#adc5c8',ha='center',rotation=rot)
    for lon,lat,s in [(-84.55,30.76,'APALACHEE'),(-82.35,30.15,'TIMUCUA-SPEAKING PEOPLES'),(-81.72,26.9,'CALUSA'),(-80.48,25.55,'TEQUESTA')]:
        txt(lon,lat,s,10,'#d3cba8',ha='center',fontstyle='italic')
    # Labels with leaders allow real site positions without enlarging settlement footprints.
    placements={
      'Anhaica':(-84.55,30.20,'Anhaica','Apalachee town'),
      'Tocobaga / Safety Harbor':(-84.0,28.65,'Tocobaga','Safety Harbor site'),
      'Calos / Mound Key':(-83.20,26.18,'Calos / Mound Key*','Calusa capital; date caveat'),
      'Tequesta':(-79.96,25.48,'Tequesta ~','Miami River village area'),
      'San Agustin':(-80.37,29.62,'San Agustín · 1565','St. Augustine'),
      'San Juan del Puerto':(-80.65,30.55,'San Juan del Puerto','Timucua mission community'),
    }
    for row in sites.itertuples():
        if row.name not in placements: continue
        tx,ty,title,sub=placements[row.name]; x,y=row.geometry.x,row.geometry.y; lx,ly=xy(tx,ty)
        col='#e3c174' if row.kind=='Indigenous' else '#f39d75'
        marker='o' if row.kind=='Indigenous' else ('D' if row.kind=='Mission' else 's')
        hollow=row.temporal_confidence=='uncertain' or row.location_confidence!='supported'
        ax.scatter([x],[y],s=45,marker=marker,c='none' if hollow else col,edgecolors=col,linewidths=1.2,zorder=8)
        ax.plot([x,lx],[y,ly],color=col,alpha=.75,lw=.65,zorder=5)
        ax.text(lx,ly+4500,title,fontsize=12,color=col,path_effects=halo,zorder=7)
        ax.text(lx,ly-9000,sub,fontsize=9,color='#dbe5df',path_effects=halo,zorder=7)
    # Regional callout lists close mission sites; tiny distance cannot be resolved statewide.
    txt(-80.30,29.12,'Nearby Timucua missions:\nNombre de Dios · by 1587\nSan Sebastián ~ · by 1587',9,'#efbd9f',linespacing=1.5,va='top')
    txt(-85.0,31.18,'Beyond the Florida reconstruction',9,'#7e9695',ha='center')
    # Earlier event, explicitly distinct from active settlements.
    x,y=xy(-82.60,27.60); lx,ly=xy(-84.05,27.18)
    ax.scatter([x],[y],s=50,facecolors='none',edgecolors='#9bb5bd',marker='v',zorder=7)
    ax.plot([x,lx],[y,ly],color='#9bb5bd',lw=.6,ls=(0,(3,4)),zorder=5)
    ax.text(lx,ly,'1539 · De Soto landing\nTampa Bay area; exact site disputed',fontsize=9,color='#a9bdc3',path_effects=halo,linespacing=1.5)
    # Legend occupies open Gulf, not the land surface.
    xx,yy=xy(-87.2,27.75)
    ax.text(xx,yy,'READING THE LANDSCAPE',fontsize=12,weight='bold',color='#f0e5c9')
    for i,(c,t) in enumerate([('#667548','Pine savannas & flatwoods'),('#345337','Hardwood & swamp forests'),('#637040','Marsh, prairie & slough mosaics'),('#305440','Mangroves & coastal wetlands')]):
        ax.add_patch(plt.Rectangle((xx,yy-24000-i*19000),10000,8000,color=c))
        ax.text(xx+17000,yy-22500-i*19000,t,fontsize=10)
    yy-=117000
    ax.text(xx,yy,'PEOPLE & PLACES',fontsize=12,weight='bold',color='#f0e5c9')
    for i,(m,c,t) in enumerate([('o','#e3c174','Indigenous town / community'),('s','#f39d75','Spanish colonial town'),('D','#f39d75','Mission within an Indigenous community')]):
        ax.scatter([xx+5000],[yy-23000-i*22000],marker=m,s=45,c=c)
        ax.text(xx+17000,yy-26000-i*22000,t,fontsize=9.5)
    ax.text(xx,yy-95000,'Filled: supported site location\nOpen / ~: approximate location or date caveat\nMarkers locate sites; they are not settlement areas.',fontsize=9,color='#c1cdd0',linespacing=1.7,va='top')
    ax.text(xx,yy-167000,'AN INHABITED LANDSCAPE',fontsize=12,weight='bold',color='#f0e5c9')
    ax.text(xx,yy-192000,'Farming, fire management, shellworks and canoe travel\nshaped this landscape. Their precise statewide footprints\nare not recoverable from the available evidence.\nNo invented fields, buildings or trails are drawn.',fontsize=9.5,color='#c1cdd0',linespacing=1.7,va='top')
    # Grid north and projected scale.
    sx,sy=xy(-87.1,24.25)
    ax.plot([sx,sx+100000],[sy,sy],color='#e9eeeb',lw=3)
    for q in [0,50000,100000]: ax.plot([sx+q,sx+q],[sy-3000,sy+3000],color='#e9eeeb',lw=1)
    for q,label in [(0,'0'),(50000,'50'),(100000,'100 km')]:
        ax.text(sx+q,sy+10000,label,fontsize=9,ha='center')
    ax.text(sx,sy-18000,'Florida GDL Albers · EPSG:3087',fontsize=8,color='#a9bdc3')
    ax.annotate('N',xy=(X1-47000,Y1-53000),xytext=(X1-47000,Y1-100000),ha='center',fontsize=12,arrowprops=dict(arrowstyle='-|>',color='#d7e1dc',lw=1.2))
    fig.text(.055,.957,'Florida, circa 1600 — At the Dawn of Spanish Colonization',fontsize=25,weight='bold')
    fig.text(.055,.928,'Historical landscape reconstruction based on ecological, geographic, and archaeological evidence.',fontsize=13,color='#bdcbd0',style='italic')
    fig.text(.055,.905,'SATELLITE-STYLE RECONSTRUCTION   /   REGIONAL EVIDENCE, NOT HISTORICAL IMAGERY',fontsize=10,color='#e3c174')
    fig.text(.055,.113,'WHAT IS KNOWN — AND WHAT IS INFERRED',fontsize=11,weight='bold',color='#e3c174')
    fig.text(.055,.100,'Vegetation: Davis / FGDL (1967) regional proxy; SFWMD predevelopment Everglades (2007, generalized figure); Kissimmee floodplain (1952–54).\nCoasts and rivers are generalized geographic proxies, not surveyed 1600 positions. Texture and coastal water shading are illustrative.\n* Mound Key: capital documented in 1566; reoccupation in the early 1600s. Its exact 1600 occupancy is uncertain. Spanish fort abandoned 1569.',fontsize=9.5,color='#c3d0d1',linespacing=1.6,va='top')
    fig.text(.055,.040,'Selected sites only • Indigenous labels do not delimit political borders • Water / landscape names are modern orientation aids\nNo later inland missions or stone Castillo • Santa Elena lies outside this Florida map • Sources and uncertainty: accompanying methodology',fontsize=9,color='#98b0b8',linespacing=1.6)
    fig.text(.945,.020,'#30DayMapChallenge 2026   /   Day 10 · Prompting Only',ha='right',fontsize=10,color='#e3c174')
    fig.savefig(O/'Florida_circa_1600.png',dpi=300,facecolor=fig.get_facecolor())
    plt.close(fig)
    with Image.open(O/'Florida_circa_1600.png') as im:
        im.thumbnail((1600,1680)); im.convert('RGB').save(O/'Florida_circa_1600_preview.jpg',quality=92)
    # Independent provenance plate; same georeferencing as the main raster.
    f,a=plt.subplots(figsize=(12,12),facecolor='#eef0e9')
    colors=np.array([[225,232,229],[104,135,105],[225,157,72],[83,151,188],[137,95,168]],np.uint8)
    a.imshow(colors[provenance],extent=extent); a.set_axis_off()
    a.set_title('Florida reconstruction: evidence provenance',color='#18332c',fontsize=18,pad=20)
    handles=[Line2D([0],[0],marker='s',ls='',color=colors[i]/255,markersize=11,label=s) for i,s in enumerate(['Outside mapped reconstruction','Davis 1967: regional natural-vegetation proxy','Former urban cells: nearest natural class (low confidence)','SFWMD 2007 Figure 15: approximate regional registration','Kissimmee 1952–54: pre-channelization wetland / water proxy'])]
    a.legend(handles=handles,loc='lower left',frameon=True,labelcolor='#18332c',fontsize=10)
    f.savefig(O/'Evidence_provenance.png',dpi=180,facecolor=f.get_facecolor()); plt.close(f)

if __name__=='__main__': main()
