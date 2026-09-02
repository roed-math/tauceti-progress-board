import json, re, pathlib, sys
root=pathlib.Path('.')
out={}
for base,state in (('TauCetiRoadmap','active'),('Completed','completed')):
    for d in sorted((root/base).iterdir()):
        rd=d/'README.md'
        if not d.is_dir() or not rd.exists(): continue
        name=d.name; txt=rd.read_text()
        title=next((l[2:].strip() for l in txt.splitlines() if l.startswith('# ')),name)
        layers=[re.sub(r'\s*\(.*\)\s*$','',l.lstrip('#').strip()) for l in txt.splitlines() if re.match(r'^#{2,4}\s+(Layer|Lane|Milestone|Part|Stage|Phase)\b',l)]
        sug=d/'Suggested.lean'
        sorries=len(re.findall(r'\bsorry\b',sug.read_text())) if sug.exists() else None
        rec={'name':name,'title':title,'state':state,'layers':layers,'readme_lines':len(txt.splitlines()),'suggested_sorries':sorries}
        st=d/'STATUS.md'
        if st.exists():
            s=st.read_text(); m=re.search(r'<!--tauceti-status:v1 (\{.*?\})-->',s)
            hdr=json.loads(m.group(1)) if m else {}
            g=re.search(r'\*\*At a glance\.\*\*\s*(.*)',s)
            fr=re.findall(r'^- \*\*(.+?)\*\*',s[s.find('## The frontier'):],re.M)
            named=re.findall(r'^- \*\*(.+?)\*\*',s[s.find('### Named results'):s.find('### Notable')] if '### Named results' in s else '',re.M)
            rec['status']={'sha':hdr.get('to_sha','')[:7],'ts':hdr.get('ts'),'glance':g.group(1).strip() if g else '','frontier':fr,'named':named}
        pg=d/'PROGRESS.md'
        if pg.exists():
            wins=[]
            for m in re.finditer(r'<!--tauceti-progress:v1 (\{.*?\})-->\s*\n## .*?(\d{4}-\d\d-\d\d) to (\d{4}-\d\d-\d\d)',pg.read_text(),re.S):
                j=json.loads(m.group(1)); wins.append({'from':m.group(2),'to':m.group(3),'prs':len(j['prs'])})
            rec['windows']=wins
        out[name]=rec

# --- Roadmaps whose layers are not `###` headings, and the one umbrella roadmap. ---
MANUAL_LAYERS = {
 'HodgeStructures': ['Core definitions','Worked instances','L0: the Hodge decomposition','L1: semisimplicity','L2: mixed Hodge structures and strictness','L3: Hodge numbers and the period domain'],
 'CFSGStatement': ['I0: the index of finite simple groups','S0: sporadic conventions','S1: the twenty-six sporadic presentations','L0: Lie-type carriers','L1: Steinberg endomorphisms','L2: twisted conventions','L3: the finite groups of Lie type','L4: the Lie-type assembly','A0: the classification statement'],
}
if 'ConformalMapping' in out:
    txt=(root/'TauCetiRoadmap/ConformalMapping/README.md').read_text()
    out['ConformalMapping']['layers']=[re.sub(r'\*|\.$','',m).strip() for m in re.findall(r'^- \*\*(L\d — [^*]+?)\*?\*?\s*(?:\(|\.\*\*|\*\*)',txt,re.M)]
for k,v in MANUAL_LAYERS.items():
    if k in out and not out[k]['layers']: out[k]['layers']=v
rt=root/'TauCetiRoadmap/RepresentationTheory'
if rt.is_dir():
    subs={}
    for p in sorted(rt.iterdir()):
        if not p.is_dir() or not (p/'README.md').exists(): continue
        t=(p/'README.md').read_text()
        title=next(l[2:].strip() for l in t.splitlines() if l.startswith('# '))
        layers=[re.sub(r'\s*\(.*\)\s*$','',l.lstrip('#').strip()) for l in t.splitlines() if re.match(r'^#{2,4}\s+(Layer|Lane|Part|Stage)\b',l)]
        sg=p/'Suggested.lean'; s=len(re.findall(r'\bsorry\b',sg.read_text())) if sg.exists() else None
        subs[p.name]={'name':p.name,'title':title.replace('Roadmap: ',''),'layers':layers,'suggested_sorries':s}
    out['RepresentationTheory']['children']=subs
    out['RepresentationTheory']['suggested_sorries']=sum(v['suggested_sorries'] or 0 for v in subs.values())

json.dump(out,open(sys.argv[1],'w'),indent=1)
print(len(out)); 
for n,r in out.items(): print(n, len(r['layers']), r['suggested_sorries'], r.get('status',{}).get('ts','-'), [w['prs'] for w in r.get('windows',[])])
