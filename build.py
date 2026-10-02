"""Build the site.

notes/*.json (authored; words in IAST)  ->  site/data/notes/<section>.json + index.json
site/index.html (artifact fragment)      ->  dist/ (full GitHub Pages site: index.html, data, sw.js, manifest, icons)

Authored note format, keyed by verse ref exactly as in text.json:
{
  "_intro": {"en": "...", "te": "..."},                      # optional, chapter-level context
  "1.2": {"pada": [["sāvarṇiḥ", "Sāvarṇi", "సావర్ణి"], ...],  # word (IAST), English gloss, Telugu gloss
          "en": "meaning", "te": "అర్థం",
          "ctx": {"en": "...", "te": "..."}}                 # optional; applies until the next ctx
}
"""
import json, os, re, shutil, glob, hashlib
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, 'site')
DIST = os.path.join(ROOT, 'docs')


def build_notes():
    text = json.load(open(f'{SITE}/data/text.json', encoding='utf-8'))
    os.makedirs(f'{SITE}/data/notes', exist_ok=True)
    idx, problems = {}, []
    merged = {}
    for f in sorted(glob.glob(f'{ROOT}/notes/*.json')) + sorted(glob.glob(f'{ROOT}/notes/parts/*.json')):
        sid = os.path.basename(f)[:-5].split('.')[0]
        part = json.load(open(f, encoding='utf-8'))
        dup = set(part) & set(merged.get(sid, {})) - {'_intro'}
        if dup:
            problems.append(f'{sid}: duplicate refs across parts {sorted(dup)[:5]}')
        merged.setdefault(sid, {}).update(part)
    for sid, notes in merged.items():
        sec = text['sections'][sid]
        refs = {v['ref'] for v in sec['verses']} | {f'pre{i}' for i in range(len(sec['preamble']))}
        for k, n in notes.items():
            if k == '_intro':
                continue
            if k not in refs:
                problems.append(f'{sid}: unknown ref {k}')
            for w in n.get('pada', []):
                if len(w) != 3 or not all(isinstance(x, str) and x for x in w):
                    problems.append(f'{sid} {k}: bad word entry {w}')
            if not n.get('en') or not n.get('te'):
                problems.append(f'{sid} {k}: missing en/te meaning')
        json.dump(notes, open(f'{SITE}/data/notes/{sid}.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        idx[sid] = sum(1 for k in notes if k != '_intro')
    json.dump(idx, open(f'{SITE}/data/notes/index.json', 'w', encoding='utf-8'))
    return idx, problems


def slim_text():
    p = f'{SITE}/data/text.json'
    d = json.load(open(p, encoding='utf-8'))
    for s in d['sections'].values():
        for v in s['verses'] + s['preamble']:
            v.pop('itrans', None)
            v.get('speaker_xl', {}).pop('iast', None) if False else None
    json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))


def icons():
    os.makedirs(f'{SITE}/icons', exist_ok=True)
    for size in (180, 192, 512):
        im = Image.new('RGB', (size, size), (143, 29, 29))
        d = ImageDraw.Draw(im)
        s = size / 100
        gold = (240, 196, 110)
        d.ellipse([18 * s, 18 * s, 82 * s, 82 * s], outline=gold, width=max(2, int(2.2 * s)))
        d.polygon([(50 * s, 26 * s), (75 * s, 70 * s), (25 * s, 70 * s)], outline=gold, width=max(2, int(2.2 * s)))
        d.polygon([(50 * s, 74 * s), (25 * s, 30 * s), (75 * s, 30 * s)], outline=gold, width=max(2, int(1.4 * s)))
        r = 4 * s
        d.ellipse([50 * s - r, 50 * s - r, 50 * s + r, 50 * s + r], fill=gold)
        im.save(f'{SITE}/icons/icon-{size}.png')


MANIFEST = {
    "name": "Saptaśatī Reader", "short_name": "Saptaśatī",
    "description": "Śrī Durgā Saptaśatī verse by verse with Telugu and English meanings.",
    "start_url": "./", "scope": "./", "display": "standalone",
    "background_color": "#f6f4f1", "theme_color": "#8f1d1d",
    "icons": [{"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
              {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}]
}

SW = """// Offline cache: the whole text is small, so cache everything on install; network-first for data so new meanings arrive.
const V = '__VERSION__';
const CORE = ['./', 'index.html', 'manifest.json', 'data/text.json', 'data/notes/index.json', 'icons/icon-180.png', 'icons/icon-192.png', 'icons/icon-512.png', __NOTES__];
self.addEventListener('install', e => { e.waitUntil(caches.open(V).then(c => c.addAll(CORE)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (e.request.method !== 'GET') return;
  const fonts = /fonts\\.(googleapis|gstatic)\\.com$/.test(u.hostname);
  if (u.origin !== location.origin && !fonts) return;
  e.respondWith(caches.open(V).then(async c => {
    const hit = await c.match(e.request);
    const net = fetch(e.request).then(r => { if (r.ok || r.type === 'opaque') c.put(e.request, r.clone()); return r; }).catch(() => hit);
    return u.pathname.includes('/data/') ? net.then(r => r || hit) : (hit || net);
  }));
});
"""


def dist(idx):
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    shutil.copytree(f'{SITE}/data', f'{DIST}/data')
    shutil.copytree(f'{SITE}/icons', f'{DIST}/icons')
    frag = open(f'{SITE}/index.html', encoding='utf-8').read()
    head_end = frag.index('</style>') + len('</style>')
    page = ('<!doctype html>\n<html lang="te">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + frag[:head_end] + '\n</head>\n<body>\n' + frag[head_end:] + '\n</body>\n</html>\n')
    open(f'{DIST}/index.html', 'w', encoding='utf-8').write(page)
    json.dump(MANIFEST, open(f'{SITE}/manifest.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    shutil.copy(f'{SITE}/manifest.json', f'{DIST}/manifest.json')
    h = hashlib.sha1()
    for f in sorted(glob.glob(f'{DIST}/**/*', recursive=True)):
        if os.path.isfile(f):
            h.update(open(f, 'rb').read())
    sw = SW.replace('__VERSION__', 'ss-' + h.hexdigest()[:10]).replace(
        '__NOTES__', ', '.join(f"'data/notes/{k}.json'" for k in idx))
    open(f'{DIST}/sw.js', 'w').write(sw)
    open(f'{DIST}/.nojekyll', 'w').write('')
    open(f'{DIST}/404.html', 'w').write('<meta http-equiv="refresh" content="0; url=./">')


if __name__ == '__main__':
    slim_text()
    icons()
    idx, problems = build_notes()
    dist(idx)
    print('notes:', idx)
    print('problems:', len(problems))
    for p in problems[:40]:
        print('  ', p)
