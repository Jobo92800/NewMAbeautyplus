#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build du site mabeautyplus.fr
Assemble : parts/head.tpl + CSS + header + <body de page> + form + footer + scripts
Usage : python3 build.py
"""
import os, re, json, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
P    = lambda *a: os.path.join(ROOT, *a)
DIST = P('dist')

def read(p):  return open(P(p), encoding='utf-8').read()

HEAD_TPL = read('parts/head.tpl.html')
BASE_CSS = read('parts/base.css')
MID      = read('parts/mid.html')
HEADER   = read('parts/header.html')
FOOTER   = read('parts/footer.html')
SCRIPTS  = read('parts/scripts.html')
FORM     = read('parts/form.html')

TEL       = '04 66 73 02 00'
TEL_INTL  = '+33466730200'
MAIL      = 'contact@mabeautyplus.fr'
CALENDLY  = 'https://calendly.com/contact-mbdpro/votre-appel-decouverte-avec-notre-conseillere-clone-2'

# ═══════════════════════════════════════════════════════════════
#  CSS additionnel (pages intérieures)
# ═══════════════════════════════════════════════════════════════
EXTRA_CSS = """
/* ---------- Hero pages intérieures ---------- */
.phero{background:radial-gradient(900px 420px at 85% -20%,rgba(232,49,138,.09),transparent 60%),
  radial-gradient(800px 420px at 0% 120%,rgba(59,191,191,.12),transparent 60%),var(--cream);
  padding:56px 0 60px}
.phero h1{font-size:clamp(1.85rem,4.8vw,2.9rem);font-weight:800;margin-bottom:16px;max-width:820px}
.phero .sub{font-size:1.08rem;color:var(--muted);max-width:720px;margin-bottom:26px}
.crumb{font-size:.84rem;color:var(--muted);margin-bottom:16px}
.crumb a{color:var(--teal-dark);font-weight:600}
.crumb span{margin:0 7px;opacity:.5}

