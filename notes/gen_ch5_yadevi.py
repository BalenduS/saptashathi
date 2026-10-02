"""Generate notes for the 'yā devī sarvabhūteṣu' verses of Chapter 5 (5.14–5.80) and 5.81–5.82."""
import json, os

HEAD = [["yā","she who","ఏ"],["devī","the Goddess","దేవి"],["sarvabhūteṣu","in all beings","సమస్త జీవులలో"]]
TAIL = [["namaḥ tasyai","salutation to her","ఆమెకు నమస్కారం"],["namaḥ tasyai","salutation to her","ఆమెకు నమస్కారం"],["namaḥ tasyai","salutation to her","ఆమెకు నమస్కారం"],["namaḥ namaḥ","salutation, salutation","నమో నమః"]]
SAL_EN = "Salutation to her, salutation to her, salutation to her; salutation again and again."
SAL_TE = "ఆమెకు నమస్కారం, ఆమెకు నమస్కారం, ఆమెకు నమస్కారం, నమో నమః."

# ref, word (as in text), en gloss, te gloss, en form phrase, te form phrase
FORMS = [
 ("5.14-16", ["viṣṇumāyā iti","as Viṣṇumāyā, Viṣṇu's power of illusion","విష్ణుమాయ అని"], ["śabditā","is called","పిలువబడుతుందో"], "is called Viṣṇumāyā", "విష్ణుమాయ అని పిలువబడుతుందో"),
 ("5.17-19", ["cetanā iti","as consciousness","చేతన (చైతన్యం) అని"], ["abhidhīyate","is named","చెప్పబడుతుందో"], "is named consciousness", "చైతన్యం అని చెప్పబడుతుందో"),
 ("5.20-22", ["buddhirūpeṇa","in the form of intelligence","బుద్ధి రూపంలో"], None, "abides as intelligence", "బుద్ధి రూపంలో నెలకొని ఉందో"),
 ("5.23-25", ["nidrārūpeṇa","in the form of sleep","నిద్ర రూపంలో"], None, "abides as sleep", "నిద్ర రూపంలో నెలకొని ఉందో"),
 ("5.26-28", ["kṣudhārūpeṇa","in the form of hunger","ఆకలి రూపంలో"], None, "abides as hunger", "క్షుధ (ఆకలి) రూపంలో నెలకొని ఉందో"),
 ("5.29-31", ["chāyārūpeṇa","in the form of shadow, reflection","ఛాయ రూపంలో"], None, "abides as shadow", "ఛాయ రూపంలో నెలకొని ఉందో"),
 ("5.32-34", ["śaktirūpeṇa","in the form of power","శక్తి రూపంలో"], None, "abides as power", "శక్తి రూపంలో నెలకొని ఉందో"),
 ("5.35-37", ["tṛṣṇārūpeṇa","in the form of thirst, craving","తృష్ణ రూపంలో"], None, "abides as thirst and craving", "తృష్ణ (దాహం, ఆశ) రూపంలో నెలకొని ఉందో"),
 ("5.38-40", ["kṣāntirūpeṇa","in the form of forbearance","క్షాంతి (సహనం) రూపంలో"], None, "abides as forbearance", "క్షాంతి (సహనం) రూపంలో నెలకొని ఉందో"),
 ("5.41-43", ["jātirūpeṇa","in the form of birth, kind","జాతి రూపంలో"], None, "abides as birth and kind", "జాతి రూపంలో నెలకొని ఉందో"),
 ("5.44-46", ["lajjārūpeṇa","in the form of modesty","లజ్జ రూపంలో"], None, "abides as modesty", "లజ్జ రూపంలో నెలకొని ఉందో"),
 ("5.47-49", ["śāntirūpeṇa","in the form of peace","శాంతి రూపంలో"], None, "abides as peace", "శాంతి రూపంలో నెలకొని ఉందో"),
 ("5.50-52", ["śraddhārūpeṇa","in the form of faith","శ్రద్ధ రూపంలో"], None, "abides as faith", "శ్రద్ధ రూపంలో నెలకొని ఉందో"),
 ("5.53-55", ["kāntirūpeṇa","in the form of beauty, radiance","కాంతి రూపంలో"], None, "abides as beauty", "కాంతి రూపంలో నెలకొని ఉందో"),
 ("5.56-58", ["lakṣmīrūpeṇa","in the form of fortune","లక్ష్మీ రూపంలో"], None, "abides as fortune", "లక్ష్మీ రూపంలో నెలకొని ఉందో"),
 ("5.59-61", ["vṛttirūpeṇa","in the form of activity, livelihood","వృత్తి రూపంలో"], None, "abides as activity and livelihood", "వృత్తి (కార్యం, జీవనోపాధి) రూపంలో నెలకొని ఉందో"),
 ("5.62-64", ["smṛtirūpeṇa","in the form of memory","స్మృతి రూపంలో"], None, "abides as memory", "స్మృతి రూపంలో నెలకొని ఉందో"),
 ("5.65-67", ["dayārūpeṇa","in the form of compassion","దయ రూపంలో"], None, "abides as compassion", "దయ రూపంలో నెలకొని ఉందో"),
 ("5.68-70", ["tuṣṭirūpeṇa","in the form of contentment","తుష్టి రూపంలో"], None, "abides as contentment", "తుష్టి (సంతృప్తి) రూపంలో నెలకొని ఉందో"),
 ("5.71-73", ["mātṛrūpeṇa","in the form of the mother","మాతృ రూపంలో"], None, "abides as the mother", "తల్లి రూపంలో నెలకొని ఉందో"),
 ("5.74-76", ["bhrāntirūpeṇa","in the form of error, delusion","భ్రాంతి రూపంలో"], None, "abides as error and delusion", "భ్రాంతి రూపంలో నెలకొని ఉందో"),
]
SAMSTHITA = ["saṃsthitā","abides","నెలకొని ఉందో"]

