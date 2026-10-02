"""Generate notes for the ritual sections: navarna.json and saptashati-nyasa.json.

Nyāsa lines follow a few fixed patterns (mantra + 'namaḥ' + a body part / finger / direction),
so their word glosses and instructions are built from the tables below. Viniyoga, dhyāna and
prayer verses are written by hand further down.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))

BIJA = {
    'oṃ': ('Om', 'ఓం'),
    'aiṃ': ('bīja aiṃ (Mahāsarasvatī)', 'ఐం బీజం (మహాసరస్వతి)'),
    'hrīṃ': ('bīja hrīṃ (Mahālakṣmī)', 'హ్రీం బీజం (మహాలక్ష్మి)'),
    'klīṃ': ('bīja klīṃ (Mahākālī)', 'క్లీం బీజం (మహాకాళి)'),
    'cāmuṇḍāyai': ('to Cāmuṇḍā', 'చాముండకు'),
    'vicce': ('vicce (bīja)', 'విచ్చే (బీజం)'),
    'namaḥ': ('salutation', 'నమస్కారం'),
}
# (place word, English gloss, Telugu gloss, English instruction, Telugu instruction)
PLACES = {
    'śirasi': ('on the head', 'శిరస్సుపై', 'touch the top of the head', 'శిరస్సును తాకండి'),
    'mukhe': ('on the mouth', 'ముఖంపై', 'touch the mouth', 'ముఖాన్ని (నోటిని) తాకండి'),
    'hṛdi': ('on the heart', 'హృదయంపై', 'touch the heart', 'హృదయాన్ని తాకండి'),
    'guhye': ('on the private parts', 'గుహ్యంపై', 'touch the lower body (traditionally done mentally or by gesture)', 'క్రింది శరీర భాగాన్ని తాకండి (సంప్రదాయంగా మనసులో లేదా సంజ్ఞతో)'),
    'pādayoḥ': ('on the feet', 'పాదాలపై', 'touch both feet', 'రెండు పాదాలను తాకండి'),
    'nābhau': ('on the navel', 'నాభిపై', 'touch the navel', 'నాభిని తాకండి'),
    'sarvāṅge': ('over the whole body', 'సర్వాంగాలపై', 'pass both hands over the whole body', 'రెండు చేతులతో శరీరమంతా తాకండి'),
    'śikhāyām': ('on the crown tuft', 'శిఖపై', 'touch the crown of the head', 'శిఖను (తల పైభాగాన్ని) తాకండి'),
    'dakṣiṇanetre': ('on the right eye', 'కుడి కంటిపై', 'touch the right eye', 'కుడి కంటిని తాకండి'),
    'vāmanetre': ('on the left eye', 'ఎడమ కంటిపై', 'touch the left eye', 'ఎడమ కంటిని తాకండి'),
    'dakṣiṇakarṇe': ('on the right ear', 'కుడి చెవిపై', 'touch the right ear', 'కుడి చెవిని తాకండి'),
    'vāmakarṇe': ('on the left ear', 'ఎడమ చెవిపై', 'touch the left ear', 'ఎడమ చెవిని తాకండి'),
    'dakṣiṇanāsāpuṭe': ('on the right nostril', 'కుడి నాసికపై', 'touch the right nostril', 'కుడి నాసికను తాకండి'),
    'vāmanāsāpuṭe': ('on the left nostril', 'ఎడమ నాసికపై', 'touch the left nostril', 'ఎడమ నాసికను తాకండి'),
}
FINGERS = {
    'aṅguṣṭhābhyāṃ': ('to the two thumbs', 'రెండు బొటనవేళ్ళకు', 'run both index fingers along both thumbs', 'రెండు చూపుడువేళ్ళతో రెండు బొటనవేళ్ళను తాకండి'),
    'tarjanībhyāṃ': ('to the two index fingers', 'రెండు చూపుడువేళ్ళకు', 'run both thumbs along both index fingers', 'రెండు బొటనవేళ్ళతో రెండు చూపుడువేళ్ళను తాకండి'),
    'madhyamābhyāṃ': ('to the two middle fingers', 'రెండు మధ్యవేళ్ళకు', 'run both thumbs along both middle fingers', 'రెండు బొటనవేళ్ళతో రెండు మధ్యవేళ్ళను తాకండి'),
    'anāmikābhyāṃ': ('to the two ring fingers', 'రెండు ఉంగరపువేళ్ళకు', 'run both thumbs along both ring fingers', 'రెండు బొటనవేళ్ళతో రెండు ఉంగరపువేళ్ళను తాకండి'),
    'kaniṣṭhikābhyāṃ': ('to the two little fingers', 'రెండు చిటికెనవేళ్ళకు', 'run both thumbs along both little fingers', 'రెండు బొటనవేళ్ళతో రెండు చిటికెనవేళ్ళను తాకండి'),
    'karatala': ('palms', 'అరచేతులు', 'touch the palms and backs of both hands, each with the other', 'ఒక చేతితో మరొక చేతి అరచేతిని, వెనుక భాగాన్ని తాకండి'),
}
ANGA = {
    'hṛdayāya': ('to the heart', 'హృదయానికి', 'namaḥ', 'touch the heart with the right hand\'s middle three fingers', 'కుడి చేతి మధ్య మూడు వేళ్ళతో హృదయాన్ని తాకండి'),
    'śirase': ('to the head', 'శిరస్సుకు', 'svāhā', 'touch the head', 'శిరస్సును తాకండి'),
    'śikhāyai': ('to the crown tuft', 'శిఖకు', 'vaṣaṭ', 'touch the crown of the head with the thumb', 'బొటనవేలితో శిఖను తాకండి'),
    'kavacāya': ('to the armour', 'కవచానికి', 'hum', 'cross the arms and touch the opposite shoulders', 'చేతులను అడ్డంగా పెట్టి ఎదురు భుజాలను తాకండి'),
    'netratrayāya': ('to the three eyes', 'మూడు నేత్రాలకు', 'vauṣaṭ', 'touch both eyes and the brow centre with three fingers', 'మూడు వేళ్ళతో రెండు కన్నులను, భ్రూమధ్యాన్ని తాకండి'),
    'astrāya': ('to the weapon', 'అస్త్రానికి', 'phaṭ', 'pass the right hand around the head and clap into the left palm', 'కుడి చేతిని తల చుట్టూ తిప్పి ఎడమ అరచేతిలో చప్పట్లు కొట్టండి'),
}
ANGA_WORD = {'namaḥ': ('salutation', 'నమస్కారం'), 'svāhā': ('svāhā', 'స్వాహా'), 'vaṣaṭ': ('vaṣaṭ', 'వషట్'),
             'hum': ('hum', 'హుం'), 'vauṣaṭ': ('vauṣaṭ', 'వౌషట్'), 'phaṭ': ('phaṭ', 'ఫట్')}
DIRS = {
    'prācyai': ('east', 'తూర్పు'), 'āgneyyai': ('south-east', 'ఆగ్నేయ దిక్కు'), 'dakṣiṇāyai': ('south', 'దక్షిణ దిక్కు'),
    'nairṛtyai': ('south-west', 'నైరృతి దిక్కు'), 'pratīcyai': ('west', 'పడమర'), 'vāyavyai': ('north-west', 'వాయవ్య దిక్కు'),
    'udīcyai': ('north', 'ఉత్తర దిక్కు'), 'aiśānyai': ('north-east', 'ఈశాన్య దిక్కు'), 'ūrdhvāyai': ('sky above', 'పైన ఆకాశం'),
    'bhūmyai': ('earth below', 'క్రింద భూమి'),
}
AKSHARA = {'cāṃ': 'cā', 'muṃ': 'muṇ', 'ḍāṃ': 'ḍā', 'yaiṃ': 'yai', 'viṃ': 'vi', 'cceṃ': 'cce'}


def words(line):
    return [w.strip(',|') for w in line.replace('\n', ' ').split() if w.strip(',|')]


def mantra_pada(ws):
    out = []
    for w in ws:
        if w in BIJA:
            out.append([w, *BIJA[w]])
        elif w in AKSHARA:
            out.append([w, f"syllable '{AKSHARA[w]}' of the mantra", f"మంత్రంలోని '{AKSHARA[w]}' అక్షరం"])
    return out


def nyasa_note(group, iast):
    ws = words(iast)
    pada = mantra_pada(ws)
    if group == 'Ṛṣyādi Nyāsa' or group == 'Akṣara Nyāsa':
        place = ws[-1]
        if place in PLACES:
            g_en, g_te, do_en, do_te = PLACES[place]
            pada.append([place, g_en, g_te])
            label = {'Ṛṣyādi Nyāsa': ('', '')}.get(group)
            return pada, place, do_en, do_te
    if group == 'Kara Nyāsa':
        for f, (g_en, g_te, do_en, do_te) in FINGERS.items():
            if any(w.startswith(f) for w in ws):
                if f == 'karatala':
                    pada += [['karatala', 'palms', 'అరచేతులు'], ['karapṛṣṭhābhyāṃ', 'and backs of the hands', 'చేతుల వెనుక భాగాలకు']]
                else:
                    pada.append([f, g_en, g_te])
                return pada, f, do_en, do_te
    if group == 'Hṛdayādi Nyāsa':
        for a, (g_en, g_te, w2, do_en, do_te) in ANGA.items():
            if a in ws:
                pada += [[a, g_en, g_te], [w2, *ANGA_WORD[w2]]]
                return pada, a, do_en, do_te
    if group == 'Dik Nyāsa':
        for d_, (en, te) in DIRS.items():
            if d_ in ws:
                pada.append([d_, f'to the {en}', f'{te} వైపుకు'])
                return pada, d_, f'snap the fingers or bow toward the {en}', f'{te} వైపు చిటికె వేయండి లేదా నమస్కరించండి'
    return pada, None, None, None


def build_navarna(sec):
    out = {"_intro": {
        "en": "The Navārṇa Vidhi prepares the reader with the nine-syllable mantra 'aiṃ hrīṃ klīṃ cāmuṇḍāyai vicce' before and after the 13 chapters. Nyāsa means 'placing': each part of the mantra is placed on a part of the body, fingers or directions with a touch, so that body and mind become fit for the recitation. Then come the dhyānas of the three Goddesses, the prayer to the rosary, 108 repetitions of the mantra, and offering the japa to the Devī. The instructions below each line say what to touch.",
        "te": "నవార్ణ విధి 13 అధ్యాయాలకు ముందు, తరువాత 'ఐం హ్రీం క్లీం చాముండాయై విచ్చే' అనే నవాక్షర మంత్రంతో పాఠకుని సిద్ధం చేస్తుంది. న్యాసం అంటే 'ఉంచడం': మంత్రంలోని ప్రతి భాగాన్ని తాకుతూ శరీర భాగాలపై, వేళ్ళపై, దిక్కులపై ఉంచుతారు; దానివల్ల శరీరం, మనస్సు పారాయణకు యోగ్యమవుతాయి. తరువాత ముగ్గురు దేవీల ధ్యానాలు, మాలా ప్రార్థన, మంత్రాన్ని 108 సార్లు జపం, జపాన్ని దేవికి సమర్పించడం. ప్రతి పంక్తి క్రింద ఏమి తాకాలో సూచించాము."
    }}
    for v in sec['verses']:
        ref, g, iast = v['ref'], v.get('group'), v['iast']
        pada, key, do_en, do_te = nyasa_note(g, iast)
        if key:
            out[ref] = {"pada": pada,
                        "en": f"{g}: recite the line and {do_en}.",
                        "te": f"{ {'Ṛṣyādi Nyāsa':'ఋష్యాది న్యాసం','Kara Nyāsa':'కర న్యాసం','Hṛdayādi Nyāsa':'హృదయాది న్యాసం','Akṣara Nyāsa':'అక్షర న్యాసం','Dik Nyāsa':'దిఙ్న్యాసం'}[g] }: పంక్తిని పఠిస్తూ {do_te}."}
    out.update(HAND_NAVARNA)
    # first entry of each group gets a context note
    firsts = {}
    for v in sec['verses']:
        firsts.setdefault(v.get('group'), v['ref'])
    for g, ref in firsts.items():
        if g in GROUP_CTX and ref in out:
            out[ref]['ctx'] = GROUP_CTX[g]
    return out


GROUP_CTX = {
    'Ṛṣyādi Nyāsa': {"en": "Ṛṣyādi Nyāsa places the mantra's seer, metre, deity, seed, power and pin on the body: head, mouth, heart, lower body, feet, navel, then the whole mantra over the whole body.",
                     "te": "ఋష్యాది న్యాసం మంత్రపు ఋషి, ఛందస్సు, దేవత, బీజం, శక్తి, కీలకాలను శరీరంపై ఉంచుతుంది: శిరస్సు, ముఖం, హృదయం, క్రింది భాగం, పాదాలు, నాభి, తరువాత సంపూర్ణ మంత్రాన్ని శరీరమంతా."},
    'Kara Nyāsa': {"en": "Kara Nyāsa places the parts of the mantra on the fingers, from thumbs to little fingers, then the whole mantra on palms and backs of the hands.",
                   "te": "కర న్యాసం మంత్ర భాగాలను బొటనవేలు నుండి చిటికెనవేలు వరకు వేళ్ళపై, తరువాత సంపూర్ణ మంత్రాన్ని అరచేతులు, చేతుల వెనుక భాగాలపై ఉంచుతుంది."},
    'Hṛdayādi Nyāsa': {"en": "Hṛdayādi (or Ṣaḍaṅga) Nyāsa places the mantra on six 'limbs': heart, head, crown, armour, eyes and weapon, each with its own closing word.",
                       "te": "హృదయాది (షడంగ) న్యాసం మంత్రాన్ని ఆరు 'అంగాల'పై ఉంచుతుంది: హృదయం, శిరస్సు, శిఖ, కవచం, నేత్రాలు, అస్త్రం; ప్రతిదానికి దాని స్వంత ముగింపు పదం."},
    'Akṣara Nyāsa': {"en": "Akṣara Nyāsa places each of the nine syllables (ai, hrī, klī, cā, muṇ, ḍā, yai, vi, cce) on a point of the head and body.",
                     "te": "అక్షర న్యాసం తొమ్మిది అక్షరాలను (ఐ, హ్రీ, క్లీ, చా, ముం, డా, యై, వి, చ్చే) తల, శరీరంలోని ఒక్కొక్క స్థానంపై ఉంచుతుంది."},
    'Dik Nyāsa': {"en": "Dik Nyāsa places the mantra in the ten directions, starting from the east and going clockwise, then above and below, as a protective enclosure.",
                  "te": "దిఙ్న్యాసం మంత్రాన్ని తూర్పు నుండి ప్రదక్షిణంగా పది దిక్కులలో, తరువాత పైన, క్రింద ఉంచుతుంది; ఇది రక్షావలయం."},
}

HAND_NAVARNA = {
 "1": {"pada": [["oṃ","Om","ఓం"],["navārṇa","nine-syllabled","నవార్ణ"],["mantrasya","of the mantra","మంత్రానికి"],["brahma","Brahmā","బ్రహ్మ"],["viṣṇu","Viṣṇu","విష్ణు"],["rudrāḥ","and Rudra","రుద్రులు"],["ṛṣayaḥ","are the seers","ఋషులు"],["gāyatrī","gāyatrī","గాయత్రి"],["uṣṇik","uṣṇik","ఉష్ణిక్"],["anuṣṭubhaḥ","anuṣṭubh","అనుష్టుప్"],["chandāṃsi","are the metres","ఛందస్సులు"],["devatāḥ","are the deities","దేవతలు"],["aiṃ","aiṃ","ఐం"],["bījam","is the seed","బీజం"],["hrīṃ","hrīṃ","హ్రీం"],["śaktiḥ","is the power","శక్తి"],["klīṃ","klīṃ","క్లీం"],["kīlakam","is the pin","కీలకం"],["prītyarthe","for the pleasure of","ప్రీతి కోసం"],["jape","in recitation","జపంలో"],["viniyogaḥ","is the application","వినియోగం"]],
       "en": "Of the nine-syllable mantra, Brahmā, Viṣṇu and Rudra are the seers; gāyatrī, uṣṇik and anuṣṭubh the metres; Śrī Mahākālī, Mahālakṣmī and Mahāsarasvatī the deities; aiṃ the seed, hrīṃ the power, klīṃ the pin. It is applied in japa for the pleasure of Mahākālī, Mahālakṣmī and Mahāsarasvatī.",
       "te": "నవార్ణ మంత్రానికి బ్రహ్మ, విష్ణు, రుద్రులు ఋషులు; గాయత్రి, ఉష్ణిక్, అనుష్టుప్ ఛందస్సులు; శ్రీ మహాకాళి, మహాలక్ష్మి, మహాసరస్వతులు దేవతలు; ఐం బీజం, హ్రీం శక్తి, క్లీం కీలకం. మహాకాళీ మహాలక్ష్మీ మహాసరస్వతుల ప్రీతి కోసం జపంలో వినియోగం.",
       "ctx": {"en": "Take a little water in the right palm while reciting the viniyoga and let it fall at the end.", "te": "వినియోగం పఠిస్తూ కుడి అరచేతిలో కొద్దిగా నీరు తీసుకొని చివర వదలండి."}},
 "8": {"pada": [["oṃ","Om","ఓం"],["aiṃ","aiṃ","ఐం"],["hrīṃ","hrīṃ","హ్రీం"],["klīṃ","klīṃ","క్లీం"],["cāmuṇḍāyai","to Cāmuṇḍā","చాముండకు"],["vicce","vicce","విచ్చే"],["sarvāṅge","over the whole body","సర్వాంగాలపై"]],
       "en": "Ṛṣyādi Nyāsa: recite the full mantra and pass both hands over the whole body. Then wash or purify the hands with the mantra before Kara Nyāsa.",
       "te": "ఋష్యాది న్యాసం: సంపూర్ణ మంత్రాన్ని పఠిస్తూ రెండు చేతులతో శరీరమంతా తాకండి. తరువాత కర న్యాసానికి ముందు మంత్రంతో చేతులను శుద్ధి చేసుకోండి."},
 "2": {"pada": [["brahma","Brahmā","బ్రహ్మ"],["viṣṇu","Viṣṇu","విష్ణు"],["rudra","Rudra","రుద్ర"],["ṛṣibhyaḥ","to the seers","ఋషులకు"],["namaḥ","salutation","నమస్కారం"],["śirasi","on the head","శిరస్సుపై"]],
       "en": "Ṛṣyādi Nyāsa: 'Salutation to the seers Brahmā, Viṣṇu and Rudra.' Touch the top of the head.",
       "te": "ఋష్యాది న్యాసం: 'బ్రహ్మ విష్ణు రుద్ర ఋషులకు నమస్కారం.' శిరస్సును తాకండి."},
 "3": {"pada": [["gāyatrī","gāyatrī","గాయత్రి"],["uṣṇik","uṣṇik","ఉష్ణిక్"],["anuṣṭup","anuṣṭubh","అనుష్టుప్"],["chandobhyaḥ","to the metres","ఛందస్సులకు"],["namaḥ","salutation","నమస్కారం"],["mukhe","on the mouth","ముఖంపై"]],
       "en": "Ṛṣyādi Nyāsa: 'Salutation to the metres gāyatrī, uṣṇik and anuṣṭubh.' Touch the mouth.",
       "te": "ఋష్యాది న్యాసం: 'గాయత్రీ ఉష్ణిక్ అనుష్టుప్ ఛందస్సులకు నమస్కారం.' ముఖాన్ని తాకండి."},
 "4": {"pada": [["mahākālī","Mahākālī","మహాకాళి"],["mahālakṣmī","Mahālakṣmī","మహాలక్ష్మి"],["mahāsarasvatī","Mahāsarasvatī","మహాసరస్వతి"],["devatābhyaḥ","to the deities","దేవతలకు"],["namaḥ","salutation","నమస్కారం"],["hṛdi","on the heart","హృదయంపై"]],
       "en": "Ṛṣyādi Nyāsa: 'Salutation to the deities Mahākālī, Mahālakṣmī and Mahāsarasvatī.' Touch the heart.",
       "te": "ఋష్యాది న్యాసం: 'మహాకాళీ మహాలక్ష్మీ మహాసరస్వతీ దేవతలకు నమస్కారం.' హృదయాన్ని తాకండి."},
 "5": {"pada": [["aiṃ","aiṃ","ఐం"],["bījāya","to the seed","బీజానికి"],["namaḥ","salutation","నమస్కారం"],["guhye","on the private parts","గుహ్యంపై"]],
       "en": "Ṛṣyādi Nyāsa: 'Salutation to the seed aiṃ.' Touch the lower body (traditionally done mentally or by gesture).",
       "te": "ఋష్యాది న్యాసం: 'ఐం బీజానికి నమస్కారం.' క్రింది శరీర భాగాన్ని తాకండి (సంప్రదాయంగా మనసులో లేదా సంజ్ఞతో)."},
 "6": {"pada": [["hrīṃ","hrīṃ","హ్రీం"],["śaktaye","to the power","శక్తికి"],["namaḥ","salutation","నమస్కారం"],["pādayoḥ","on the feet","పాదాలపై"]],
       "en": "Ṛṣyādi Nyāsa: 'Salutation to the power hrīṃ.' Touch both feet.",
       "te": "ఋష్యాది న్యాసం: 'హ్రీం శక్తికి నమస్కారం.' రెండు పాదాలను తాకండి."},
 "7": {"pada": [["klīṃ","klīṃ","క్లీం"],["kīlakāya","to the pin","కీలకానికి"],["namaḥ","salutation","నమస్కారం"],["nābhau","on the navel","నాభిపై"]],
       "en": "Ṛṣyādi Nyāsa: 'Salutation to the pin klīṃ.' Touch the navel.",
       "te": "ఋష్యాది న్యాసం: 'క్లీం కీలకానికి నమస్కారం.' నాభిని తాకండి."},
 "30": {"pada": [["oṃ","Om","ఓం"],["aiṃ","aiṃ","ఐం"],["hrīṃ","hrīṃ","హ్రీం"],["klīṃ","klīṃ","క్లీం"],["cāmuṇḍāyai","to Cāmuṇḍā","చాముండకు"],["vicce","vicce","విచ్చే"]],
        "en": "Vyāpaka Nyāsa ('pervading'): recite the full mantra while passing both hands over the body from head to foot and back up.",
        "te": "వ్యాపక న్యాసం ('వ్యాపించే'): సంపూర్ణ మంత్రాన్ని పఠిస్తూ రెండు చేతులతో శిరస్సు నుండి పాదాల వరకు, తిరిగి పైకి శరీరమంతా తాకండి."},
 "41": {"pada": [["khaḍgam","sword","ఖడ్గం"],["cakra","discus","చక్రం"],["gadā","mace","గద"],["iṣu","arrows","బాణాలు"],["cāpa","bow","ధనుస్సు"],["parighān","iron club","పరిఘ"],["śūlam","trident","శూలం"],["bhuśuṇḍīm","sling","భుశుండి"],["śiraḥ","head","శిరస్సు"],["śaṅkham","conch","శంఖం"],["sandadhatīm","holding","ధరించినదానిని"],["karaiḥ","in her hands","చేతులలో"],["trinayanām","three-eyed","త్రినేత్రను"],["sarvāṅga","all limbs","సర్వాంగ"],["bhūṣā","ornaments","ఆభరణాలతో"],["āvṛtām","covered with","కూడినదానిని"],["nīlāśma","sapphire","నీలమణి"],["dyutim","lustre","కాంతి గలదానిని"],["āsya","faces","ముఖాలు"],["pāda","feet","పాదాలు"],["daśakām","ten each","పది చొప్పున గలదానిని"],["seve","I serve","సేవిస్తాను"],["mahākālikām","Mahākālī","మహాకాళిని"],["yām","whom","ఎవరిని"],["astaut","praised","స్తుతించాడో"],["svapite","when asleep","నిద్రిస్తుండగా"],["harau","Hari","హరి"],["kamalajaḥ","the lotus-born (Brahmā)","కమలజుడు (బ్రహ్మ)"],["hantum","to slay","సంహరించడానికి"],["madhum","Madhu","మధుని"],["kaiṭabham","Kaiṭabha","కైటభుని"]],
        "en": "I serve Mahākālī, who holds in her hands sword, discus, mace, arrows, bow, iron club, trident, sling, a severed head and conch; three-eyed, adorned on every limb, with the lustre of sapphire and ten faces and ten feet; whom lotus-born Brahmā praised, while Hari slept, to have Madhu and Kaiṭabha slain.",
        "te": "చేతులలో ఖడ్గం, చక్రం, గద, బాణాలు, ధనుస్సు, పరిఘ, శూలం, భుశుండి, శిరస్సు, శంఖం ధరించిన, త్రినేత్ర, సర్వాంగ భూషణాలు గల, నీలమణి కాంతి గల, పది ముఖాలు, పది పాదాలు గల మహాకాళిని సేవిస్తాను; హరి నిద్రిస్తుండగా మధుకైటభుల సంహారం కోసం కమలజుడు స్తుతించినది ఆమెనే.",
        "ctx": {"en": "The same dhyāna as the opening of Chapter 1.", "te": "1వ అధ్యాయ ప్రారంభ ధ్యానమే ఇది."}},
 "42": {"pada": [["akṣasrak","rosary","అక్షమాల"],["paraśum","axe","పరశువు"],["gadā","mace","గద"],["iṣu","arrow","బాణం"],["kuliśam","thunderbolt","వజ్రం"],["padmam","lotus","పద్మం"],["dhanuḥ","bow","ధనుస్సు"],["kuṇḍikām","water-pot","కుండిక"],["daṇḍam","staff","దండం"],["śaktim","spear","శక్తి"],["asim","sword","ఖడ్గం"],["carma","shield","డాలు"],["jalajam","conch","శంఖం"],["ghaṇṭām","bell","ఘంట"],["surābhājanam","wine-cup","సురాపాత్ర"],["śūlam","trident","శూలం"],["pāśa","noose","పాశం"],["sudarśane","and discus","సుదర్శనాలను"],["dadhatīm","holding","ధరించినదానిని"],["hastaiḥ","in her hands","చేతులలో"],["prasanna","gracious","ప్రసన్న"],["ānanām","face","ముఖం గలదానిని"],["seve","I serve","సేవిస్తాను"],["sairibha","the buffalo","మహిషుని"],["mardinīm","slayer of","మర్దినిని"],["mahālakṣmīm","Mahālakṣmī","మహాలక్ష్మిని"],["saroja","lotus","పద్మంపై"],["sthitām","seated on","ఉన్నదానిని"]],
        "en": "I serve Mahālakṣmī, slayer of the buffalo, seated on a lotus, gracious of face, holding in her hands rosary, axe, mace, arrow, thunderbolt, lotus, bow, water-pot, staff, spear, sword, shield, conch, bell, wine-cup, trident, noose and the discus Sudarśana.",
        "te": "చేతులలో అక్షమాల, పరశువు, గద, బాణం, వజ్రం, పద్మం, ధనుస్సు, కుండిక, దండం, శక్తి, ఖడ్గం, డాలు, శంఖం, ఘంట, సురాపాత్ర, శూలం, పాశం, సుదర్శన చక్రం ధరించిన, ప్రసన్న ముఖం గల, పద్మంపై ఉన్న మహిషమర్దిని మహాలక్ష్మిని సేవిస్తాను.",
        "ctx": {"en": "The same dhyāna as the opening of Chapter 2.", "te": "2వ అధ్యాయ ప్రారంభ ధ్యానమే ఇది."}},
 "43": {"pada": [["ghaṇṭā","bell","ఘంట"],["śūla","trident","శూలం"],["halāni","plough","నాగలి"],["śaṅkha","conch","శంఖం"],["musale","pestle","ముసలం"],["cakram","discus","చక్రం"],["dhanuḥ","bow","ధనుస్సు"],["sāyakam","arrow","బాణం"],["hastābjaiḥ","in her lotus hands","కరకమలాలలో"],["dadhatīm","holding","ధరించినదానిని"],["ghanānta","the clouds' edge","మేఘాంతంలో"],["vilasat","shining","ప్రకాశించే"],["śītāṃśu","moon","చంద్రుని"],["tulya","equal to","సమానమైన"],["prabhām","radiance","ప్రభ గలదానిని"],["gaurī","Gaurī's","గౌరి"],["deha","body","దేహం నుండి"],["samudbhavām","born from","పుట్టినదానిని"],["trijagatām","of the three worlds","ముల్లోకాలకు"],["ādhārabhūtām","the support","ఆధారభూతను"],["mahāpūrvām","'Mahā'-prefixed","మహా అనే పూర్వపదం గల"],["sarasvatīm","Sarasvatī","సరస్వతిని"],["anubhaje","I worship","భజిస్తాను"],["śumbha","Śumbha","శుంభ"],["ādi","and other","మొదలైన"],["daitya","daityas","దైత్యులను"],["ardinīm","tormentor of","మర్దించినదానిని"]],
        "en": "Here I worship Mahāsarasvatī, who holds in her lotus hands bell, trident, plough, conch, pestle, discus, bow and arrow; radiant as the moon shining at the edge of the clouds; born from Gaurī's body; support of the three worlds; destroyer of Śumbha and the other daityas.",
        "te": "కరకమలాలలో ఘంట, శూలం, నాగలి, శంఖం, ముసలం, చక్రం, ధనుస్సు, బాణం ధరించిన, మేఘాంతంలో ప్రకాశించే చంద్రుని వంటి ప్రభ గల, గౌరి దేహం నుండి పుట్టిన, ముల్లోకాలకు ఆధారభూత, శుంభాది దైత్యులను మర్దించిన మహాసరస్వతిని ఇక్కడ భజిస్తాను.",
        "ctx": {"en": "The same dhyāna as the opening of Chapter 5.", "te": "5వ అధ్యాయ ప్రారంభ ధ్యానమే ఇది."}},
 "44": {"pada": [["oṃ","Om","ఓం"],["aiṃ","aiṃ","ఐం"],["hrīṃ","hrīṃ","హ్రీం"],["akṣamālikāyai","to the rosary","అక్షమాలికకు"],["namaḥ","salutation","నమస్కారం"]],
        "en": "'Oṃ aiṃ hrīṃ, salutation to the rosary.' Worship the japa-mālā with this mantra.",
        "te": "'ఓం ఐం హ్రీం అక్షమాలికకు నమస్కారం.' ఈ మంత్రంతో జపమాలను పూజించండి.",
        "ctx": {"en": "Mālā Prārthanā: before japa, the rosary itself is honoured and asked for success.", "te": "మాలా ప్రార్థన: జపానికి ముందు జపమాలను పూజించి సిద్ధిని ప్రార్థిస్తారు."}},
 "45": {"pada": [["oṃ","Om","ఓం"],["māṃ","māṃ (bīja)","మాం (బీజం)"],["māle","O rosary","ఓ మాలా"],["mahāmāye","O great māyā","ఓ మహామాయా"],["sarvaśakti","all power","సర్వశక్తి"],["svarūpiṇi","whose form is","స్వరూపిణీ"],["caturvargaḥ","the four aims of life","చతుర్వర్గం"],["tvayi","in you","నీలో"],["nyastaḥ","is placed","ఉంచబడింది"],["tasmāt","therefore","కాబట్టి"],["me","to me","నాకు"],["siddhidā","giver of success","సిద్ధిదాయిని"],["bhava","be","అగుము"]],
        "en": "'O rosary, O great māyā, whose form is all power: the four aims of life are placed in you. So be the giver of success to me.'",
        "te": "'ఓ మాలా, మహామాయా, సర్వశక్తి స్వరూపిణీ, చతుర్వర్గం నీలో ఉంచబడింది. కాబట్టి నాకు సిద్ధిదాయినివి కమ్ము.'",
        "ctx": {"en": "The four aims (caturvarga) are dharma, artha, kāma and mokṣa.", "te": "చతుర్వర్గం: ధర్మ, అర్థ, కామ, మోక్షాలు."}},
 "46": {"pada": [["oṃ","Om","ఓం"],["avighnam","without obstacles","విఘ్నం లేకుండా"],["kuru","make it","చేయి"],["māle","O rosary","ఓ మాలా"],["tvam","you","నిన్ను"],["gṛhṇāmi","I take","గ్రహిస్తున్నాను"],["dakṣiṇe","right","కుడి"],["kare","in hand","చేతిలో"],["japakāle","at the time of japa","జపకాలంలో"],["ca","and","మరియు"],["siddhyartham","for success","సిద్ధి కోసం"],["prasīda","be gracious","ప్రసన్నురాలవు కమ్ము"],["mama","my","నా"],["siddhaye","for success","సిద్ధి కోసం"]],
        "en": "'Make it free of obstacles, O rosary; I take you in my right hand. At the time of japa, be gracious for my success.'",
        "te": "'ఓ మాలా, విఘ్నం లేకుండా చేయి; నిన్ను కుడి చేతిలో గ్రహిస్తున్నాను. జపకాలంలో నా సిద్ధి కోసం ప్రసన్నురాలవు కమ్ము.'",
        "ctx": {"en": "The source writes 'dakṣiṇeḥkare'; corrected to dakṣiṇe kare ('in the right hand').", "te": "మూలంలో 'దక్షిణేఃకరే' అని ఉంది; 'దక్షిణే కరే' (కుడి చేతిలో) అని సరిచేశాము."}},
 "47": {"pada": [["oṃ","Om","ఓం"],["akṣamālā","rosary","అక్షమాల"],["adhipataye","to the presiding power of","అధిపతికి"],["susiddhim","full success","సుసిద్ధిని"],["dehi","give","ఇవ్వు"],["sarvamantra","all mantras","సర్వమంత్ర"],["artha","aims","అర్థ"],["sādhini","fulfiller of","సాధినీ"],["sādhaya","accomplish","సాధించు"],["sarvasiddhim","all success","సర్వసిద్ధిని"],["parikalpaya","arrange","కల్పించు"],["me","for me","నాకు"],["svāhā","svāhā","స్వాహా"]],
        "en": "'Oṃ, to the presiding power of the rosary: give full success, give it, O fulfiller of the aims of all mantras; accomplish, accomplish; arrange all success for me, arrange it. Svāhā.'",
        "te": "'ఓం అక్షమాలాధిపతికి: సుసిద్ధిని ఇవ్వు, ఇవ్వు; సర్వమంత్రార్థ సాధినీ, సాధించు, సాధించు; నాకు సర్వసిద్ధిని కల్పించు, కల్పించు. స్వాహా.'"},
 "48": {"pada": [["oṃ","Om","ఓం"],["aiṃ","aiṃ","ఐం"],["hrīṃ","hrīṃ","హ్రీం"],["klīṃ","klīṃ","క్లీం"],["cāmuṇḍāyai","to Cāmuṇḍā","చాముండకు"],["vicce","vicce","విచ్చే"]],
        "en": "The Navārṇa mantra. Recite it 108 times on the rosary.",
        "te": "నవార్ణ మంత్రం. జపమాలపై 108 సార్లు జపించండి.",
        "ctx": {"en": "aiṃ is the bīja of Mahāsarasvatī, hrīṃ of Mahālakṣmī, klīṃ of Mahākālī; Cāmuṇḍā is the Devī who unites them; 'vicce' is explained in the Kuñjikā (9) as the giver of fearlessness.", "te": "ఐం మహాసరస్వతి బీజం, హ్రీం మహాలక్ష్మి బీజం, క్లీం మహాకాళి బీజం; చాముండ వారిని ఏకం చేసే దేవి; 'విచ్చే' అభయప్రదాయిని అని కుంజిక (9) వివరిస్తుంది."}},
 "49": {"pada": [["guhya","secret","గుహ్యం"],["atiguhya","most secret","అతిగుహ్యం"],["goptrī","guardian of","రక్షించేదానివి"],["tvam","you","నీవు"],["gṛhāṇa","accept","స్వీకరించు"],["asmat","by us","మా చేత"],["kṛtam","done","చేసిన"],["japam","japa","జపాన్ని"],["siddhiḥ","success","సిద్ధి"],["bhavatu","may there be","కలుగుగాక"],["me","for me","నాకు"],["devi","O Goddess","ఓ దేవీ"],["tvat","your","నీ"],["prasādāt","by grace","ప్రసాదంతో"],["maheśvari","O great Goddess","ఓ మహేశ్వరీ"]],
        "en": "'You are the guardian of what is secret and most secret: accept the japa we have done. By your grace, O great Goddess, may I have success.'",
        "te": "'గుహ్యాతిగుహ్యాలను రక్షించేదానివి నీవు; మేము చేసిన జపాన్ని స్వీకరించు. ఓ మహేశ్వరీ, నీ ప్రసాదంతో నాకు సిద్ధి కలుగుగాక.'",
        "ctx": {"en": "Offer the japa with a little water into the Devī's left hand (or onto the ground before her) while reciting this.", "te": "దీనిని పఠిస్తూ కొద్దిగా నీటితో జపాన్ని దేవి ఎడమ చేతిలో (లేదా ఆమె ముందు నేలపై) సమర్పించండి."}},
}


NYASA_VERSES = [
 ("khaḍginī śūlinī", {"pada": [["khaḍginī","bearer of the sword","ఖడ్గిని"],["śūlinī","bearer of the trident","శూలిని"],["ghorā","terrible","ఘోర"],["gadinī","bearer of the mace","గదిని"],["cakriṇī","bearer of the discus","చక్రిణి"],["śaṅkhinī","bearer of the conch","శంఖిని"],["cāpinī","bearer of the bow","చాపిని"],["bāṇa","arrows","బాణ"],["bhuśuṇḍī","sling","భుశుండి"],["parighāyudhā","armed with the iron club","పరిఘాయుధ"]],
   "en": "'She bears the sword and trident; she is terrible; she bears the mace and discus, the conch and bow, arrows, sling and iron club.'",
   "te": "'ఖడ్గం, శూలం ధరించిన ఘోర; గద, చక్రం, శంఖం, ధనుస్సు, బాణాలు, భుశుండి, పరిఘ ఆయుధాలు గలది.'",
   "src": "1.81"}),
 ("śūlena pāhi", {"pada": [["śūlena","with the spear","శూలంతో"],["pāhi","protect","రక్షించు"],["naḥ","us","మమ్మల్ని"],["devi","O Goddess","ఓ దేవీ"],["khaḍgena","with the sword","ఖడ్గంతో"],["ambike","O Ambikā","ఓ అంబికా"],["ghaṇṭā","bell","ఘంట"],["svanena","with the sound","నాదంతో"],["cāpajyā","bowstring","అల్లెతాడు"],["niḥsvanena","with the twang","ధ్వనితో"]],
   "en": "'Protect us with your spear, O Goddess; protect us with your sword, Ambikā; protect us with the sound of your bell and the twang of your bowstring.'",
   "te": "'ఓ దేవీ, శూలంతో మమ్మల్ని రక్షించు; ఓ అంబికా, ఖడ్గంతో రక్షించు; ఘంటానాదంతో, అల్లెతాటి ధ్వనితో రక్షించు.'",
   "src": "4.24"}),
 ("prācyāṃ rakṣa", {"pada": [["prācyām","in the east","తూర్పున"],["rakṣa","protect","రక్షించు"],["pratīcyām","in the west","పడమరన"],["caṇḍike","O Caṇḍikā","ఓ చండికా"],["dakṣiṇe","in the south","దక్షిణాన"],["bhrāmaṇena","by whirling","తిప్పడంతో"],["ātma","your own","నీ"],["śūlasya","spear","శూలాన్ని"],["uttarasyām","in the north","ఉత్తరాన"],["īśvari","O sovereign","ఓ ఈశ్వరీ"]],
   "en": "'Protect us in the east and the west, Caṇḍikā; protect us in the south; and, by whirling your spear, in the north too, O sovereign.'",
   "te": "'ఓ చండికా, తూర్పున, పడమరన, దక్షిణాన రక్షించు; ఓ ఈశ్వరీ, నీ శూలాన్ని తిప్పుతూ ఉత్తరాన కూడా రక్షించు.'",
   "src": "4.25"}),
 ("saumyāni yāni", {"pada": [["saumyāni","gentle","సౌమ్యమైన"],["yāni","which","ఏ"],["rūpāṇi","forms","రూపాలు"],["trailokye","in the three worlds","ముల్లోకాలలో"],["vicaranti","move about","సంచరిస్తాయో"],["te","your","నీ"],["atyartha","exceedingly","అత్యంత"],["ghorāṇi","terrible","ఘోరమైనవి"],["taiḥ","with those","వాటితో"],["rakṣa","protect","రక్షించు"],["asmān","us","మమ్మల్ని"],["bhuvam","the earth","భూమిని"]],
   "en": "'With your gentle forms that move about the three worlds, and with those that are exceedingly terrible, protect us and the earth.'",
   "te": "'ముల్లోకాలలో సంచరించే నీ సౌమ్య రూపాలతో, అత్యంత ఘోర రూపాలతో మమ్మల్ని, భూమిని రక్షించు.'",
   "src": "4.26"}),
 ("khaḍgaśūlagadādīni", {"pada": [["khaḍga","sword","ఖడ్గం"],["śūla","trident","శూలం"],["gadā","mace","గద"],["ādīni","and the rest","మొదలైన"],["astrāṇi","weapons","అస్త్రాలు"],["te","your","నీ"],["ambike","O Ambikā","ఓ అంబికా"],["karapallava","tender hands","కరపల్లవాలను"],["saṅgīni","clinging to","అంటుకొని ఉన్న"],["taiḥ","with those","వాటితో"],["rakṣa","protect","రక్షించు"],["asmān","us","మమ్మల్ని"],["sarvataḥ","on every side","అన్ని వైపుల నుండి"]],
   "en": "'With the sword, trident, mace and the other weapons that rest in your tender hands, Ambikā, protect us on every side.'",
   "te": "'ఓ అంబికా, నీ కరపల్లవాలలో ఉన్న ఖడ్గం, శూలం, గద మొదలైన అస్త్రాలతో మమ్మల్ని అన్ని వైపుల నుండి రక్షించు.'",
   "src": "4.27"}),
 ("sarvasvarūpe", {"pada": [["sarvasvarūpe","whose form is all","సర్వస్వరూపిణీ"],["sarveśe","ruler of all","సర్వేశా"],["sarvaśakti","all powers","సర్వశక్తులతో"],["samanvite","endowed with","కూడినదానా"],["bhayebhyaḥ","from fears","భయాల నుండి"],["trāhi","save","రక్షించు"],["naḥ","us","మమ్మల్ని"],["devi","O Goddess","ఓ దేవీ"],["durge","O Durgā","ఓ దుర్గా"],["namaḥ astu te","salutations to you","నీకు నమస్కారం"]],
   "en": "'You whose form is everything, ruler of all, endowed with every power, save us from fears, O Goddess. O Durgā Devī, salutations to you.'",
   "te": "'సర్వస్వరూపిణీ, సర్వేశా, సర్వశక్తులతో కూడినదానా, ఓ దేవీ, భయాల నుండి మమ్మల్ని రక్షించు. దుర్గాదేవీ, నీకు నమస్కారం.'",
   "src": "11.24"}),
]


def build_nyasa(sec):
    out = {"_intro": {
        "en": "The Saptaśatī Nyāsa is done just before the 13 chapters. Its viniyoga names the seers, deities, metres, śaktis, bījas, elements and Vedas of the three caritas. The nyāsa itself uses six protective verses from the text (1.81, 4.24–4.27, 11.24), first on the fingers, then on the six 'limbs', followed by the dhyāna of Durgā.",
        "te": "సప్తశతీ న్యాసం 13 అధ్యాయాలకు సరిగ్గా ముందు చేస్తారు. దీని వినియోగం మూడు చరిత్రల ఋషులు, దేవతలు, ఛందస్సులు, శక్తులు, బీజాలు, తత్త్వాలు, వేదాలను చెబుతుంది. న్యాసం గ్రంథంలోని ఆరు రక్షా శ్లోకాలను (1.81, 4.24–4.27, 11.24) ఉపయోగిస్తుంది: మొదట వేళ్ళపై, తరువాత ఆరు 'అంగాల'పై; తరువాత దుర్గా ధ్యానం."}}
    out["1"] = {"pada": [["prathama","first","ప్రథమ"],["madhyama","middle","మధ్యమ"],["uttara","last","ఉత్తమ"],["caritrāṇām","of the stories","చరిత్రలకు"],["brahma","Brahmā","బ్రహ్మ"],["viṣṇu","Viṣṇu","విష్ణు"],["rudrāḥ","Rudra","రుద్రులు"],["ṛṣayaḥ","the seers","ఋషులు"],["devatāḥ","the deities","దేవతలు"],["chandāṃsi","the metres","ఛందస్సులు"],["nandā","Nandā","నంద"],["śākambharī","Śākambharī","శాకంభరి"],["bhīmāḥ","and Bhīmā","భీమలు"],["śaktayaḥ","the powers","శక్తులు"],["raktadantikā","Raktadantikā","రక్తదంతిక"],["durgā","Durgā","దుర్గ"],["bhrāmaryaḥ","and Bhrāmarī","భ్రామరులు"],["bījāni","the seeds","బీజాలు"],["agni","fire","అగ్ని"],["vāyu","wind","వాయువు"],["sūryāḥ","and sun","సూర్యులు"],["tattvāni","the elements","తత్త్వాలు"],["ṛk","Ṛg","ఋక్"],["yajuḥ","Yajur","యజుర్"],["sāma","Sāma","సామ"],["vedāḥ","Vedas","వేదాలు"],["dhyānāni","the meditations","ధ్యానాలు"],["sakala","all","సకల"],["kāmanā","wishes","కామనల"],["siddhaye","for the fulfilment of","సిద్ధి కోసం"],["viniyogaḥ","is the application","వినియోగం"]],
        "en": "Of the first, middle and last caritas: Brahmā, Viṣṇu and Rudra are the seers; Mahākālī, Mahālakṣmī and Mahāsarasvatī the deities; gāyatrī, uṣṇik and anuṣṭubh the metres; Nandā, Śākambharī and Bhīmā the śaktis; Raktadantikā, Durgā and Bhrāmarī the bījas; fire, wind and sun the elements; the Ṛg, Yajur and Sāma Vedas the meditations. It is applied in japa for the fulfilment of all wishes and the pleasure of Mahākālī, Mahālakṣmī and Mahāsarasvatī.",
        "te": "ప్రథమ, మధ్యమ, ఉత్తమ చరిత్రలకు: బ్రహ్మ, విష్ణు, రుద్రులు ఋషులు; మహాకాళి, మహాలక్ష్మి, మహాసరస్వతులు దేవతలు; గాయత్రి, ఉష్ణిక్, అనుష్టుప్ ఛందస్సులు; నంద, శాకంభరి, భీమలు శక్తులు; రక్తదంతిక, దుర్గ, భ్రామరులు బీజాలు; అగ్ని, వాయువు, సూర్యులు తత్త్వాలు; ఋగ్, యజుర్, సామ వేదాలు ధ్యానాలు. సకల కామనా సిద్ధి కోసం, మహాకాళీ మహాలక్ష్మీ మహాసరస్వతుల ప్రీతి కోసం జపంలో వినియోగం.",
        "ctx": {"en": "Each list of three matches the three caritas in order: the first carita (Ch. 1) belongs to Brahmā, Mahākālī, gāyatrī, and so on.", "te": "ప్రతి మూడింటి జాబితా మూడు చరిత్రలకు వరుసగా సరిపోతుంది: ప్రథమ చరిత్ర (1వ అధ్యా.) బ్రహ్మ, మహాకాళి, గాయత్రి మొదలైనవి."}}
    fingers = [('aṅguṣṭhābhyāṃ','to the two thumbs','రెండు బొటనవేళ్ళకు','run both index fingers along both thumbs','రెండు చూపుడువేళ్ళతో రెండు బొటనవేళ్ళను తాకండి'),
               ('tarjanībhyāṃ','to the two index fingers','రెండు చూపుడువేళ్ళకు','run both thumbs along both index fingers','రెండు బొటనవేళ్ళతో చూపుడువేళ్ళను తాకండి'),
               ('madhyamābhyāṃ','to the two middle fingers','రెండు మధ్యవేళ్ళకు','run both thumbs along both middle fingers','రెండు బొటనవేళ్ళతో మధ్యవేళ్ళను తాకండి'),
               ('anāmikābhyāṃ','to the two ring fingers','రెండు ఉంగరపువేళ్ళకు','run both thumbs along both ring fingers','రెండు బొటనవేళ్ళతో ఉంగరపువేళ్ళను తాకండి'),
               ('kaniṣṭhikābhyāṃ','to the two little fingers','రెండు చిటికెనవేళ్ళకు','run both thumbs along both little fingers','రెండు బొటనవేళ్ళతో చిటికెనవేళ్ళను తాకండి'),
               ('karatalakarapṛṣṭhābhyāṃ','to palms and backs of the hands','అరచేతులకు, చేతుల వెనుక భాగాలకు','touch the palms and backs of both hands','రెండు చేతుల అరచేతులను, వెనుక భాగాలను తాకండి')]
    angas = list(ANGA.items())
    for i, (key, base) in enumerate(NYASA_VERSES):
        f = fingers[i]
        a, (ag_en, ag_te, aw, ado_en, ado_te) = angas[i]
        for ref, extra, do_en, do_te, label_en, label_te in [
            (str(2 + i), [[f[0], f[1], f[2]], ['namaḥ', 'salutation', 'నమస్కారం']], f[3], f[4], 'Kara Nyāsa', 'కర న్యాసం'),
            (str(8 + i), [[a, ag_en, ag_te], [aw, *ANGA_WORD[aw]]], ado_en, ado_te, 'Hṛdayādi Nyāsa', 'హృదయాది న్యాసం')]:
            n = {"pada": base['pada'] + extra,
                 "en": f"{base['en']} ({label_en}: {do_en}.)",
                 "te": f"{base['te']} ({label_te}: {do_te}.)"}
            if i == 0:
                n["ctx"] = {"en": f"{label_en}: each verse is recited, then the closing phrase with the touch. This verse is {base['src']} of the text.",
                            "te": f"{label_te}: ప్రతి శ్లోకాన్ని పఠించి, ముగింపు పదంతో తాకాలి. ఈ శ్లోకం గ్రంథంలోని {base['src']}."}
            else:
                n["ctx"] = {"en": f"This verse is {base['src']} of the text.", "te": f"ఈ శ్లోకం గ్రంథంలోని {base['src']}."}
            out[ref] = n
    out["14"] = {"pada": [["vidyut","lightning","మెరుపు"],["dāma","streak","రేఖ"],["sama","equal","సమానమైన"],["prabhām","radiance","ప్రభ గలదానిని"],["mṛgapati","the lion's","సింహపు"],["skandha","shoulder","భుజంపై"],["sthitām","seated","ఉన్నదానిని"],["bhīṣaṇām","fearsome","భీషణను"],["kanyābhiḥ","by maidens","కన్యల చేత"],["karavāla","swords","ఖడ్గాలు"],["kheṭa","shields","డాళ్ళు"],["vilasat","gleaming","ప్రకాశించే"],["hastābhiḥ","in whose hands","చేతులు గల"],["āsevitām","attended","సేవించబడేదానిని"],["hastaiḥ","in her hands","చేతులలో"],["cakra","discus","చక్రం"],["gadā","mace","గద"],["asi","sword","ఖడ్గం"],["kheṭa","shield","డాలు"],["viśikhān","arrows","బాణాలు"],["cāpam","bow","ధనుస్సు"],["guṇam","noose","పాశం"],["tarjanīm","the warning gesture","తర్జనీ ముద్ర"],["bibhrāṇām","holding","ధరించినదానిని"],["anala","fire","అగ్ని"],["ātmikām","whose nature is","స్వరూపిణిని"],["śaśidharām","bearing the moon","చంద్రుని ధరించినదానిని"],["durgām","Durgā","దుర్గను"],["trinetrām","three-eyed","త్రినేత్రను"],["bhaje","I worship","భజిస్తాను"]],
        "en": "I worship three-eyed Durgā, radiant as a streak of lightning, seated on the lion's shoulder, fearsome, attended by maidens with swords and shields gleaming in their hands; who holds discus, mace, sword, shield, arrows, bow and noose and shows the warning finger; whose nature is fire and who bears the moon.",
        "te": "మెరుపు రేఖ వంటి ప్రభతో, సింహపు భుజంపై కూర్చొని, భీషణంగా, ఖడ్గాలు డాళ్ళు చేతుల్లో ప్రకాశించే కన్యలచే సేవించబడుతూ, చక్రం, గద, ఖడ్గం, డాలు, బాణాలు, ధనుస్సు, పాశం, తర్జనీ ముద్ర ధరించి, అగ్నిస్వరూపిణిగా, చంద్రుని ధరించిన త్రినేత్ర దుర్గను భజిస్తాను.",
        "ctx": {"en": "Nearly the same as the Chapter 12 dhyāna (which reads 'vidyuddhāma', 'flash of lightning').", "te": "12వ అధ్యాయ ధ్యానానికి దాదాపు సమానం (అక్కడ 'విద్యుద్ధామ', 'మెరుపు కాంతి' అని ఉంది)."}}
    return out


if __name__ == '__main__':
    text = json.load(open(os.path.join(HERE, '..', 'site', 'data', 'text.json'), encoding='utf-8'))['sections']
    for name, fn in [('navarna', build_navarna), ('saptashati-nyasa', build_nyasa)]:
        notes = fn(text[name])
        with open(os.path.join(HERE, f'{name}.json'), 'w', encoding='utf-8') as f:
            json.dump(notes, f, ensure_ascii=False, indent=1)
        print(name, len([k for k in notes if not k.startswith('_')]))