/* ---------- Prose (pages légales / éditoriales) ---------- */
.prose{max-width:820px;margin:0 auto}
.prose h2{font-size:1.42rem;margin:38px 0 12px;color:var(--dark-title)}
.prose h3{font-size:1.1rem;margin:24px 0 8px;color:var(--teal-dark)}
.prose p,.prose li{color:var(--mid);font-size:1rem;margin-bottom:12px}
.prose ul,.prose ol{padding-left:22px;margin-bottom:16px}
.prose li{margin-bottom:7px}
.prose a{color:var(--pink);font-weight:600;text-decoration:underline}
.prose table{width:100%;border-collapse:collapse;margin:18px 0;font-size:.94rem}
.prose th,.prose td{border:1px solid var(--line);padding:10px 12px;text-align:left}
.prose th{background:var(--teal-light);color:var(--teal-dark);font-weight:700}
.todo{background:#FFF6DC;border:1px solid #F0D48A;border-radius:12px;padding:14px 16px;
  font-size:.92rem;color:#7A5A10;margin:14px 0}
.todo b{color:#5C4208}

/* ---------- Fiche centre ---------- */
.centre-grid{display:grid;gap:34px;align-items:start}
@media(min-width:940px){.centre-grid{grid-template-columns:1fr 1fr}}
.infobox{background:#fff;border:1px solid var(--line);border-radius:var(--radius);
  padding:26px 24px;box-shadow:var(--shadow)}
.infobox h3{font-size:1.12rem;margin-bottom:16px}
.inforow{display:flex;gap:13px;padding:12px 0;border-bottom:1px solid var(--line);font-size:.95rem}
.inforow:last-child{border-bottom:none}
.inforow .k{color:var(--muted);min-width:96px;font-weight:600;flex-shrink:0}
.inforow .v{color:var(--ink)}
.inforow .v a{color:var(--teal-dark);font-weight:700}
.mapbox{border-radius:var(--radius);overflow:hidden;border:1px solid var(--line);box-shadow:var(--shadow)}
.mapbox iframe{display:block;width:100%;height:340px;border:0}
.gscore{display:inline-flex;align-items:center;gap:9px;background:var(--teal-light);
  border-radius:999px;padding:9px 17px;font-weight:700;color:var(--teal-dark);font-size:.94rem}
.equip-grid{display:grid;gap:11px;grid-template-columns:1fr 1fr;margin-top:26px}
@media(min-width:760px){.equip-grid{grid-template-columns:repeat(3,1fr)}}
.equip{background:#fff;border:1px solid var(--line);border-radius:13px;padding:15px 16px;
  font-weight:600;font-size:.93rem;color:var(--ink);transition:.2s;display:block}
.equip:hover{border-color:var(--teal);transform:translateY(-2px);box-shadow:var(--shadow-sm)}
.equip small{display:block;font-weight:500;color:var(--muted);font-size:.82rem;margin-top:3px}

/* ---------- Avis ---------- */
.rev-grid{display:grid;gap:18px;margin-top:38px}
@media(min-width:760px){.rev-grid{grid-template-columns:1fr 1fr}}
@media(min-width:1060px){.rev-grid{grid-template-columns:repeat(3,1fr)}}
.rev{background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:24px 22px;
  display:flex;flex-direction:column;box-shadow:var(--shadow)}
.rev .stars{color:#F5A623;font-size:.95rem;letter-spacing:2px;margin-bottom:11px}
.rev p{color:var(--mid);font-size:.95rem;margin-bottom:16px}
.rev .who{margin-top:auto;font-weight:700;color:var(--teal-dark);font-size:.92rem}
.rev .who small{display:block;font-weight:500;color:var(--muted);font-size:.8rem;margin-top:2px}

/* ---------- Contact ---------- */
.contact-grid{display:grid;gap:30px}
@media(min-width:940px){.contact-grid{grid-template-columns:.85fr 1.15fr}}
"""

# ═══════════════════════════════════════════════════════════════
#  DONNÉES CENTRES
# ═══════════════════════════════════════════════════════════════
LEVIERS = {
 'luxotherapie':            ('Luxothérapie', 'Métabolisme, compulsions, stress'),
 'reeducation-alimentaire': ('Rééducation alimentaire', 'Sans régime ni frustration'),
 'i-shape':                 ('I-Shape', 'Électrostimulation allongée'),
 'pressodynamie':           ('Pressodynamie', 'Drainage et jambes lourdes'),
 'cavitalyse':              ('Cavitalyse', 'Amas graisseux localisés'),
 'adipologie':              ('Adipologie', 'Ultrasons LFU multifocalisés'),
 'new-sequential':          ('New Séquential', 'Protocole séquentiel ciblé'),
 'mesojet':                 ('Mésojet', 'Hydroporation et radiofréquence'),
 'advance-lift':            ('Advance Lift', 'Soin anti-âge progressif'),
}

PILIERS = ['luxotherapie','reeducation-alimentaire','i-shape','pressodynamie']


CENTRES = [
 dict(slug='le-grau-du-roi', ville='Le Grau-du-Roi', zone='Camargue &amp; Petite Camargue',
      rue='63 Rue des Médards', cp='30240', lat=43.541137, lng=4.1364882,
      note='4,8', avis=147, dep='Gard (30)',
      autour='Aigues-Mortes, La Grande-Motte, Le Grau-du-Roi, Vauvert, Saint-Laurent-d’Aigouze',
      equip=PILIERS + ['advance-lift','cavitalyse','adipologie','new-sequential']),
 dict(slug='serignan', ville='Sérignan', zone='Biterrois &amp; littoral héraultais',
      rue='120 Avenue de la Plage', cp='34410', lat=43.2782779, lng=3.2840187,
      note='4,9', avis=129, dep='Hérault (34)',
      autour='Béziers, Valras-Plage, Villeneuve-lès-Béziers, Vendres, Portiragnes',
      equip=PILIERS + ['mesojet']),
 dict(slug='le-cres', ville='Le Crès', zone='Montpellier &amp; agglomération',
      rue='1 Avenue des Chasseurs', cp='34920', lat=43.6611466, lng=3.9358744,
      note='4,9', avis=69, dep='Hérault (34)',
      autour='Montpellier, Castelnau-le-Lez, Jacou, Vendargues, Saint-Aunès',
      equip=PILIERS + ['mesojet']),
 dict(slug='cabestany', ville='Cabestany', zone='Perpignan &amp; Roussillon',
      rue='4 Rue Ambroise Croizat', cp='66330', lat=42.6934213, lng=2.9303549,
      note='4,9', avis=30, dep='Pyrénées-Orientales (66)',
      autour='Perpignan, Saint-Nazaire, Canet-en-Roussillon, Théza, Alénya',
      equip=list(PILIERS)),
 dict(slug='avignon', ville='Avignon', zone='Vaucluse &amp; Provence',
      rue='8 Boulevard de la Fraternité', cp='84140', lat=43.9357177, lng=4.8722736,
      note='4,9', avis=8, dep='Vaucluse (84)',
      autour='Avignon, Montfavet, Le Pontet, Morières-lès-Avignon, Vedène',
      equip=list(PILIERS)),
]

def crumb(*items):
    out = ['<p class="crumb"><a href="/">Accueil</a>']
    for label, href in items:
        out.append('<span>›</span>' + (f'<a href="{href}">{label}</a>' if href else label))
    return ''.join(out) + '</p>'

# ═══════════════════════════════════════════════════════════════
#  PAGE CENTRE
# ═══════════════════════════════════════════════════════════════
def page_centre(c):
    equip = ''.join(
        f'<a class="equip" href="/{k}">{LEVIERS[k][0]}<small>{LEVIERS[k][1]}</small></a>'
        for k in c['equip'])
    autres = ''.join(
        f'<a class="ccard" href="/centres/{o["slug"]}"><div class="city">{o["ville"]}</div>'
        f'<div class="addr">{o["rue"]}<br>{o["cp"]}</div><span class="go">Voir le centre →</span></a>'
        for o in CENTRES if o['slug'] != c['slug'])

    body = f"""
<section class="phero">
  <div class="wrap">
    {crumb(('Nos centres','/centres'), (c['ville'], None))}
    <p class="eyebrow">{c['zone']}</p>
    <h1>Centre MAbeautyplus <span class="pink-text">{c['ville']}</span></h1>
    <p class="sub">La méthode MAbeautyplus à {c['ville']} : une analyse de composition corporelle offerte,
    puis un accompagnement construit sur vos données — métabolisme, alimentation, sommeil, stress et émotions.</p>
    <div class="hero-cta">
      <a href="#inscription" class="btn btn-pink btn-lg js-scroll">Mon analyse offerte</a>
      <a href="tel:0466730200" class="btn btn-ghost">📞 {TEL}</a>
    </div>
    <div style="margin-top:24px"><span class="gscore">★ {c['note']}/5 sur Google · {c['avis']} avis</span></div>
  </div>
</section>

<section>
  <div class="wrap centre-grid">
    <div class="infobox">
      <h3>Informations pratiques</h3>
      <div class="inforow"><span class="k">Adresse</span><span class="v">{c['rue']}<br>{c['cp']} {c['ville']}</span></div>
      <div class="inforow"><span class="k">Téléphone</span><span class="v"><a href="tel:0466730200">{TEL}</a></span></div>
      <div class="inforow"><span class="k">E-mail</span><span class="v"><a href="mailto:{MAIL}">{MAIL}</a></span></div>
      <div class="inforow"><span class="k">Horaires</span><span class="v">Lundi – Vendredi · 09h00 – 19h00<br>
        <span style="color:var(--muted);font-size:.88rem">Fermé samedi et dimanche</span></span></div>
      <div class="inforow"><span class="k">Département</span><span class="v">{c['dep']}</span></div>
      <div class="inforow"><span class="k">Zone</span><span class="v" style="color:var(--muted);font-size:.9rem">{c['autour']}</span></div>
      <div style="margin-top:20px"><a href="#inscription" class="btn btn-pink js-scroll">Réserver mon analyse offerte</a></div>
    </div>
    <div class="mapbox">
      <iframe src="https://www.google.com/maps?q={c['lat']},{c['lng']}&amp;hl=fr&amp;z=16&amp;output=embed"
        loading="lazy" referrerpolicy="no-referrer-when-downgrade"
        title="Localisation du centre MAbeautyplus {c['ville']}"></iframe>
    </div>
  </div>
</section>

<section class="levers">
  <div class="wrap center">
    <p class="eyebrow">Disponible dans ce centre</p>
    <h2 class="section-title">Les leviers du centre de {c['ville']}</h2>
    <p class="section-lead">Aucun levier n'est activé sans raison : c'est votre analyse initiale qui détermine
    lesquels sont pertinents, dans quel ordre et à quelle fréquence.</p>
  </div>
  <div class="wrap"><div class="equip-grid">{equip}</div></div>
</section>

<section class="approach">
  <div class="wrap center">
    <p class="eyebrow">Votre première visite</p>
    <h2 class="section-title">Comment ça se passe à {c['ville']}</h2>
  </div>
  <div class="wrap"><div class="steps-grid">
    <div class="step"><h3>Vous prenez contact</h3><p>Par téléphone ou via le formulaire. Une experte vous rappelle
      sous 24h pour un premier échange, sans engagement.</p></div>
    <div class="step"><h3>L'analyse offerte</h3><p>Environ 30 minutes au centre : échange sur votre parcours et
      analyse de composition corporelle — masse grasse, graisse viscérale, masse musculaire, eau, métabolisme de base.</p></div>
    <div class="step"><h3>Votre programme</h3><p>Nous vous présentons ce que nous avons observé et ce que nous
      proposons. Vous décidez ensuite, en connaissance de cause.</p></div>
  </div></div>
</section>

{FORM}

<section class="centers">
  <div class="wrap center">
    <p class="eyebrow">Nos autres centres</p>
    <h2 class="section-title">Vous êtes plus proche d'un autre centre ?</h2>
  </div>
  <div class="wrap"><div class="center-grid">{autres}</div></div>
</section>
"""
    jsonld = {
      "@context":"https://schema.org",
      "@type":"HealthAndBeautyBusiness",
      "@id":f"https://www.mabeautyplus.fr/centres/{c['slug']}#business",
      "name":f"MAbeautyplus {c['ville']}",
      "url":f"https://www.mabeautyplus.fr/centres/{c['slug']}",
      "image":"https://static.wixstatic.com/media/87a2c5_a02814c5cd4c4f868df0f8f91d317935~mv2.png",
      "telephone":TEL_INTL,
      "email":MAIL,
      "parentOrganization":{"@id":"https://www.mabeautyplus.fr/#organization"},
      "address":{"@type":"PostalAddress","streetAddress":c['rue'],"addressLocality":c['ville'],
                 "postalCode":c['cp'],"addressRegion":c['dep'],"addressCountry":"FR"},
      "geo":{"@type":"GeoCoordinates","latitude":c['lat'],"longitude":c['lng']},
      "openingHoursSpecification":[{"@type":"OpeningHoursSpecification",
        "dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday"],
        "opens":"09:00","closes":"19:00"}],
      "areaServed":[a.strip() for a in c['autour'].replace('’',"'").split(',')]
    }
    return dict(
      path=f"/centres/{c['slug']}",
      title=f"Centre MAbeautyplus {c['ville']} | Perte de poids, minceur & bien-être",
      desc=f"Centre MAbeautyplus à {c['ville']} ({c['cp']}) : analyse de composition corporelle offerte, "
           f"luxothérapie, rééducation alimentaire et soins minceur. {c['rue']}. Tél. {TEL}.",
      ogdesc=f"La méthode MAbeautyplus à {c['ville']} — analyse de composition corporelle offerte, sans engagement.",
      body=body, jsonld=jsonld)

# ═══════════════════════════════════════════════════════════════
#  HUB CENTRES
# ═══════════════════════════════════════════════════════════════
def page_centres_hub():
    cards = ''.join(f"""
      <a class="pathcard" href="/centres/{c['slug']}">
        <h3>{c['ville']}</h3>
        <p>{c['rue']} — {c['cp']}</p>
        <ul><li>{c['zone'].replace('&amp;','et')}</li><li>★ {c['note']}/5 · {c['avis']} avis Google</li>
        <li>Lundi – Vendredi · 09h – 19h</li></ul>
        <span class="more">Voir le centre</span>
      </a>""" for c in CENTRES)
    body = f"""
<section class="phero">
  <div class="wrap">
    {crumb(('Nos centres', None))}
    <p class="eyebrow">Près de chez vous</p>
    <h1>Nos 5 centres dans le <span class="pink-text">Sud de la France</span></h1>
    <p class="sub">Du Gard aux Pyrénées-Orientales, en passant par l'Hérault et le Vaucluse.
    Cinq centres, une même méthode et les mêmes standards de qualité.</p>
    <div class="hero-cta"><a href="#inscription" class="btn btn-pink btn-lg js-scroll">Mon analyse offerte</a></div>
  </div>
</section>

<section class="paths">
  <div class="wrap"><div class="paths-grid" style="grid-template-columns:repeat(auto-fit,minmax(240px,1fr))">{cards}</div></div>
</section>

<section>
  <div class="wrap center">
    <p class="eyebrow">Partout la même exigence</p>
    <h2 class="section-title">Ce que vous retrouverez dans chaque centre</h2>
  </div>
  <div class="wrap"><div class="pillar-grid">
    <div class="pillar"><div class="pillar-body"><h3>Des appareils certifiés</h3>
      <p>Équipements certifiés CE dispositif médical, entretenus et contrôlés, dans des cabines individuelles.</p></div></div>
    <div class="pillar"><div class="pillar-body"><h3>Des équipes formées</h3>
      <p>Des praticiennes formées à la méthode, qui vous suivent de l'analyse initiale jusqu'à la stabilisation.</p></div></div>
    <div class="pillar"><div class="pillar-body"><h3>Un protocole personnalisé</h3>
      <p>Aucun programme standardisé : chaque parcours part de vos données de composition corporelle.</p></div></div>
    <div class="pillar"><div class="pillar-body"><h3>Une hygiène irréprochable</h3>
      <p>Matériel stérilisé, cabines privées et protocoles d'hygiène appliqués entre chaque rendez-vous.</p></div></div>
  </div></div>
</section>

{FORM}
"""
    return dict(path='/centres',
      title='Nos 5 centres MAbeautyplus | Sud de la France',
      desc='Les centres MAbeautyplus : Le Grau-du-Roi, Sérignan, Le Crès (Montpellier), Cabestany (Perpignan) '
           'et Avignon. Analyse de composition corporelle offerte, sans engagement.',
      ogdesc='Cinq centres dans le Sud de la France, une même méthode d\'accompagnement global.',
      body=body, jsonld=None)

# ═══════════════════════════════════════════════════════════════
#  AVIS
# ═══════════════════════════════════════════════════════════════
REVIEWS = [
 ("Après plusieurs régimes essayés, j'avais perdu tout espoir. Quand on m'a dit que je pouvais manger de tout et "
  "quand même perdre du poids, j'ai voulu essayer. J'ai perdu 7 kg en 3 mois, sans frustration.", "Le Grau-du-Roi"),
 ("J'ai fait une cure de luxothérapie et d'électrostimulation allongée. J'en suis très satisfaite — et je n'ai pas "
  "repris un gramme depuis.", "Le Grau-du-Roi"),
 ("Des séances de luxothérapie très bénéfiques. Un vrai climat de confiance s'est créé, on m'a aidée à mettre en "
  "place de nouvelles habitudes alimentaires que je tiens toujours.", "Le Grau-du-Roi"),
 ("Une année d'accompagnement pour une prise de poids liée à la ménopause et un sommeil perturbé. Le résultat est "
  "là : perte de poids, meilleur sommeil, et surtout un vrai sentiment de bien-être.", "Sérignan"),
 ("J'étais sceptique au départ, et pourtant les résultats sont là. Dans ma tête je partais sur un régime, alors "
  "qu'il s'agit d'un rééquilibrage — une autre façon de manger qui n'a rien d'un régime.", "Sérignan"),
 ("En 12 séances, j'ai atteint mon objectif. Ma santé s'est nettement améliorée et ma silhouette s'est remodelée. "
  "Merci à toute l'équipe pour l'accueil, l'écoute et les conseils.", "Sérignan"),
 ("Le programme proposé au premier rendez-vous n'est pas une promesse miracle, mais un accompagnement sérieux, "
  "motivant et vraiment efficace. Le livret de rééquilibrage est remarquablement bien fait.", "Le Crès"),
 ("Neuf semaines après mon bilan, je me sens beaucoup mieux et j'ai moins mal aux genoux. L'accompagnement est "
  "encourageant, tout est bien expliqué et les échanges sont constructifs.", "Le Crès"),
 ("Grâce à la luxothérapie, les envies de sucre ont diminué dès les premières séances. Je suis végétarienne et "
  "l'accompagnement alimentaire a vraiment été adapté à mon cas.", "Le Crès"),
 ("J'ai une fibromyalgie et j'ai réussi à perdre du poids. L'accueil a été formidable, et le premier rendez-vous "
  "était une véritable analyse de composition corporelle. Très professionnel.", "Cabestany"),
 ("J'ai beaucoup appris sur la nutrition, l'équilibre alimentaire et les bonnes habitudes du quotidien. Une écoute "
  "attentive et des explications claires qui m'ont permis d'avancer à mon rythme.", "Cabestany"),
 ("J'avais tout essayé : programmes, substituts, jeûne… et à chaque fois je reprenais. Cette fois j'ai enfin trouvé "
  "une façon saine de perdre du poids et j'ai appris à rééquilibrer mon alimentation.", "Cabestany"),
 ("Toujours souriante, à l'écoute, ma thérapeute me motive sans pression et avec bienveillance. Je n'imaginais pas "
  "pouvoir me remuscler à 58 ans, ni dépasser mes pulsions alimentaires.", "Avignon"),
 ("Un accueil chaleureux et un accompagnement très professionnel. J'ai déjà vu la différence et ce n'est que le "
  "début. Merci à toute l'équipe.", "Avignon"),
 ("Je suis venue pour un bilan offert avec un objectif de perte de poids. Après 6 séances sur 12, ma silhouette "
  "est plus fine et mon ventre moins gonflé — c'était mon plus gros complexe.", "Avignon"),
]

def page_avis():
    total = sum(c['avis'] for c in CENTRES)
    cards = ''.join(f"""
      <div class="rev"><div class="stars">★★★★★</div><p>{t}</p>
      <div class="who">Cliente vérifiée<small>Centre de {v}</small></div></div>""" for t, v in REVIEWS)
    scores = ''.join(f"""
      <a class="ccard" href="/centres/{c['slug']}"><div class="city">{c['ville']}</div>
      <div class="addr"><b style="color:var(--ink);font-size:1.05rem">★ {c['note']}/5</b><br>{c['avis']} avis Google</div>
      <span class="go">Voir le centre →</span></a>""" for c in CENTRES)
    body = f"""
<section class="phero">
  <div class="wrap">
    {crumb(('Avis & témoignages', None))}
    <p class="eyebrow">Ils nous ont fait confiance</p>
    <h1>Avis et <span class="pink-text">témoignages</span></h1>
    <p class="sub">Plus de {total} avis déposés sur Google pour l'ensemble de nos centres. Voici une sélection
    de ce que nos clients nous ont écrit.</p>
    <div class="hero-cta"><a href="#inscription" class="btn btn-pink btn-lg js-scroll">Mon analyse offerte</a></div>
  </div>
</section>

<section class="centers">
  <div class="wrap center">
    <p class="eyebrow">Note Google par centre</p>
    <h2 class="section-title">Nos notes, centre par centre</h2>
  </div>
  <div class="wrap"><div class="center-grid">{scores}</div></div>
</section>

<section>
  <div class="wrap center">
    <p class="eyebrow">Témoignages</p>
    <h2 class="section-title">Ce qu'ils nous ont dit</h2>
    <p class="section-lead">Témoignages issus des avis Google de nos centres. Les résultats évoqués sont propres
    à chaque personne et ne constituent pas une promesse de résultat.</p>
  </div>
  <div class="wrap"><div class="rev-grid">{cards}</div></div>
</section>

{FORM}
"""
    return dict(path='/avis',
      title='Avis & témoignages clients | MAbeautyplus',
      desc=f'Plus de {total} avis Google sur les centres MAbeautyplus. Témoignages de personnes accompagnées '
           'en perte de poids, ménopause, stress et sommeil dans nos 5 centres du Sud de la France.',
      ogdesc='Les témoignages des personnes accompagnées chez MAbeautyplus.',
      body=body, jsonld=None)

# ═══════════════════════════════════════════════════════════════
#  CONTACT
# ═══════════════════════════════════════════════════════════════
def page_contact():
    rows = ''.join(f"""
      <div class="inforow"><span class="k">{c['ville']}</span>
      <span class="v">{c['rue']}, {c['cp']}<br>
      <a href="/centres/{c['slug']}">Voir la fiche du centre →</a></span></div>""" for c in CENTRES)
    body = f"""
<section class="phero">
  <div class="wrap">
    {crumb(('Contact', None))}
    <p class="eyebrow">Nous joindre</p>
    <h1>Parlons de vous, <span class="pink-text">en toute confiance</span></h1>
    <p class="sub">Un échange téléphonique pour vous écouter et définir ensemble ce qui vous convient le mieux.
    Confidentiel et sans aucun engagement.</p>
  </div>
</section>

<section>
  <div class="wrap contact-grid">
    <div class="infobox">
      <h3>Nous contacter</h3>
      <div class="inforow"><span class="k">Téléphone</span><span class="v"><a href="tel:0466730200">{TEL}</a></span></div>
      <div class="inforow"><span class="k">E-mail</span><span class="v"><a href="mailto:{MAIL}">{MAIL}</a></span></div>
      <div class="inforow"><span class="k">Horaires</span><span class="v">Lundi – Vendredi<br>09h00 – 19h00</span></div>
      <div class="inforow"><span class="k">Rendez-vous</span><span class="v"><a href="{CALENDLY}" target="_blank" rel="noopener" class="js-schedule">Réserver un créneau en ligne →</a></span></div>
    </div>
    <div class="infobox">
      <h3>Nos 5 centres</h3>
      {rows}
    </div>
  </div>
</section>

{FORM}
"""
    return dict(path='/contact',
      title='Contact | MAbeautyplus — 5 centres dans le Sud de la France',
      desc=f'Contactez MAbeautyplus : {TEL}, {MAIL}. Cinq centres au Grau-du-Roi, Sérignan, Le Crès, '
           'Cabestany et Avignon. Analyse de composition corporelle offerte, sans engagement.',
      ogdesc='Un échange téléphonique confidentiel et sans engagement.',
      body=body, jsonld=None)

# ═══════════════════════════════════════════════════════════════
#  PAGES LÉGALES
# ═══════════════════════════════════════════════════════════════
TODO = ('<div class="todo"><b>À compléter :</b> {}</div>')

CTA_BAND = f"""
<section class="formsec" id="inscription">
  <div class="wrap">
    <div class="form-card center">
      <span class="price-tag">Valeur 87€ — offert</span>
      <h2>Réservez votre analyse de composition corporelle <span class="pink-text">offerte</span></h2>
      <p class="reassure">Un premier échange téléphonique pour vous écouter, sans aucun engagement.</p>
      <div class="hero-cta" style="justify-content:center">
        <a href="/#inscription" class="btn btn-pink btn-lg">Mon analyse offerte</a>
        <a href="tel:0466730200" class="btn btn-ghost btn-lg">📞 {TEL}</a>
      </div>
    </div>
  </div>
</section>
"""

def legal_page(path, title, desc, h1, eyebrow, content):
    body = f"""
<section class="phero" style="padding:44px 0 40px">
  <div class="wrap">
    {crumb((h1, None))}
    <p class="eyebrow">{eyebrow}</p>
    <h1>{h1}</h1>
  </div>
</section>
<section><div class="wrap"><div class="prose">{content}</div></div></section>
{CTA_BAND}
"""
    return dict(path=path, title=title, desc=desc, ogdesc=desc, body=body, jsonld=None, noindex_ok=True)

MENTIONS = legal_page('/mentions-legales',
 'Mentions légales | MAbeautyplus',
 'Mentions légales du site mabeautyplus.fr : éditeur, directeur de publication, hébergeur et propriété intellectuelle.',
 'Mentions légales', 'Informations réglementaires', f"""
<p>Conformément à l'article 6 de la loi n° 2004-575 du 21 juin 2004 pour la confiance dans l'économie numérique,
il est précisé aux utilisateurs du site <b>www.mabeautyplus.fr</b> l'identité des différents intervenants dans le
cadre de sa réalisation et de son suivi.</p>

<h2>Éditeur du site</h2>
{TODO.format('raison sociale exacte, forme juridique (SARL, SAS…), montant du capital social, adresse du siège social, numéro SIRET, numéro RCS et ville d\'immatriculation, numéro de TVA intracommunautaire.')}
<table>
  <tr><th>Raison sociale</th><td>[ à compléter ]</td></tr>
  <tr><th>Forme juridique</th><td>[ à compléter ]</td></tr>
  <tr><th>Capital social</th><td>[ à compléter ]</td></tr>
  <tr><th>Siège social</th><td>[ à compléter ]</td></tr>
  <tr><th>SIRET</th><td>[ à compléter ]</td></tr>
  <tr><th>RCS</th><td>[ à compléter ]</td></tr>
  <tr><th>TVA intracommunautaire</th><td>[ à compléter ]</td></tr>
  <tr><th>Téléphone</th><td>{TEL}</td></tr>
  <tr><th>E-mail</th><td>{MAIL}</td></tr>
</table>

<h2>Directeur de la publication</h2>
{TODO.format('nom et prénom du directeur de la publication (généralement le représentant légal).')}
<p>[ à compléter ]</p>

<h2>Hébergeur du site</h2>
<p>Le site est hébergé par <b>Netlify, Inc.</b>, 512 2nd Street, Suite 200, San Francisco, CA 94107, États-Unis —
<a href="https://www.netlify.com" target="_blank" rel="noopener">www.netlify.com</a>.</p>
<p>Le nom de domaine est enregistré auprès d'<b>OVH SAS</b>, 2 rue Kellermann, 59100 Roubaix, France.</p>

<h2>Propriété intellectuelle</h2>
<p>L'ensemble des éléments composant le site — structure, textes, images, photographies, vidéos, logos, marques
et éléments graphiques — est la propriété exclusive de l'éditeur ou de ses partenaires, et est protégé par le
droit de la propriété intellectuelle. Toute reproduction, représentation, modification ou exploitation, totale ou
partielle, sans autorisation écrite préalable, est interdite et constituerait une contrefaçon au sens des articles
L.335-2 et suivants du Code de la propriété intellectuelle.</p>

<h2>Nature des prestations</h2>
<p>Les prestations proposées par MAbeautyplus relèvent du <b>bien-être et de l'esthétique</b>. Elles ne constituent
ni un traitement médical, ni un acte thérapeutique, ni un diagnostic, et ne se substituent en aucun cas à un avis,
un suivi ou un traitement médical. En cas de doute sur votre état de santé, ou si vous suivez un traitement, il
vous appartient de consulter un professionnel de santé avant de débuter un accompagnement. Les résultats évoqués
sur ce site sont propres à chaque personne et ne constituent pas une promesse de résultat.</p>

<h2>Liens hypertextes</h2>
<p>Le site peut contenir des liens vers des sites tiers. L'éditeur n'exerce aucun contrôle sur ces sites et décline
toute responsabilité quant à leur contenu ou à l'usage qui pourrait en être fait.</p>

<h2>Limitation de responsabilité</h2>
<p>L'éditeur s'efforce de fournir des informations aussi exactes que possible. Il ne saurait toutefois être tenu
responsable des omissions, inexactitudes ou carences dans la mise à jour, qu'elles soient de son fait ou du fait
de tiers partenaires. L'utilisateur reconnaît utiliser ces informations sous sa responsabilité exclusive.</p>

<h2>Droit applicable</h2>
<p>Les présentes mentions légales sont régies par le droit français. En cas de litige, et à défaut de résolution
amiable, les tribunaux français seront seuls compétents.</p>
""")

CONFID = legal_page('/politique-de-confidentialite',
 'Politique de confidentialité | MAbeautyplus',
 'Politique de confidentialité MAbeautyplus : données collectées, finalités, durée de conservation, '
 'destinataires et exercice de vos droits RGPD.',
 'Politique de confidentialité', 'Protection des données', f"""
<p>MAbeautyplus attache une importance particulière à la protection de vos données personnelles. La présente
politique décrit les traitements réalisés dans le cadre du site <b>www.mabeautyplus.fr</b>, conformément au
Règlement (UE) 2016/679 (RGPD) et à la loi Informatique et Libertés modifiée.</p>

<h2>Responsable de traitement</h2>
{TODO.format('raison sociale et adresse du responsable de traitement, identiques aux mentions légales.')}
<p>[ à compléter ] — Contact : <a href="mailto:{MAIL}">{MAIL}</a> · {TEL}</p>

<h2>Données collectées</h2>
<p>Via les formulaires du site, nous collectons les données que vous nous transmettez volontairement :</p>
<ul>
  <li>prénom et nom ;</li>
  <li>numéro de téléphone ;</li>
  <li>adresse e-mail ;</li>
  <li>centre choisi et objectif principal indiqué ;</li>
  <li>date et heure de la demande.</li>
</ul>
<p>Nous collectons également, via nos outils de mesure d'audience et de publicité, des données de navigation
(pages consultées, source de visite, identifiants techniques et de cookies). Voir la section « Cookies ».</p>

<h2>Finalités et bases légales</h2>
<table>
  <tr><th>Finalité</th><th>Base légale</th></tr>
  <tr><td>Vous recontacter suite à votre demande d'analyse offerte</td><td>Consentement (art. 6.1.a)</td></tr>
  <tr><td>Gestion de la relation client et suivi des rendez-vous</td><td>Exécution de mesures précontractuelles / contrat (art. 6.1.b)</td></tr>
  <tr><td>Mesure d'audience et amélioration du site</td><td>Consentement (cookies non essentiels)</td></tr>
  <tr><td>Publicité ciblée et mesure des campagnes</td><td>Consentement (cookies non essentiels)</td></tr>
</table>

<h2>Destinataires</h2>
<p>Vos données sont destinées aux équipes de MAbeautyplus et au centre que vous avez sélectionné. Elles sont
également traitées par nos sous-traitants techniques, agissant sur instruction et dans le cadre d'accords
conformes au RGPD :</p>
<ul>
  <li><b>Netlify, Inc.</b> — hébergement du site et traitement des soumissions de formulaire ;</li>
  <li><b>Airtable, Inc.</b> — enregistrement et gestion des demandes de contact ;</li>
  <li><b>Calendly LLC</b> — prise de rendez-vous en ligne ;</li>
  <li><b>Google Ireland Ltd.</b> — mesure d'audience (Google Analytics) et publicité (Google Ads) ;</li>
  <li><b>Meta Platforms Ireland Ltd.</b> — mesure et diffusion publicitaire (Meta Pixel).</li>
</ul>
<p>Certains de ces prestataires sont susceptibles de transférer des données hors de l'Union européenne. Ces
transferts sont encadrés par les clauses contractuelles types de la Commission européenne et, le cas échéant,
par le Data Privacy Framework.</p>

<h2>Durée de conservation</h2>
<ul>
  <li>Prospects n'ayant pas donné suite : <b>3 ans</b> à compter du dernier contact ;</li>
  <li>Clients : durée de la relation commerciale, puis <b>3 ans</b> à compter du dernier contact, sans préjudice
      des obligations légales de conservation comptable ;</li>
  <li>Données de cookies : <b>13 mois maximum</b>.</li>
</ul>

<h2>Vos droits</h2>
<p>Vous disposez d'un droit d'accès, de rectification, d'effacement, de limitation, d'opposition, de portabilité,
ainsi que du droit de retirer votre consentement à tout moment et de définir des directives relatives au sort de
vos données après votre décès.</p>
<p>Pour exercer ces droits, écrivez à <a href="mailto:{MAIL}">{MAIL}</a>. Une pièce justificative d'identité
pourra être demandée en cas de doute raisonnable sur votre identité. Vous disposez également du droit d'introduire
une réclamation auprès de la <a href="https://www.cnil.fr" target="_blank" rel="noopener">CNIL</a>.</p>

<h2>Cookies</h2>
<p>Le site dépose des cookies nécessaires à son fonctionnement, ainsi que — sous réserve de votre consentement —
des cookies de mesure d'audience et de publicité (Google Analytics, Google Ads, Meta Pixel), déployés via Google
Tag Manager. Vous pouvez à tout moment modifier vos préférences depuis le bandeau de gestion des cookies ou les
paramètres de votre navigateur.</p>
{TODO.format("installer un bandeau de consentement (CMP) conforme aux recommandations CNIL, qui bloque le dépôt des cookies Google Analytics, Google Ads et Meta Pixel <b>avant</b> le recueil du consentement. Sans cela, le déclenchement actuel de GTM et du Pixel dès le chargement de la page n’est pas conforme.")}

<h2>Sécurité</h2>
<p>Nous mettons en œuvre des mesures techniques et organisationnelles appropriées pour protéger vos données contre
la destruction, la perte, l'altération, la divulgation ou l'accès non autorisés : connexion chiffrée (HTTPS),
accès restreints et authentifiés aux outils, journalisation.</p>

<h2>Mise à jour</h2>
<p>La présente politique peut être modifiée pour tenir compte des évolutions légales ou techniques.
Dernière mise à jour : juillet 2026.</p>
""")

CGV = legal_page('/cgv',
 'Conditions générales de vente | MAbeautyplus',
 'Conditions générales de vente des prestations de bien-être et d\'esthétique MAbeautyplus : réservation, '
 'paiement, annulation et réclamations.',
 'Conditions générales de vente', 'Nos conditions', f"""
{TODO.format("ces CGV sont un socle à adapter à ta réalité commerciale (modalités de paiement, échelonnement, durée de validité des cures, politique d’annulation réelle). <b>Fais-les relire par un juriste avant mise en ligne</b> : ce document engage ta responsabilité contractuelle.")}

<h2>Article 1 — Objet et champ d'application</h2>
<p>Les présentes conditions générales de vente régissent les relations entre MAbeautyplus et toute personne
physique majeure souscrivant une prestation dans l'un de ses centres. Toute souscription implique l'acceptation
sans réserve des présentes conditions.</p>

<h2>Article 2 — Nature des prestations</h2>
<p>Les prestations proposées relèvent du bien-être et de l'esthétique. Elles ne constituent ni un traitement
médical, ni un acte thérapeutique, ni un diagnostic, et ne se substituent pas à un suivi médical. Il appartient
au client d'informer le centre de toute pathologie, traitement en cours ou contre-indication susceptible de
s'opposer à la réalisation d'une prestation.</p>

<h2>Article 3 — Analyse préalable</h2>
<p>Toute prestation est précédée d'une analyse de composition corporelle et d'un entretien, réalisés à titre
gracieux et sans engagement. Cette analyse permet de déterminer si un accompagnement est pertinent et, le cas
échéant, d'en définir le contenu, la durée et la fréquence.</p>

<h2>Article 4 — Formation du contrat et tarifs</h2>
<p>Les tarifs applicables sont communiqués au client à l'issue de l'analyse préalable, avant toute souscription,
et font l'objet d'un document écrit remis au client. Ils s'entendent en euros, toutes taxes comprises.</p>
{TODO.format('préciser ici les modalités : paiement comptant, échelonné, moyens acceptés, et la durée de validité des séances souscrites.')}

<h2>Article 5 — Droit de rétractation</h2>
<p>Les prestations souscrites sur place, dans le centre, ne relèvent pas du droit de rétractation applicable à la
vente à distance. Lorsqu'un contrat est conclu à distance ou hors établissement, le client dispose d'un délai de
quatorze (14) jours pour se rétracter, conformément aux articles L.221-18 et suivants du Code de la consommation,
sauf exécution de la prestation entamée avec son accord exprès avant l'expiration de ce délai.</p>

<h2>Article 6 — Rendez-vous, retard et annulation</h2>
<p>Les rendez-vous sont nominatifs. Toute annulation doit être signalée au moins <b>24 heures</b> à l'avance,
par téléphone au {TEL}. Un rendez-vous annulé tardivement ou non honoré pourra être décompté du forfait souscrit.
En cas de retard, la prestation pourra être écourtée afin de ne pas décaler les rendez-vous suivants.</p>

<h2>Article 7 — Interruption de l'accompagnement</h2>
<p>En cas de survenance d'une contre-indication médicale dûment justifiée en cours d'accompagnement, les séances
non consommées pourront être suspendues ou remboursées au prorata, sur présentation d'un certificat médical.</p>

<h2>Article 8 — Résultats</h2>
<p>Les prestations constituent une obligation de moyens et non de résultat. Les résultats observés varient selon
les personnes, leur physiologie, leur assiduité et le respect des recommandations formulées lors de
l'accompagnement.</p>

<h2>Article 9 — Responsabilité</h2>
<p>MAbeautyplus ne saurait être tenu responsable des conséquences résultant d'informations inexactes ou
incomplètes communiquées par le client, notamment concernant son état de santé, ses traitements ou ses
antécédents.</p>

<h2>Article 10 — Données personnelles</h2>
<p>Les données collectées sont traitées conformément à notre
<a href="/politique-de-confidentialite">politique de confidentialité</a>.</p>

<h2>Article 11 — Réclamations et médiation</h2>
<p>Toute réclamation peut être adressée à <a href="mailto:{MAIL}">{MAIL}</a>. Conformément à l'article L.612-1 du
Code de la consommation, le client peut recourir gratuitement à un médiateur de la consommation en vue de la
résolution amiable d'un litige.</p>
{TODO.format("indiquer le nom et les coordonnées du médiateur de la consommation auquel tu adhères. L’adhésion à un dispositif de médiation est <b>obligatoire</b> pour tout professionnel vendant à des consommateurs.")}

<h2>Article 12 — Droit applicable</h2>
<p>Les présentes conditions sont soumises au droit français.</p>
""")

# ═══════════════════════════════════════════════════════════════
#  ASSEMBLAGE
# ═══════════════════════════════════════════════════════════════
def render(page):
    head = (HEAD_TPL
        .replace('{{TITLE}}', page['title'])
        .replace('{{DESC}}', page['desc'])
        .replace('{{OGDESC}}', page.get('ogdesc', page['desc']))
        .replace('{{PATH}}', page['path'] if page['path'] != '/' else '/')
        .replace('{{EXTRA_HEAD}}', ''))
    head = head + '<style>\n' + BASE_CSS + EXTRA_CSS + '</style>\n'
    jsonld = ''
    if page.get('jsonld_raw'):
        jsonld = '<script type="application/ld+json">' + page['jsonld_raw'] + '</script>\n'
    elif page.get('jsonld'):
        jsonld = ('<script type="application/ld+json">'
                  + json.dumps(page['jsonld'], ensure_ascii=False, indent=1) + '</script>\n')
    return head + MID + HEADER + page['body'] + FOOTER + jsonld + SCRIPTS

def write(page):
    p = page['path']
    out = os.path.join(DIST, 'index.html') if p == '/' else os.path.join(DIST, p.strip('/'), 'index.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(render(page))
    return out

def main():
    if os.path.isdir(DIST): shutil.rmtree(DIST)
    os.makedirs(DIST, exist_ok=True)

    pages = [
      dict(path='/',
           title="MAbeautyplus | La méthode d'accompagnement global du corps et du bien-être",
           desc="MAbeautyplus n'est ni un centre minceur classique, ni un institut de soins isolés. C'est une "
                "méthode d'accompagnement global : analyse de composition corporelle, programme sur-mesure et "
                "suivi humain, dans 5 centres du Sud de la France.",
           ogdesc="On ne traite pas un symptôme. On accompagne une personne.",
           body=read('pages/index.body.html'), jsonld_raw=read('pages/index.jsonld.json')),
      page_centres_hub(),
      *[page_centre(c) for c in CENTRES],
      page_avis(), page_contact(), MENTIONS, CONFID, CGV,
    ]
    # le JSON-LD global de l'accueil est déjà dans index.body ? non : on le réinjecte
    for pg in pages:
        print('→', write(pg).replace(ROOT + '/', ''))

    # sitemap
    urls = ''.join(f'  <url><loc>https://www.mabeautyplus.fr{p["path"]}</loc>'
                   f'<changefreq>monthly</changefreq><priority>{"1.0" if p["path"]=="/" else "0.8"}</priority></url>\n'
                   for p in pages)
    open(os.path.join(DIST, 'sitemap.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '</urlset>\n')
    open(os.path.join(DIST, 'robots.txt'), 'w', encoding='utf-8').write(
        'User-agent: *\nAllow: /\n\nSitemap: https://www.mabeautyplus.fr/sitemap.xml\n')
    print(f'\n{len(pages)} pages générées + sitemap.xml + robots.txt')

if __name__ == '__main__':
    main()
