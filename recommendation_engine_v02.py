import csv, math
from pathlib import Path
BASE=Path(__file__).parent
AXES=['street','minimal','utility','heritage','technical','military']
def load(name):
    with open(BASE/name,encoding='utf-8') as f: return list(csv.DictReader(f))
ENT=load('entities.csv'); REL=load('relationships.csv')
BY_NAME={x['name'].lower():x for x in ENT}
def vec(e): return [float(e[a]) for a in AXES]
def cosine(a,b):
    d=sum(x*y for x,y in zip(a,b)); na=math.sqrt(sum(x*x for x in a)); nb=math.sqrt(sum(y*y for y in b))
    return d/(na*nb) if na*nb else 0
def profile(selections):
    chosen=[BY_NAME[s.lower()] for s in selections if s.lower() in BY_NAME]
    if not chosen: raise ValueError('No known selections')
    return [sum(vec(e)[i] for e in chosen)/len(chosen) for i in range(len(AXES))], chosen
def relation_info(chosen_ids,target):
    vals=[]
    for r in REL:
        linked=((r['from_id'] in chosen_ids and r['to_id']==target['entity_id']) or (r['to_id'] in chosen_ids and r['from_id']==target['entity_id']))
        if linked: vals.append((float(r['strength']),r.get('relation_type','')))
    return max(vals, default=(0,''), key=lambda x:x[0])
def depth_value(e):
    return {'gateway':20,'explore':45,'deep':70,'rabbit hole':92}.get(e.get('discovery_depth','').lower(),50)
def recommend(selections, extra_taste=None):
    p, chosen=profile(selections)
    if extra_taste:
        for axis,val in extra_taste.items():
            if axis in AXES: p[AXES.index(axis)]=(p[AXES.index(axis)]+float(val))/2
    ids={e['entity_id'] for e in chosen}; rows=[]
    for e in ENT:
        if e['entity_id'] in ids or e['type']=='shop': continue
        sim=cosine(p,vec(e))*100; rel,rel_type=relation_info(ids,e); depth=depth_value(e)
        safe=.78*sim+.22*rel
        clone_pen=max(0,sim-94)*3
        deeper=.58*sim+.12*rel+.30*depth-clone_pen
        bridge=max(0,100-abs(sim-72)*2.4)
        surprise=.40*bridge+.35*depth+.25*sim-.18*rel
        rows.append({'entity':e,'sim':sim,'rel':rel,'safe':safe,'deeper':deeper,'surprise':surprise})
    safe=max(rows,key=lambda x:x['safe'])
    rem=[r for r in rows if r['entity']['entity_id']!=safe['entity']['entity_id']]
    deeper=max(rem,key=lambda x:x['deeper'])
    rem=[r for r in rem if r['entity']['entity_id']!=deeper['entity']['entity_id']]
    surprise=max(rem,key=lambda x:x['surprise'])
    def pack(r): return {'name':r['entity']['name'],'similarity':round(r['sim'],1),'depth':r['entity'].get('discovery_depth','')}
    return {'profile':dict(zip(AXES,[round(x,1) for x in p])),'SAFE':pack(safe),'GO_DEEPER':pack(deeper),'SURPRISE_ME':pack(surprise)}
if __name__=='__main__': print(recommend(['WTAPS','1LDK'], {'military':100}))
