"""Parse sanskritdocuments.org durga700.itx (ITRANS) into structured JSON.

Each section -> {id, title, kind, preamble:[blocks], verses:[{n, ref, kind, itrans, deva, telu, iast}]}
A verse ends at a line carrying a number marker `|| N||` or `|| C.N||`.
Unnumbered blocks before the first numbered verse (viniyoga, dhyanam) become preamble.
"""
import json, re, sys
from indic_transliteration import sanscript as S

SRC = 'durga700.itx'

SECTIONS = [  # (marker substring in \section line, id, english title, kind)
    ('argalAstotram', 'argala', 'Argalā Stotram', 'prayer'),
    ('kIlakastotram', 'kilakam', 'Kīlaka Stotram', 'prayer'),
    ('devI kavacham', 'kavacham', 'Devī Kavacham', 'prayer'),
]
for i, t in enumerate([
    'Madhu–Kaiṭabha Vadha', 'Mahiṣāsura Sainya Vadha', 'Mahiṣāsura Vadha',
    'Śakrādi Stuti', 'Devī Dūta Saṁvāda', 'Dhūmralocana Vadha',
    'Caṇḍa–Muṇḍa Vadha', 'Raktabīja Vadha', 'Niśumbha Vadha', 'Śumbha Vadha',
    'Nārāyaṇī Stuti', 'Bhagavatī Vākya (Phalaśruti)', 'Suratha–Vaiśya Varapradāna'], 1):
    SECTIONS.append((None, f'ch{i}', t, 'chapter'))
SECTIONS += [
    ('aparAdhakShamApaNa', 'kshamapana', 'Aparādha Kṣamāpaṇa Stotram', 'prayer'),
    ('devIsUktam', 'devisuktam', 'Ṛgvedokta Devī Sūktam', 'prayer'),
]

# Source typos corrected here (original file left untouched). (bad, good)
ERRATA = [
    ('bhayArtAH sharaNaM gatAH || 6.\n', 'bhayArtAH sharaNaM gatAH || 6||\n'),
    ('tatrArthalAbhashva', 'tatrArthalAbhashcha'),
    ('vijayA satata sthitA', 'vijayA satataM sthitA'),
    ('digbandhadevatAstatvam', 'digbandhadevatAstattvam'),
    ('daityaH kSheNarakto gamiShyati', 'daityaH kShINarakto gamiShyati'),
]

NUM = re.compile(r'\|\|\s*(?:(\d+)\\?\.)?(\d+)\s*\|\|\s*$')


def clean(s):
    s = re.sub(r'\\-\s*$', '', s); s = s.replace('\\-', '-').replace('\\,', ',').replace('\\.', '.').replace('\\', '')
    s = s.replace('d.h', 'd') if False else s
    return s.strip()


def xl(itrans):
    t = itrans.replace('.h', '')  # explicit halant marker; scheme handles word-final consonants
    return {
        'deva': S.transliterate(t, S.ITRANS, S.DEVANAGARI),
        'telu': S.transliterate(t, S.ITRANS, S.TELUGU),
        'iast': S.transliterate(t, S.ITRANS, S.IAST).replace('~', 'ṃ'),
    }


