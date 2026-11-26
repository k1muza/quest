"""Validate every saved agricultural polygon against actual river and bank geometry."""
from pathlib import Path
import json
from shapely.geometry import shape
root=Path(__file__).resolve().parent
data=json.loads((root/'farm-footprints.json').read_text())
river=shape(data['river']); bank=river.buffer(data['clearance'],quad_segs=64)
footprints=[(f['kind'],shape(f['geometry'])) for f in data['footprints']]
assert footprints and river.is_valid and not river.is_empty
violations=[]
for i,(kind,poly) in enumerate(footprints):
    if poly.is_empty or not poly.is_valid or poly.distance(river)<data['clearance']-1e-6 or poly.intersection(bank).area>1e-6:
        violations.append((i,kind))
result={'footprints':len(footprints),'minimumClearance':min(p.distance(river) for _,p in footprints),'waterIntersectionArea':sum(p.intersection(river).area for _,p in footprints),'bankIntersectionArea':sum(p.intersection(bank).area for _,p in footprints),'violations':violations}
print(json.dumps(result,indent=2));assert not violations
