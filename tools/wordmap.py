"""Map each printed word (whitespace token) of a verse to the word-by-word glosses it contains.

Sanskrit sandhi fuses words, so one printed token may hold several glossed words. Glosses are
matched in order, by stem, against the tokens; the result is a list (one per token, across all
lines) of gloss indices. Used by build.py to power the tap-a-word popup.
"""
import re

NORM = re.compile(r"[^a-zāīūṛṝḷṅñṭḍṇśṣṃḥ]")
VOW = 'aāiīuūṛṝeo'
def norm(s): return NORM.sub('', s.lower())

def variants(w):
    """Forms a word can take at the start of a fused token."""
    v = {w}
    base = re.sub(r'(ṃ|ḥ|m)$', '', w)
    v.add(base)
    if re.search(r'aḥ$', w): v.add(w[:-2] + 'o')                       # tataḥ -> tato, saḥ -> so
    if base and base[-1] in VOW and len(base) >= 3: v.add(base[:-1] + '*')  # final vowel fused: devī -> devy…, taiḥ -> tair…
    if re.search(r'[td]$', base): v.add(base[:-1] + 'n'); v.add(base[:-1] + 'd')
    if len(base) > 4: v.add(base[:max(3, round(len(base) * .7))])
    return {x for x in v if len(x) >= 1}

def score(tok, w, vs):
    if not tok: return 0
    if tok == w or tok == re.sub(r'(ṃ|ḥ|m)$', '', w): return 4
    best = 0
    for x in vs:
        if x.endswith('*'):                                             # must be followed by a vowel or semivowel
            x = x[:-1]
            if len(x) >= 2 and tok.startswith(x) and len(tok) > len(x) and tok[len(x)] in VOW + 'yvr': best = max(best, 2)
            continue
        if len(x) >= 2 and tok.startswith(x): best = max(best, 3 if len(x) >= 3 else 2)
        elif len(x) >= 4 and x in tok: best = max(best, 1)
    base = re.sub(r'(ṃ|ḥ|m)$', '', w)
    if not best and len(base) == 2 and base[-1] in VOW and len(tok) > 2 and tok[0] == base[0] and tok[1] in VOW:
        best = 2                                                       # ca+api -> cāpi, sa+eva -> saiva
    if not best and len(base) >= 4 and base[0] in VOW and base[1:] in tok and not tok.startswith(base[1:]):
        best = 1                                                       # initial vowel fused: ca+ambike -> cāmbike
    return best

def tokens(iast):
    return [norm(tok) for line in iast.split('\n') for tok in line.split()]

def wordmap(iast, pada):
    toks = tokens(iast)
    res = [[] for _ in toks]
    p = 0
    subs = []
    for gi, g in enumerate(pada):
        for sub in g[0].split():
            w = norm(sub)
            if w: subs.append((gi, w, variants(w)))
    for gi, w, vs in subs:
        j = next((k for k in range(p, len(toks)) if score(toks[k], w, vs)), None)
        if j is None:
            j = next((k for k in range(0, p) if score(toks[k], w, vs) >= 2), None)
        if j is not None:
            if gi not in res[j]: res[j].append(gi)
            if j >= p: p = j
    # repeated words (yā … yā …): give still-empty tokens any gloss that matches them well
    for k, tok in enumerate(toks):
        if tok and not res[k]:
            hit = next((gi for gi, w, vs in subs if score(tok, w, vs) >= 3), None)
            if hit is not None: res[k].append(hit)
    for r in res: r.sort()
    return res
