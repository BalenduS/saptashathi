"""Check meaning files against the text: every entry annotated, every glossed word found in its verse."""
import json, re, sys, glob, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
t = json.load(open(f'{ROOT}/site/data/text.json', encoding='utf-8'))['sections']
norm = lambda s: re.sub(r"[^a-zāīūṛṝḷṅñṭḍṇśṣṃḥ]", "", s.lower())
sids = sys.argv[1:] or [os.path.basename(f)[:-5] for f in glob.glob(f'{ROOT}/site/data/notes/*.json') if not f.endswith('index.json')]
bad = 0
for sid in sids:
    n = json.load(open(f'{ROOT}/site/data/notes/{sid}.json', encoding='utf-8'))
    ents = {v['ref']: v['iast'] for v in t[sid]['verses']}
    ents.update({f'pre{i}': p['iast'] for i, p in enumerate(t[sid]['preamble'])})
    missing = [r for r in ents if r not in n]
    low = []
    for ref, note in n.items():
        if ref == '_intro': continue
        v = norm(ents[ref]); ws = [norm(w[0]) for w in note['pada']]
        hit = sum(1 for w in ws if w[:max(2, int(len(w) * .6))] in v)
        if hit / len(ws) < 0.5: low.append(f'{ref} ({hit}/{len(ws)})')
    print(f'{sid}: {len(ents)} entries, {len(ents)-len(missing)} annotated, missing {missing}, weak word match {low}')
    bad += len(missing) + len(low)
sys.exit(1 if bad else 0)