CTX = {
 "5.14-16": {"en": "The refrain hymn begins. Each verse names one thing that lives in every being, from consciousness and intelligence to hunger, sleep, craving and even error, and salutes the Devī as that. The point is that nothing in us, high or low, is outside her. Each of these verses counts as three mantras in the 700, one for each 'namas tasyai'.", "te": "పల్లవి స్తోత్రం మొదలవుతుంది. ప్రతి శ్లోకం సమస్త జీవులలో ఉండే ఒక దానిని, చైతన్యం, బుద్ధి నుండి ఆకలి, నిద్ర, తృష్ణ, భ్రాంతి వరకు, పేర్కొని దేవికి ఆ రూపంలో నమస్కరిస్తుంది. మనలోని ఉన్నతమైనదైనా, అల్పమైనదైనా ఏదీ ఆమెకు వెలుపల లేదని భావం. 700 గణనలో ఈ ప్రతి శ్లోకం మూడు మంత్రాలుగా లెక్కించబడుతుంది, ఒక్కో 'నమస్తస్యై'కి ఒకటి."},
 "5.23-25": {"en": "Sleep, hunger, thirst: even the most ordinary bodily states are named as her forms. The same Goddess appeared in Chapter 1 as Yoganidrā, the sleep of Viṣṇu.", "te": "నిద్ర, ఆకలి, దాహం: అతి సామాన్యమైన శారీరక స్థితులు కూడా ఆమె రూపాలుగా చెప్పబడ్డాయి. ఇదే దేవి 1వ అధ్యాయంలో విష్ణువు నిద్ర అయిన యోగనిద్రగా కనిపించింది."},
 "5.74-76": {"en": "The list ends with bhrānti, error or delusion. Even our mistakes are her play: the same Mahāmāyā who deludes is the one who frees, as the sage said in Chapter 1.", "te": "జాబితా భ్రాంతితో ముగుస్తుంది. మన పొరపాట్లు కూడా ఆమె లీలే: మోహింపజేసే మహామాయే విముక్తినీ ఇస్తుందని 1వ అధ్యాయంలో మహర్షి చెప్పాడు."},
}

out = {}
for ref, word, verb, en_form, te_form in FORMS:
    pada = HEAD + [word] + [verb or SAMSTHITA] + TAIL
    out[ref] = {
        "pada": pada,
        "en": f"To the Goddess who {en_form} in all beings: {SAL_EN}",
        "te": f"సమస్త జీవులలో ఏ దేవి {te_form}, ఆమెకు నమస్కారం, ఆమెకు నమస్కారం, ఆమెకు నమస్కారం, నమో నమః.",
    }
    if ref in CTX:
        out[ref]["ctx"] = CTX[ref]