def main():
    raw = open(SRC, encoding='utf-8').read()
    for bad, good in ERRATA:
        assert raw.count(bad) == 1, bad
        raw = raw.replace(bad, good)
    lines = raw.split('\n')
    # locate section starts
    starts = []
    ch = 0
    for idx, ln in enumerate(lines):
        if not ln.startswith('\\section'):
            continue
        m = re.search(r'(\d+)\\\.', ln)
        if 'adhyAyaH' in ln:
            ch += 1
            starts.append((idx, f'ch{ch}'))
            continue
        for mark, sid, *_ in SECTIONS:
            if mark and mark in ln:
                starts.append((idx, sid))
    meta = {sid: (title, kind) for _, sid, title, kind in SECTIONS}
    # dhyanam at the very top (before argala)
    out = []
    first = starts[0][0]
    top = [l for l in lines[lines.index('\\begin{document}') + 1:first]]
    out.append(block_section('dhyanam', 'Śrī Caṇḍikā Dhyānam', 'prayer', top))
    for k, (idx, sid) in enumerate(starts):
        end = starts[k + 1][0] if k + 1 < len(starts) else len(lines)
        body = lines[idx + 1:end]
        title, kind = meta[sid]
        out.append(parse_section(sid, title, kind, body))
    json.dump(out, open('../site/data/text.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for s in out:
        print(f"{s['id']:12} entries={len(s['verses']):4} mantras={sum(v.get('count',1) for v in s['verses']):4} pre={[p.get('label') for p in s['preamble']]}")
    print('chapter mantra total', sum(v.get('count',1) for s in out if s['kind']=='chapter' for v in s['verses']))


SKIP = re.compile(r'^(%|\\|#|\s*\|\|\s*(iti|svasti|shrI|devI mAhAtmyam|atha)|uvAcha \d|.*evamAditaH|\.\s*aiM OM)')


def block_section(sid, title, kind, body):
    blocks, cur = [], []
    for ln in body:
        if SKIP.match(ln) or 'engtitle' in ln or 'itxtitle' in ln:
            continue
        if not ln.strip():
            if cur:
                blocks.append(cur); cur = []
            continue
        if ln.strip() == 'athavA':
            if cur:
                blocks.append(cur); cur = []
            continue
        cur.append(clean(ln))
    if cur:
        blocks.append(cur)
    verses = []
    for i, b in enumerate(blocks, 1):
        it = '\n'.join(b)
        verses.append({'n': i, 'n_end': i, 'count': 1, 'ref': f'{i}', 'kind': 'shloka', 'itrans': it, **xl(it)})
    return {'id': sid, 'title': title, 'kind': kind, 'preamble': [], 'verses': verses}


def parse_section(sid, title, kind, body):
    NUMR = re.compile(r'\|\|\s*(?:(\d+)\.)?(\d+)(?:-(\d+))?\s*\|\|\s*$')
    class UV:
        @staticmethod
        def match(c):
            return len(c) < 45 and re.search(r'(vAcha|UchuH|uvAca)\s*\|{1,2}\s*$', c) is not None
    pre, verses, cur, speaker = [], [], [], None
    block, mode = [], None
    def flush_block():
        nonlocal block, mode
        if block:
            pre.append({'label': mode or 'invocation', **({'itrans': '\n'.join(block)} )})
        block, mode = [], None
    for raw in body:
        ln = raw.rstrip()
        s = ln.strip()
        if not s or s.startswith('%') or s.startswith('\\section'):
            continue
        if 'samAptam' in s or 'adhyAyaH ||' in s or 'manvantare devImAhAtmye' in s or 'evamAditaH' in s:
            continue
        if re.match(r'^\|\|.*\|\|$', s) and not NUMR.search(clean(s)):
            continue
        if s.startswith('. aiM OM') or s == 'viniyogaH':
            if s == 'viniyogaH':
                flush_block(); mode = 'viniyoga'
            continue
        if 'svasti shrI' in s or s.startswith('##') or 'Encoded by' in s or s.startswith('. hrIM') or s.startswith('. klIM'):
            if 'Encoded' in s or s.startswith('##'):
                break
        c = clean(s)
        if 'klIM OM' in c or re.search(r'^(uvAcha \d|samastA )', c) or 'surathavaishyayor' in c:
            cur = []; continue
        if any(k in s for k in ('svasti shrI', '. hrIM', '. klIM', '|| iti ', 'devIkavachaM samAptam')):
            continue
        m = NUMR.search(c)
        if not verses and not m and not cur:
            # preamble zone
            if c.startswith('. dhyAnam') or c.startswith('dhyAnam'):
                flush_block(); mode = 'dhyanam'; continue
            if c.startswith('OM namashchaNDikAyai'):
                flush_block(); pre.append({'label': 'namaskara', 'itrans': c}); continue
            if c.startswith('asya') or c.startswith('OM asya'):
                if mode != 'viniyoga':
                    flush_block(); mode = 'viniyoga'
            if UV.match(c):
                flush_block(); speaker = c.rstrip(' |'); continue
            if mode in ('viniyoga', 'dhyanam'):
                block.append(c)
                if (mode == 'viniyoga' and re.search(r'viniyogaH\s*\|+$', c)) or (mode == 'dhyanam' and c.endswith('||')):
                    flush_block()
                continue
            cur.append(c)
            continue
        if not m and UV.match(c) and not cur:
            speaker = c.rstrip(' |'); continue
        flush_block()
        if m:
            text = NUMR.sub('', c).rstrip(' |')
            cur.append(text)
            a, b = int(m.group(2)), int(m.group(3) or m.group(2))
            it = '\n'.join(x for x in cur if x)
            is_uv = len(cur) == 1 and len(text) < 40 and re.search(r'(vAcha|UchuH|uvAca)\s*$', text) is not None
            ref = (f'{m.group(1)}.' if m.group(1) else '') + (f'{a}' if a == b else f'{a}-{b}')
            v = {'n': a, 'n_end': b, 'count': b - a + 1, 'ref': ref,
                 'kind': 'uvacha' if is_uv else 'shloka', 'itrans': it, **xl(it)}
            if speaker and not is_uv:
                v['speaker'] = speaker; v['speaker_xl'] = xl(speaker)
            speaker = None
            verses.append(v); cur = []
        else:
            cur.append(c)
    flush_block()
    if cur:
        pre.append({'label': 'trailing', 'itrans': '\n'.join(cur)})
    for p in pre:
        p.update(xl(p['itrans']))
    return {'id': sid, 'title': title, 'kind': kind, 'preamble': pre, 'verses': verses}


if __name__ == '__main__':
    main()
