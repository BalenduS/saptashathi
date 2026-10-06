"""Check notes/prose/chN.json: passages cover every entry (preamble + verses) of the chapter once, in order."""
import json, sys, glob, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(f'{ROOT}/site/data/text.json', encoding='utf-8'))['sections']

def refs(sid):
    s = T[sid]
    return [f'pre{i}' for i in range(len(s['preamble']))] + [v['ref'] for v in s['verses']]

def check(path):
    sid = os.path.basename(path)[:-5]
    d = json.load(open(path, encoding='utf-8'))
    R, probs, pos = refs(sid), [], 0
    for k in ('title',):
        if not d.get(k, {}).get('en') or not d[k].get('te'): probs.append(f'missing {k}')
    for i, p in enumerate(d.get('passages', [])):
        a, b = p.get('from'), p.get('to', p.get('from'))
        if a not in R or b not in R: probs.append(f'#{i} unknown ref {a}-{b}'); continue
        ia, ib = R.index(a), R.index(b)
        if ia != pos: probs.append(f'#{i} {a}: expected to start at {R[pos] if pos < len(R) else "END"}')
        if ib < ia: probs.append(f'#{i} {a}-{b} reversed')
        if not p.get('en') or not p.get('te'): probs.append(f'#{i} {a}-{b} missing en/te')
        pos = ib + 1
    if pos != len(R): probs.append(f'stops before {R[pos] if pos < len(R) else "?"} (covered {pos}/{len(R)})')
    return sid, probs

if __name__ == '__main__':
    files = sys.argv[1:] or sorted(glob.glob(f'{ROOT}/notes/prose/ch*.json'))
    bad = 0
    for f in files:
        sid, pr = check(f)
        print(sid, 'OK' if not pr else pr[:8]); bad += bool(pr)
    sys.exit(1 if bad else 0)