out["5.77"] = {
 "pada": [["indriyāṇām","of the senses","ఇంద్రియాలకు"],["adhiṣṭhātrī","the presiding power","అధిష్ఠాత్రి"],["bhūtānām","of the elements","భూతాలకు"],["ca","and","మరియు"],["akhileṣu","in all","సమస్త"],["yā","she who","ఎవరైతే"],["bhūteṣu","beings","జీవులలో"],["satatam","always","ఎల్లప్పుడూ"],["tasyai","to her","ఆమెకు"],["vyāptyai","who pervades","వ్యాపించిన"],["devyai","to the Goddess","దేవికి"],["namaḥ namaḥ","salutations","నమో నమః"]],
 "en": "To the Goddess who presides over the senses and the elements, and who always pervades all beings: salutations again and again.",
 "te": "ఇంద్రియాలకు, పంచభూతాలకు అధిష్ఠాత్రి అయి, సమస్త జీవులలో ఎల్లప్పుడూ వ్యాపించి ఉన్న దేవికి నమో నమః."
}
out["5.78-80"] = {
 "pada": [["citi","pure consciousness","చితి (శుద్ధ చైతన్యం)"],["rūpeṇa","in the form of","రూపంలో"],["yā","she who","ఎవరైతే"],["kṛtsnam","the whole","సమస్త"],["etat","this","ఈ"],["vyāpya","pervading","వ్యాపించి"],["sthitā","abides","ఉందో"],["jagat","world","జగత్తును"]] + TAIL,
 "en": "To her who, as pure consciousness, pervades and abides in this whole world: " + SAL_EN,
 "te": "శుద్ధ చైతన్య రూపంలో ఈ సమస్త జగత్తును వ్యాపించి ఉన్న ఆమెకు నమస్కారం, ఆమెకు నమస్కారం, ఆమెకు నమస్కారం, నమో నమః.",
 "ctx": {"en": "The hymn ends where it began, with consciousness, now as citi, pure awareness that fills everything. 5.17 said consciousness lives in each being; 5.78 says it is the whole world.", "te": "స్తోత్రం మొదలైన చోటే, చైతన్యంతోనే ముగుస్తుంది; ఇప్పుడు అది సమస్తాన్నీ నింపే శుద్ధ చైతన్యం (చితి). 5.17 ప్రతి జీవిలో చైతన్యం ఉందని చెప్పింది; 5.78 అదే సమస్త జగత్తు అని చెబుతుంది."}
}
out["5.81"] = {
 "pada": [["stutā","praised","స్తుతించబడిన"],["suraiḥ","by the gods","దేవతల చేత"],["pūrvam","before","పూర్వం"],["abhīṣṭa","desired","కోరిన"],["saṃśrayāt","for the sake of their refuge","ఆశ్రయం కోసం"],["tathā","and","అలాగే"],["surendreṇa","by Indra","ఇంద్రుని చేత"],["dineṣu","for days","రోజుల పాటు"],["sevitā","served","సేవించబడిన"],["karotu","may she do","చేయుగాక"],["sā","she","ఆ"],["naḥ","for us","మాకు"],["śubha","good","శుభానికి"],["hetuḥ","the cause","కారణమైన"],["īśvarī","the Sovereign","ఈశ్వరి"],["śubhāni","good things","శుభాలను"],["bhadrāṇi","blessings","భద్రాలను"],["abhihantu","may she strike down","నశింపజేయుగాక"],["ca","and","మరియు"],["āpadaḥ","calamities","ఆపదలను"]],
 "en": "She was praised by the gods long ago for the refuge they sought, and served by Indra for many days. May that Sovereign, the source of all good, bring us what is good and blessed, and strike down our calamities.",
 "te": "కోరిన ఆశ్రయం కోసం పూర్వం దేవతలచేత స్తుతించబడి, ఇంద్రుని చేత ఎన్నో రోజులు సేవించబడిన శుభకారిణి అయిన ఆ ఈశ్వరి మాకు శుభాలను, భద్రాలను చేయుగాక; మా ఆపదలను నశింపజేయుగాక."
}
out["5.82"] = {
 "pada": [["yā","she who","ఎవరైతే"],["sāmpratam","now","ఇప్పుడు"],["ca","and","మరియు"],["uddhata","arrogant","గర్విష్ఠులైన"],["daitya","daityas","దైత్యుల చేత"],["tāpitaiḥ","tormented","పీడించబడిన"],["asmābhiḥ","by us","మా చేత"],["īśā","the ruler","ఈశ్వరి"],["ca","and","మరియు"],["suraiḥ","by the gods","దేవతల చేత"],["namasyate","is bowed to","నమస్కరించబడుతోందో"],["yā","she who","ఎవరైతే"],["ca","and","మరియు"],["smṛtā","when remembered","స్మరించబడిన"],["tat kṣaṇam eva","that very moment","ఆ క్షణమే"],["hanti","destroys","నశింపజేస్తుందో"],["naḥ","our","మా"],["sarva","all","సమస్త"],["āpadaḥ","calamities","ఆపదలను"],["bhakti","devotion","భక్తితో"],["vinamra","bowed","వంగిన"],["mūrtibhiḥ","by those whose bodies are","శరీరాలు గలవారి చేత"]],
 "en": "She is the ruler to whom we gods, tormented now by the arrogant daityas, bow; and when remembered by those bowed in devotion, she destroys all our calamities at that very moment.",
 "te": "గర్విష్ఠులైన దైత్యులచేత ఇప్పుడు పీడించబడుతున్న దేవతలమైన మేము ఏ ఈశ్వరికి నమస్కరిస్తున్నామో, భక్తితో వంగినవారు స్మరించగానే ఆ క్షణమే మా సమస్త ఆపదలను ఆమె నశింపజేస్తుంది."
}

here = os.path.dirname(os.path.abspath(__file__))
json.dump(out, open(os.path.join(here, 'parts', 'ch5.b.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out), 'entries')
