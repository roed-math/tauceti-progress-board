#!/usr/bin/env python3
"""Assemble the Tau Ceti progress board prototype from local.json, coverage.json, merged.json, open.json."""
import json, datetime as dt, collections, html, sys, pathlib

S = pathlib.Path(__file__).parent
local = json.load(open(S / 'local.json'))
cov = json.load(open(S / 'coverage.json'))
merged = json.load(open(S / 'merged.json'))
openprs = json.load(open(S / 'open.json'))

TODAY = dt.date(2026, 9, 2)
WEEKS = 16
ROADMAP_HEAD = 'f78e6bb'
SNAPSHOT = '2026-09-02T15:40Z'
topics = json.load(open(S / 'topics.json'))

def roadmap_of(pr):
    labs = [l['name'] for l in (pr.get('labels') or {}).get('nodes', pr.get('labels') or [])] if isinstance(pr.get('labels'), dict) else [l['name'] for l in pr.get('labels') or []]
    labs = [l for l in labs if l.startswith('roadmap/') and l not in ('roadmap/none', 'roadmap/Unknown')]
    return labs[0][len('roadmap/'):] if len(labs) == 1 else None

def week_start(d):
    return d - dt.timedelta(days=d.weekday())

week0 = week_start(TODAY) - dt.timedelta(weeks=WEEKS - 1)
weeks = [week0 + dt.timedelta(weeks=i) for i in range(WEEKS)]

act = collections.defaultdict(lambda: {'weekly': [0] * WEEKS, 'total': 0, 'net': 0, 'last': None, 'd30': 0, 'open': 0})
allweekly = [0] * WEEKS
for pr in merged:
    r = roadmap_of(pr)
    day = dt.date.fromisoformat(pr['mergedAt'][:10])
    wi = (week_start(day) - week0).days // 7
    if 0 <= wi < WEEKS:
        allweekly[wi] += 1
    if r is None:
        continue
    a = act[r]
    a['total'] += 1
    a['net'] += pr['additions'] - pr['deletions']
    if 0 <= wi < WEEKS:
        a['weekly'][wi] += 1
    if (TODAY - day).days < 30:
        a['d30'] += 1
    if a['last'] is None or day > a['last']:
        a['last'] = day
for pr in openprs:
    r = roadmap_of(pr)
    if r:
        act[r]['open'] += 1

def states(s):
    return list(s) if s else None

rows = []
def mkrow(name, rec, parent=None, state=None):
    st = rec.get('status')
    layers = rec['layers']
    cv = states(cov.get(name)) if parent is None else states(cov.get('RepresentationTheory/children', {}).get(name))
    if cv is None:
        cv = ['?'] * len(layers)
    a = act.get(name) if parent is None else None
    row = {
        'name': name, 'title': rec['title'].removeprefix('Roadmap: '), 'parent': parent,
        'state': state or rec.get('state', 'active'),
        'topic': topics['map'].get(parent or name, 'Unsorted'),
        'layers': layers, 'cov': cv,
        'sorries': rec.get('suggested_sorries'),
        'status': None, 'windows': rec.get('windows', []),
        'act': None,
    }
    if st:
        ts = dt.datetime.fromisoformat(st['ts'].replace('Z', '+00:00')).date()
        row['status'] = {'sha': st['sha'], 'date': ts.isoformat(), 'age': (TODAY - ts).days,
                         'glance': st['glance'], 'frontier': st['frontier'], 'named': st['named']}
    if a:
        since = 0
        if st:
            since = sum(1 for pr in merged if roadmap_of(pr) == name and pr['mergedAt'] > st['ts'])
        row['act'] = {'weekly': a['weekly'], 'total': a['total'], 'net': a['net'],
                      'last': a['last'].isoformat() if a['last'] else None,
                      'lastAge': (TODAY - a['last']).days if a['last'] else None,
                      'd30': a['d30'], 'open': a['open'], 'sinceSnapshot': since}
    return row

for name, rec in local.items():
    rows.append(mkrow(name, rec))
    for cn, crec in rec.get('children', {}).items():
        rows.append(mkrow(cn, crec, parent=name, state=rec.get('state', 'active')))

# Completed roadmaps with no STATUS are done by declaration.
for r in rows:
    if r['state'] == 'completed' and all(c == '?' for c in r['cov']):
        r['cov'] = ['d'] * len(r['layers'])

data = {'today': TODAY.isoformat(), 'weeks': [w.isoformat() for w in weeks], 'allweekly': allweekly,
        'roadmapHead': ROADMAP_HEAD, 'snapshot': SNAPSHOT, 'rows': rows, 'topics': topics['order'],
        'mergedTotal': len(merged), 'openTotal': len(openprs),
        'firstMerge': min(p['mergedAt'][:10] for p in merged)}

template = open(S / 'board_template.html').read()
out = template.replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False))
open(S / 'tauceti-progress-board.html', 'w').write(out)
open(S / 'index.html', 'w').write(out)
print('rows', len(rows), 'bytes', len(out))
