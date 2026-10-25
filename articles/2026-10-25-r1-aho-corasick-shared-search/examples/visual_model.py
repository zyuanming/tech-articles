"""Reproducible visual instrumentation of the teaching model. CC0-1.0."""
from collections import deque
from pathlib import Path
import json
from ac import Matcher, naive

def measure():
    patterns = ['he', 'she', 'his', 'hers']
    ac = Matcher(patterns)
    seen = {''}; insertions = []
    for p in patterns:
        path = [p[:i] for i in range(1, len(p)+1)]
        insertions.append(dict(pattern=p, path=path, shared=[s for s in path if s in seen],
                               new=[s for s in path if s not in seen]))
        seen.update(path)
    queue = deque(ac.child[0].values()); bfs = []
    while queue:
        before = [ac.label[v] for v in queue]
        v = queue.popleft(); queue.extend(ac.child[v].values())
        bfs.append(dict(pop=ac.label[v], depth=len(ac.label[v]), before=before,
                        after=[ac.label[u] for u in queue]))
    hits, trace = ac.feed('ushershis')
    assert sorted(hits) == naive(patterns, 'ushershis')
    events = [dict(depth=0, kind='start', label='起点')]
    for row in trace:
        for f in row['fallback']:
            events.append(dict(depth=0 if f=='根' else len(f), kind='fail', label=f, i=row['i']))
        events.append(dict(depth=0 if row['state']=='根' else len(row['state']),
                           kind='consume', label=row['ch'], i=row['i']))
    rises = sum(max(0,b['depth']-a['depth']) for a,b in zip(events,events[1:]))
    drops = sum(max(0,a['depth']-b['depth']) for a,b in zip(events,events[1:]))
    fail_count = sum(e['kind']=='fail' for e in events)
    assert fail_count <= drops <= rises <= len(trace)
    assert events[-1]['depth'] == rises-drops
    dense_patterns = ['a','aa','aaa']; dense_text = 'aaaa'
    dense_hits, dense_trace = Matcher(dense_patterns).feed(dense_text)
    assert sorted(dense_hits) == naive(dense_patterns,dense_text)
    assert len(dense_hits)==9
    multi_hits,multi_trace=Matcher(patterns).feed('ushershisx')
    assert multi_trace[-1]['fallback']==['s','根'] and multi_trace[-1]['state']=='根'
    she=ac.label.index('she'); sh=ac.label.index('sh')
    chain=[]; v=she
    while v:
        chain.append(dict(state=ac.label[v], outputs=[patterns[i] for i in ac.end[v]]))
        v=ac.link[v]
    return dict(patterns=patterns, text='ushershis', insertions=insertions, bfs=bfs,
        layers=[[s or '根' for s in ['']+[r['pop'] for r in bfs] if len(s)==d] for d in range(max(map(len,ac.label))+1)],
        build_step=dict(parent='sh',char='e',parent_fail=ac.label[ac.fail[sh]],child='she',child_fail=ac.label[ac.fail[she]]),
        multi=multi_trace[-1],output_chain=chain,trace=trace,events=events,rises=rises,drops=drops,fail_count=fail_count,
        dense=dict(patterns=dense_patterns,text=dense_text,hits=dense_hits,trace=dense_trace))

if __name__=='__main__':
    data=measure()
    Path(__file__).with_name('visual-results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print('Visual instrumentation verified; dense outputs:',len(data['dense']['hits']))
