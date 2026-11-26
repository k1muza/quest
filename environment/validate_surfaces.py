"""Independently sample the generated road and river centrelines against model mesh polygons."""
import json
from inspect_ports import surfaces
from shapely.affinity import rotate
from shapely.geometry import LineString
L=json.load(open('layout.json')); cache={};bad=[];stats={'pathSegments':0,'roadSamples':0,'riverSamples':0,'bridgePathSegments':0,'offSurface':0};worst=0
for t in L['cells']:
 for p in t.get('pathMetadata',[]):
  key=(t['asset'],t['angle']);kind=p['kind'];stats['pathSegments']+=1
  if key not in cache:cache[key]=[rotate(g,-key[1],origin=(0,0)) for g in surfaces('assets/'+key[0]+'.gltf')]
  if 'crossing' in t['asset'] and kind=='road':stats['bridgePathSegments']+=1;continue
  poly=cache[key][0 if kind=='road' else 1];ls=LineString(p['localXZ']);count=max(2,int(ls.length/.025))
  for i in range(count+1):
   q=ls.interpolate(i/count,normalized=True);d=q.distance(poly);worst=max(worst,d);stats[kind+'Samples']+=1
   if d>.025:stats['offSurface']+=1;bad.append((t['c'],t['r'],kind,round(d,4)))
report={'stats':stats,'maxOutsideDistanceModelUnits':worst,'offSurfaceSamples':bad,'toleranceModelUnits':.025,'bridgeDeckCentreHeight':L['bridgeDeck'][20][1]};print(json.dumps(report,indent=2));json.dump(report,open('surface-validation.json','w'),indent=2)
if bad:raise SystemExit(1)
