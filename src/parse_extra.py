"""Parse the supplementary Gita Press angas and assemble the final ordered text.json.

Inputs: text.json from parse.py (core 700 + kavacham/argala/kilakam/kshamapana/devisuktam/dhyanam)
        + rAtrisUktam, deviiatharva, siddhakunjikaa, 3 rahasya files, tantradurgA700 (navarna/nyasa).
"""
import json, re
from parse import xl, clean

DATA = '../site/data/text.json'


def body_of(fname, start=None, stop=None):
    raw = open(fname, encoding='utf-8').read()
    raw = raw.split('\\begin{document}', 1)[1]
    if start:
        raw = raw[raw.index(start):]
    if stop:
        raw = raw[:raw.index(stop)]
    out = []
    skipping = [False]
    for ln in raw.split('\n'):
        s = ln.strip()
        if not s or s.startswith('\\') or s.startswith('%') or s == '##':
            continue
        if s.startswith('##') or s.startswith('## '):
            if re.match(r'^##\s*var\s*##\s*OM aM kaM', s):
                skipping[0] = True          # multi-line variant mantra block (Kunjika)
            continue
        if skipping[0]:
            if re.search(r'\|\|\s*\d+\s*\|\|$', s):
                skipping[0] = False
            continue
        s = re.sub(r'\s*##.*$', '', s).strip()   # inline variant note -> drop to EOL
        s = re.sub(r"\\[`'\"]|[`]", '', s)     # vedic svara marks
        s = s.replace('\\"', '').replace('"', '')
        if s:
            out.append(s)
    return out


NUMR = re.compile(r'(?:\|\||\.\.)\s*(?:10\\?\.127\\?\.0?)?(\d+)\s*(?:\|\||\.\.)?\s*$')


def generic(sid, title, kind, lines, num=NUMR, skip=()):
    pre, verses, cur, speaker, block, mode = [], [], [], None, [], None
    for s in lines:
        if any(k in s for k in skip):
            continue
        c = clean(s)
        if re.search(r'(vAcha|UchuH)\s*\|{0,2}$', c) and len(c) < 40:
            speaker = c.rstrip(' |'); continue
        if not verses and (c.startswith('asya') or c.startswith('OM asya') or mode == 'viniyoga'):
            mode = 'viniyoga'; block.append(c)
            if re.search(r'viniyogaH\s*\|+$', c):
                pre.append({'label': 'viniyoga', 'itrans': '\n'.join(block)}); block, mode = [], None
            continue
        if re.match(r'^(shrI\s?gaNeshAya|shrIgaNeshAya)', c):
            continue
        m = num.search(c)
        if m:
            cur.append(num.sub('', c).rstrip(' |.'))
            n = int(m.group(1)); it = '\n'.join(cur)
            v = {'n': n, 'n_end': n, 'count': 1, 'ref': str(n), 'kind': 'shloka', 'itrans': it, **xl(it)}
            if speaker:
                v['speaker'] = speaker; v['speaker_xl'] = xl(speaker); speaker = None
            verses.append(v); cur = []
        else:
            cur.append(c)
    for p in pre:
        p.update(xl(p['itrans']))
    return {'id': sid, 'title': title, 'kind': kind, 'preamble': pre, 'verses': verses}


def ritual(sid, title, groups):
    """groups: [(label_en, [itrans lines...])] -> each line one 'step' entry."""
    verses, n = [], 0
    for label, lines in groups:
        for it in lines:
            n += 1
            verses.append({'n': n, 'n_end': n, 'count': 1, 'ref': str(n), 'kind': 'ritual',
                           'group': label, 'itrans': it, **xl(it)})
    return {'id': sid, 'title': title, 'kind': 'ritual', 'preamble': [], 'verses': verses}


def main():
    core = {s['id']: s for s in json.load(open(DATA, encoding='utf-8'))}

    ratri_v = generic('ratri-vedic', 'Vedokta Rātri Sūktam', 'prayer',
                      [re.sub(r'(?<=[A-Za-z~^.])1(?=[A-Za-z ])', '', l)  # strip svarita-kampa digit
                       for l in body_of('rAtrisUktam.itx', 'OM rAtrI', 'parishiShTam')],
                      num=re.compile(r'\|\|\s*10\\?\.127\\?\.0?(\d+)\s*$'))
    ratri_v['verses'] = [v for v in ratri_v['verses'] if v['n'] <= 8]
    ratri_v['source_note'] = 'Ṛgveda 10.127 (svara marks omitted)'

    athar = generic('atharvashirsha', 'Devyatharvaśīrṣam', 'prayer',
                    body_of('deviiatharva.itx', 'OM sarve vai devA'),
                    num=re.compile(r'\|\|\s*(\d+)\s*\|\|\s*$'),
                    skip=('iti ', 'shAntiH shAntiH', 'Proofread', 'Encoded', 'Please send', 'Last updated', 'http'))

    kunj = generic('kunjika', 'Siddha Kuñjikā Stotram', 'prayer',
                   body_of('siddhakunjikaa.itx', 'OM asya', 'iti shrIrudrayAmale'),
                   num=re.compile(r'\|\|\s*(\d+)\s*\|\|\s*$'))

    rah = [generic(f'rahasya-{k}', t, 'prayer', body_of(f, 'asya' if k == 'pradhanika' else 'R^iShiruvAcha', 'iti shrImArkaNDeya'),
                   num=re.compile(r'\|\|\s*(\d+)\s*\|\|\s*$'))
           for k, t, f in [('pradhanika', 'Prādhānika Rahasyam', 'prAdhAnikarahasyam.itx'),
                           ('vaikrtika', 'Vaikṛtika Rahasyam', 'vaikRitikarahasyam.itx'),
                           ('murti', 'Mūrti Rahasyam', 'mUrtirahasyam.itx')]]

    # --- Navarna vidhi: Sanskrit lines only, Hindi instructions dropped (we write our own) ---
    t = body_of('tantradurgA700.itx', '|| viniyogaH ||', '|| itinavArNajapavidhiH')
    def take(after, before):
        i = next(k for k, l in enumerate(t) if after in l) + 1
        j = next(k for k, l in enumerate(t) if k >= i and before in l)
        out = []
        for l in t[i:j]:
            l = re.sub(r'\s*\(.*?\)\s*', ' ', l).strip()      # hindi parentheticals
            l = re.sub(r'\s*\(.*$', '', l).strip()              # unclosed hindi parenthetical
            l = l.replace('rudraR^IShibhyo', 'rudraR^iShibhyo').replace('naiR^Ityai', 'nairR^ityai')
            l = l.replace('sarvA~Nge,', 'sarvA~Nge |')
            l = re.sub(r', isa mUlamantra.*$', ',', l)
            if re.search(r'\b(kA|ke|kI|kareM|kare|karake|haiM|hai|meM|se|aura|isa|isameM|nimnA)\b', l) and not l.startswith('OM'):
                continue
            if l and not l.startswith('||') and not l.endswith(' -') and l not in ('mahAkAlI -', 'mahAlakShmI -', 'mahAsarasvatI -'):
                out.append(clean(l))
        return out
    vin = '\n'.join(take('shrIgaNapatirjayati', 'pUrvokta'))
    dhy_lines = take('|| dhyAnaM ||', 'mAlA prArthanA')
    dhy, buf = [], []
    for l in dhy_lines:
        if l in ('mahAkAlI', 'mahAlakShmI', 'mahAsarasvatI'):
            continue
        buf.append(l)
        if re.search(r'\|\|\s*\d\s*\|\|$', l):
            dhy.append(re.sub(r'\s*\|\|\s*\d\s*\|\|$', ' ||', '\n'.join(buf))); buf = []
    mala = ['OM aiM hrIM akShamAlikAyai namaH |'] + [
        '\n'.join(take('mAlA prArthanA', 'isake pashchAta')[i:i + 2]) for i in (0, 2)] + [
        '\n'.join(take('isake pashchAta', 'isake bAda'))]
    navarna = ritual('navarna', 'Navārṇa Vidhi', [
        ('Viniyoga', [vin]),
        ('Ṛṣyādi Nyāsa', take('|| R^iShyAdinyAsaH ||', '|| karanyAsaH ||')),
        ('Kara Nyāsa', take('|| karanyAsaH ||', '|| hR^idayAdinyAsaH ||')),
        ('Hṛdayādi Nyāsa', take('|| hR^idayAdinyAsaH ||', '|| akSharanyAsaH ||')),
        ('Akṣara Nyāsa', take('|| akSharanyAsaH ||', 'evaM vinyasya')),
        ('Vyāpaka Nyāsa', ['OM aiM hrIM klIM chAmuNDAyai vichche |']),
        ('Dik Nyāsa', take('|| di~NnyAsaH ||', '|| dhyAnaM ||')),
        ('Dhyānam · Mahākālī', dhy[:1]), ('Dhyānam · Mahālakṣmī', dhy[1:2]), ('Dhyānam · Mahāsarasvatī', dhy[2:3]),
        ('Mālā Prārthanā', mala),
        ('Japa (108 times)', ['OM aiM hrIM klIM chAmuNDAyai vichche |']),
        ('Japa Samarpaṇam', ['guhyAtiguhyagoptrI tvaM gR^ihANAsmatkR^itaM japam |\nsiddhirbhavatu me devi tvatprasAdAn maheshvari ||']),
    ])

    # --- Saptashati nyasa (Gita Press form: verse + anga phrase, without the tantric bijas) ---
    u = body_of('tantradurgA700.itx', 'viniyogaH\\-', '|| R^iShyAdinyAsaH ||')
    sn_vin = '\n'.join(clean(l) for l in u[1:u.index(next(l for l in u if 'ise paDhakara' in l))])
    pairs = []
    vs = [l for l in u if not l.startswith('||') and 'ise paDhakara' not in l]
    k = 0
    blocks = []
    cur = []
    for l in vs[vs.index(next(l for l in vs if l.startswith('khaDganI'))):]:
        l = re.sub(r'\s*\((?:khaDginI|chApajyAniHsvanena|ghnaiM, ghreM)\)\s*', ' ', l).strip()
        l = l.replace('khaDganI', 'khaDginI')
        m = re.match(r'^OM aiM \S+ (.*)$', l)
        if m:  # bija + anga line -> keep anga phrase only
            blocks.append('\n'.join(cur).rstrip() + '\n' + m.group(1)); cur = []
        else:
            cur.append(clean(l))
    anga = [b for b in blocks]
    dh = body_of('tantradurgA700.itx', '|| dhyAnamantraH ||', 'artha \\-')[1:]
    nyasa = ritual('saptashati-nyasa', 'Saptaśatī Nyāsa & Dhyānam', [
        ('Viniyoga', [sn_vin]),
        ('Kara Nyāsa', anga),
        ('Hṛdayādi Nyāsa', [re.sub(r'a~NguShThAbhyAM namaH|tarjanIbhyAM namaH|madhyamAbhyAM namaH|anAmikAbhyAM namaH|kaniShThikAbhyAM namaH|karatalakarapR\^iShThAbhyAM namaH', r, a)
                            for a, r in zip(anga, ['hR^idayAya namaH', 'shirase svAhA', 'shikhAyai vaShaT', 'kavachAya hum', 'netratrayAya vauShaT', 'astrAya phaT'])]),
        ('Dhyānam', ['\n'.join(clean(l) for l in dh)]),
    ])

    tantric_ratri = {'id': 'ratri-tantric', 'title': 'Tantrokta Rātri Sūktam', 'kind': 'ref',
                     'ref': {'section': 'ch1', 'from': 70, 'to': 87}, 'preamble': [], 'verses': []}
    tantric_devi = {'id': 'devisuktam-tantric', 'title': 'Tantrokta Devī Sūktam', 'kind': 'ref',
                    'ref': {'section': 'ch5', 'from': 9, 'to': 82}, 'preamble': [], 'verses': []}

    order = [
        ('purvanga', 'Pūrvāṅga · before the paath', [core['dhyanam'] | {'title': 'Śrī Caṇḍikā Dhyānam'},
            core['kavacham'], core['argala'], core['kilakam'], ratri_v, tantric_ratri, athar, navarna, nyasa]),
        ('prathama', 'Prathama Caritra · Mahākālī', [core['ch1']]),
        ('madhyama', 'Madhyama Caritra · Mahālakṣmī', [core[f'ch{i}'] for i in (2, 3, 4)]),
        ('uttara', 'Uttama Caritra · Mahāsarasvatī', [core[f'ch{i}'] for i in range(5, 14)]),
        ('uttaranga', 'Uttarāṅga · after the paath', [
            {'id': 'navarna-after', 'title': 'Navārṇa Vidhi (again)', 'kind': 'ref',
             'ref': {'section': 'navarna'}, 'preamble': [], 'verses': []},
            core['devisuktam'] | {'title': 'Ṛgvedokta Devī Sūktam'}, tantric_devi, *rah,
            core['kshamapana']]),
        ('extras', 'Also recited', [kunj]),
    ]
    out = {'groups': [{'id': g, 'title': t, 'sections': [s['id'] for s in ss]} for g, t, ss in order],
           'sections': {s['id']: s for _, _, ss in order for s in ss}}
    json.dump(out, open(DATA, 'w', encoding='utf-8'), ensure_ascii=False)
    for g, t, ss in order:
        print(t)
        for s in ss:
            print(f"   {s['id']:20} {s['title']:34} entries={len(s['verses'])}")


if __name__ == '__main__':
    main()
