#!/usr/bin/env python3
"""
OCHO HERRENTOUR — ATHEN 2026
Static Web-App & KML Generator (build.py)
Reads 00_Athen_Master_Context.md + dossiers/01..26.md + images/
and compiles index.html + ochos_athen_2026.kml
"""
import glob
import html
import json
import math
import os
import re
import markdown

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOSSIERS_DIR = os.path.join(BASE_DIR, "dossiers")
IMAGES_DIR = os.path.join(BASE_DIR, "images")

HOME_BASE = {
    "name": "ATHINUM 1 | HOME BASE",
    "subtitle": "Korinnis 11 (Ecke Platia Eleftherias / Koumoundourou)",
    "address": "Korinnis 11, 105 53 Athen",
    "lat": 37.98067,
    "lng": 23.72257,
    "gmaps": "https://www.google.com/maps/place/ATHINUM+1+%7C+by+Valenci/@37.9806589,23.7223653,61m/data=!3m1!1e3!4m6!3m5!1s0x14a1bd007b9342ff:0x8d7f2bb0512213cf!8m2!3d37.9806698!4d23.7225669!16s%2Fg%2F11xz165djq"
}

# Curated tactical metadata + exact coordinates for all 26 dossiers
SPOT_META = {
    1: {
        "short_title": "BIOS",
        "subtitle": "Industrial-Kulturzentrum & Unprätentiöses Akropolis-Rooftop",
        "district": "Psyri / West",
        "district_tag": "psyri",
        "cats": ["rooftop", "late", "drinks"],
        "cat_label": "ROOFTOP / LATE NIGHT",
        "address": "Pireos 84, 104 35 Athen",
        "walk_min": 5,
        "walk_text": "400 m · 5 Min.",
        "hours_short": "Tägl. 10:00–02:00 (Fr/Sa bis 03:00)",
        "food_status": "SNACKS ONLY",
        "food_note": "Reine Bar — kein Abendessen (nur Bar-Snacks)",
        "signature": "Papoto-Slush (Eis am Stiel im Cocktailglas) & kaltes Fassbier",
        "insider": "Eingang um die Ecke auf der Salaminos 13 nutzen · Aufzug direkt in den 2. Stock / aufs Dach · Liegestühle mit unverbautem Blick auf die beleuchtete Akropolis.",
        "lat": 37.97918,
        "lng": 23.71915,
    },
    2: {
        "short_title": "UPUPA EPOPS",
        "subtitle": "Theatrale Vintage-Cocktailbar & Begrünter 1930er-Innenhof",
        "district": "Petralona",
        "district_tag": "petralona",
        "cats": ["cocktails", "daydrinking", "food"],
        "cat_label": "COCKTAILS / HOF & BARFOOD",
        "address": "Alkminis 7, 118 54 Kato Petralona",
        "walk_min": 20,
        "walk_text": "1,6 km · 20 Min.",
        "hours_short": "Tägl. 10:00–02:00 (Fr/Sa bis 03:00)",
        "food_status": "BARFOOD / PIZZA",
        "food_note": "Starkes Barfood & Sauerteig-Pizza (Küche bis 00:30)",
        "signature": "Upupa Epops Signature Cocktail & Trüffel-Pilz-Pinsa",
        "insider": "Drei zusammengefügte 1930er-Steinhäuser · Perfekt als Start der Donnerstag-West-Linie vor Line Athens (nur 400 m weiter).",
        "lat": 37.97152,
        "lng": 23.71184,
    },
    3: {
        "short_title": "LINE ATHENS",
        "subtitle": "Weltklasse-Avantgarde-Bar (#6 World's 50 Best Bars) & In-House-Fermentation",
        "district": "Petralona",
        "district_tag": "petralona",
        "cats": ["cocktails", "food", "late"],
        "cat_label": "WORLD'S 50 BEST / AVANTGARDE",
        "address": "Agathodaimonos 37, 118 53 Kato Petralona",
        "walk_min": 22,
        "walk_text": "1,7 km · 22 Min.",
        "hours_short": "Mo–Do 17:00–02:00 · Fr 17:00–03:00 · Sa/So ab 10:30",
        "food_status": "GASTRO BARFOOD",
        "food_note": "Hauseigene Sauerteig-Bäckerei & Zero-Waste-Gerichte",
        "signature": "Hauseigene Fruchtweine ('Why Not' Erdbeer/Feige/Granatapfel) & 'Line's Hot Dog'",
        "insider": "Ehemalige Kunstgalerie in alter Fabrik · Ab 21:30 Uhr legt der DJ auf · 5 Min. Fußweg von Upupa Epops.",
        "lat": 37.96885,
        "lng": 23.70995,
    },
    4: {
        "short_title": "TAF (THE ART FOUNDATION)",
        "subtitle": "Versteckter Hinterhof von 1870, Kunstgalerie & Kult-Bar",
        "district": "Monastiraki / Psyri",
        "district_tag": "monastiraki",
        "cats": ["daydrinking", "cocktails", "late"],
        "cat_label": "HIDDEN COURTYARD / ART BAR",
        "address": "Normanou 5, 105 55 Monastiraki",
        "walk_min": 10,
        "walk_text": "800 m · 10 Min.",
        "hours_short": "Mo–Do 11:00–02:00 · Fr/Sa bis 03:00",
        "food_status": "DRINKS ONLY",
        "food_note": "Reine Bar & Café — vorab in Psyri essen!",
        "signature": "Freddo Espresso tagsüber · Klassische Highballs & Gin-Drinks nachts",
        "insider": "Durch den dunklen Torbogen auf der Flohmarktgasse Normanou 5 gehen · Couleur Locale ist direkt im Gebäude daneben (Normanou 3)!",
        "lat": 37.97622,
        "lng": 23.72438,
    },
    5: {
        "short_title": "COULEUR LOCALE",
        "subtitle": "Verstecktes Panorama-Rooftop mit Frontalblick auf die Akropolis",
        "district": "Monastiraki",
        "district_tag": "monastiraki",
        "cats": ["rooftop", "daydrinking", "cocktails"],
        "cat_label": "ROOFTOP / SUNSET VIEW",
        "address": "Normanou 3, 105 55 Monastiraki",
        "walk_min": 10,
        "walk_text": "800 m · 10 Min.",
        "hours_short": "Tägl. 09:30–02:00 (Fr/Sa bis 03:00)",
        "food_status": "BRUNCH & BARFOOD",
        "food_note": "Brunch bis 18:00, danach Burger/Pinsa/Fingerfood",
        "signature": "Mediterranean Mule & Akropolis-Sundowner um 17:00 Uhr",
        "insider": "In die unscheinbare Ladenpassage Normanou 3 hineingehen und den Aufzug in den 3. Stock nehmen · Im November mit Glas-Windschutz & Heizstrahlern.",
        "lat": 37.97628,
        "lng": 23.72452,
    },
    6: {
        "short_title": "360 COCKTAIL BAR",
        "subtitle": "Mehrstöckiger Industrial-Dachgarten direkt über dem Monastiraki-Platz",
        "district": "Monastiraki",
        "district_tag": "monastiraki",
        "cats": ["rooftop", "cocktails", "daydrinking"],
        "cat_label": "ROOFTOP GARDEN / BAR",
        "address": "Ifestou 2, 105 55 Monastiraki",
        "walk_min": 10,
        "walk_text": "820 m · 10 Min.",
        "hours_short": "Tägl. 09:00–03:00 (Fr/Sa bis 04:00)",
        "food_status": "FULL RESTAURANT",
        "food_note": "Vollwertige Küche, Sushi & Barfood",
        "signature": "360 Passion & Mastiha-Cocktails an der zentralen 360°-Insel-Theke",
        "insider": "Für 8 Personen nach den langen Hochtischen an der offenen Bar fragen (ohne Restaurant-Reservierungszwang).",
        "lat": 37.97621,
        "lng": 23.72548,
    },
    7: {
        "short_title": "THE CLUMSIES",
        "subtitle": "Neoklassizistische Weltklasse-All-Day-Bar (#60 World's 50 Best)",
        "district": "Zentrum / Psyri",
        "district_tag": "zentrum",
        "cats": ["cocktails", "daydrinking", "late"],
        "cat_label": "WORLD'S 50 BEST / HOUSE PARTY",
        "address": "Praxitelous 30, 105 61 Athen",
        "walk_min": 9,
        "walk_text": "750 m · 9 Min.",
        "hours_short": "Tägl. 10:00–02:00 (Fr/Sa bis 04:00)",
        "food_status": "BRUNCH & BARFOOD",
        "food_note": "Starker Brunch & gehobenes Barfood (Küche bis 23:30)",
        "signature": "Aegean Negroni (mit Fenchel, Mastiha & Diktamos) & Popeye Smash",
        "insider": "Donnerstagabend (19–21:30 Uhr) entspannt ohne Türsteher-Schlange · Im überdachten Innenhof oder an der langen Holztheke stehen.",
        "lat": 37.97896,
        "lng": 23.72942,
    },
    8: {
        "short_title": "BABA AU RUM",
        "subtitle": "Athens Rum- & Tiki-Tempel (#14 Europe's 50 Best Bars 2026)",
        "district": "Zentrum",
        "district_tag": "zentrum",
        "cats": ["cocktails", "late"],
        "cat_label": "EUROPE'S 50 BEST / RUM & TIKI",
        "address": "Klitiou 6, 105 60 Athen",
        "walk_min": 11,
        "walk_text": "850 m · 11 Min.",
        "hours_short": "So–Fr 19:00–03:00 · Sa 19:00–03:30",
        "food_status": "DRINKS ONLY",
        "food_note": "Reine Cocktailbar (nur Nüsse/Oliven)",
        "signature": "Baba Zombie, Mai Tai nach 1944er-Originalrezept & Spicy Baba",
        "insider": "Bei 8 Leuten stellt man sich abends lässig an die Stehtische auf der Fußgängerzone Klitiou · Nur 90 m neben The Bar in Front of the Bar!",
        "lat": 37.97748,
        "lng": 23.72985,
    },
    9: {
        "short_title": "THE BAR IN FRONT OF THE BAR",
        "subtitle": "Street-Cocktail-Phänomen & Speakeasy (#2 Europe's 50 Best Bars 2026)",
        "district": "Zentrum",
        "district_tag": "zentrum",
        "cats": ["cocktails", "late"],
        "cat_label": "#2 EUROPE'S 50 BEST / STREET BAR",
        "address": "Petraki 1, 105 63 Athen",
        "walk_min": 12,
        "walk_text": "950 m · 12 Min.",
        "hours_short": "Tägl. 18:00–02:00/03:00",
        "food_status": "DRINKS ONLY",
        "food_note": "Reine Cocktailbar — Street-Drinking-Konzept",
        "signature": "Jeden Tag komplett neue 8-Drinks-Karte aus auf -24 °C gefrosteten Gläsern",
        "insider": "2-in-1-Spot: Vorne auf der Fußgängerzone Petraki für große Gruppen perfekt im Stehen · Hinter der verspiegelten Tür versteckt sich das Speakeasy 'Rumble in the Jungle'.",
        "lat": 37.97654,
        "lng": 23.73162,
    },
    10: {
        "short_title": "BARRO NEGRO",
        "subtitle": "Athens 1. Tequilaria, Mezcaleria & Paloma Embassy (#13 Europe's 50 Best)",
        "district": "Zentrum",
        "district_tag": "zentrum",
        "cats": ["cocktails", "late"],
        "cat_label": "EUROPE'S 50 BEST / AGAVE & PALOMA",
        "address": "Ioannou Paparrigopoulou 15, 105 61 Athen",
        "walk_min": 10,
        "walk_text": "800 m · 10 Min.",
        "hours_short": "Mo–Do 18:00–02:00 · Fr 18:00–03:00 · Sa/So ab 16:00",
        "food_status": "DRINKS ONLY",
        "food_note": "Reine Agaven-Cocktailbar",
        "signature": "Barro Negro Paloma (11 €), Mezcal Negroni & Michelada (7 €)",
        "insider": "Direkt neben Black Duck Garden und nur 100 m von The Clumsies — ideal für ein schnelles Cocktail-Hopping.",
        "lat": 37.97938,
        "lng": 23.73082,
    },
    11: {
        "short_title": "BLACK DUCK GARDEN",
        "subtitle": "Geheimer Palmen-Innenhof von 1836 im Museum der Stadt Athen",
        "district": "Zentrum",
        "district_tag": "zentrum",
        "cats": ["daydrinking", "food", "cocktails"],
        "cat_label": "GARDEN OASIS / BISTRO & BAR",
        "address": "Ioannou Paparrigopoulou 5–7, 105 61 Athen",
        "walk_min": 10,
        "walk_text": "820 m · 10 Min.",
        "hours_short": "Tägl. 10:00–01:00 (Fr/Sa bis 02:00)",
        "food_status": "BISTRO & PLATTERS",
        "food_note": "All-Day-Bistro, Käse-/Charcuterie-Platten & Brunch",
        "signature": "Wein-/Käseplatte unter dem historischen Königin-Amalia-Palmenbaum",
        "insider": "Perfekter erster Landeplatz am Donnerstagnachmittag (16:30 Uhr) zum Runterkommen nach dem Flug.",
        "lat": 37.97912,
        "lng": 23.73118,
    },
    12: {
        "short_title": "TALES OF ALES (+ CRAFT BEER TRIO)",
        "subtitle": "10 rotierende Craft-Beer-Taps & 170+ griechische Mikrobrauerei-Dosen",
        "district": "Zentrum",
        "district_tag": "zentrum",
        "cats": ["beer", "daydrinking", "late"],
        "cat_label": "CRAFT BEER / TAPROOM",
        "address": "Miltiadou 19, 105 60 Athen (+ Brew Str & Strange Brew)",
        "walk_min": 8,
        "walk_text": "750 m · 8 Min.",
        "hours_short": "Mo–Do 14:00–01:00 · Fr/Sa 14:00–02:00 · So 17:00–01:00",
        "food_status": "STREETFOOD NEXT DOOR",
        "food_note": "Gegenüber auf Miltiadou 12 Smash-Burger holen & zum Bier essen!",
        "signature": "Strange Brew 'Jasmine IPA', Seven Seals & Kykao vom Fass",
        "insider": "Liegt mitten im Bermudadreieck zwischen Clumsies (90 m) und Baba au Rum (140 m) — der beste Zwischenstopp für ein ehrliches IPA.",
        "lat": 37.97822,
        "lng": 23.72968,
    },
    13: {
        "short_title": "AVLI PSYRRI",
        "subtitle": "Verstecktes weiß-blaues Hinterhof-Kafeneio (seit 1985 unter Herr Takis)",
        "district": "Psyri (Home-Kiez)",
        "district_tag": "psyri",
        "cats": ["food", "daydrinking"],
        "cat_label": "HIDDEN COURTYARD / MEZEDOPOLEIO",
        "address": "Agiou Dimitriou 12, 105 54 Psyri",
        "walk_min": 5,
        "walk_text": "550 m · 5 Min.",
        "hours_short": "Mi–Mo 13:00–02:00 (Di geschlossen)",
        "food_status": "FULL MEZE TABLE",
        "food_note": "Ehrliche Pfannen-Meze für 4–7 € pro Teller!",
        "signature": "Tigania (Schweinefleisch aus der Gusseisenpfanne), Keftedes & Tsipouro",
        "insider": "WICHTIG: Eingang durch die schmale blaue Eisentür auf der Agiou Dimitriou 12 (nicht Agion Anargyron!) · Keine Reservierung, Cash mitnehmen.",
        "lat": 37.97815,
        "lng": 23.72555,
    },
    14: {
        "short_title": "AMA LACHEI (STIS NEFELIS)",
        "subtitle": "Modern-Greek-Mezedopoleio im begrünten Pausenhof einer alten Grundschule",
        "district": "Exarchia",
        "district_tag": "exarchia",
        "cats": ["food", "daydrinking"],
        "cat_label": "MEZE / SCHOOLYARD GARDEN",
        "address": "Kallidromiou 69, 106 83 Exarchia",
        "walk_min": 22,
        "walk_text": "1,9 km · 22 Min. (6 Min. Uber)",
        "hours_short": "Mo–Mi 12:00–23:30 · Do–So 12:00–00:00",
        "food_status": "FULL MEZE FEAST",
        "food_note": "Große griechisch-kretische Sharing-Tafel (auch innen in den alten Klassenzimmern)",
        "signature": "Mastelo-Grillkäse mit Tomatenmarmelade, Apaki & geschmortes Lamm",
        "insider": "Pflicht-Stopp nach dem Samstagsmarkt auf der Kallidromiou · Für 8 Personen am Wochenende kurz telefonisch reservieren (+30 210 3845978).",
        "lat": 37.98692,
        "lng": 23.73815,
    },
    15: {
        "short_title": "PHARAOH",
        "subtitle": "Michelin Bib Gourmand Holzfeuer-Küche, 400+ Naturweine & Vinyl-HiFi-Bar",
        "district": "Exarchia",
        "district_tag": "exarchia",
        "cats": ["food", "wine", "late"],
        "cat_label": "WOODFIRE / NATURAL WINE & VINYL",
        "address": "Solomou 54, 106 82 Exarchia",
        "walk_min": 13,
        "walk_text": "1,2 km · 13 Min.",
        "hours_short": "Mo–Do 17:30–02:00 · Fr/Sa 13:30–02:00 (So zu!)",
        "food_status": "MICHELIN WOODFIRE",
        "food_note": "Alles über offenem Olivenholzfeuer & in Holzöfen gegart",
        "signature": "Sauerteigbrot mit geräucherter Butter, Hortopita aus dem Holzofen & griechischer Naturwein",
        "insider": "Falls Tische ausgebucht sind: Ab 21:30 Uhr Walk-in an der breiten Edelstahl-Theke direkt vor dem Vinyl-DJ und dem offenen Feuer!",
        "lat": 37.98542,
        "lng": 23.72995,
    },
    16: {
        "short_title": "TANINI AGAPI MOU",
        "subtitle": "Unprätentiöse Griechische Naturwein-Bar (100+ Weine offen & Wine on Tap)",
        "district": "Exarchia",
        "district_tag": "exarchia",
        "cats": ["wine", "daydrinking", "late"],
        "cat_label": "NATURAL WINE BAR / ZERO SNOBBERY",
        "address": "Ippokratous 91 & Methonis, 106 80 Exarchia",
        "walk_min": 22,
        "walk_text": "1,9 km · 22 Min.",
        "hours_short": "So–Do 17:00–01:00 · Fr/Sa 17:00–02:00",
        "food_status": "PINSA & PLATTERS",
        "food_note": "Knusprige Sauerteig-Pinsa & griechische Käse-/Wurstplatten",
        "signature": "Orange Wine vom Fass (6,50 €), Xinomavro-Flight & Trüffel-Pinsa",
        "insider": "Jede der 100+ Flaschen wird auch glasweise ausgeschenkt! Unten im Gewölbekeller gibt es einen Vinyl-Listening-Raum.",
        "lat": 37.98562,
        "lng": 23.73992,
    },
    17: {
        "short_title": "ROZALIA EXARCHIA",
        "subtitle": "Kult-Taverne seit 1978 mit 16er-Vorspeisen-Tablett & überdachtem Gartenhof",
        "district": "Exarchia",
        "district_tag": "exarchia",
        "cats": ["food", "late"],
        "cat_label": "CLASSIC TAVERNA / MEZE TRAY",
        "address": "Valtetsiou 54–59, 106 81 Exarchia",
        "walk_min": 19,
        "walk_text": "1,7 km · 19 Min.",
        "hours_short": "Tägl. 12:00–01:00 (Fr/Sa bis 02:00)",
        "food_status": "FULL TAVERNA",
        "food_note": "Küche bis nach Mitternacht — perfekt für 8 hungrige Männer",
        "signature": "Vorspeisen-Auswahl direkt vom großen 16-Teller-Silbertablett am Tisch + Lamm im Pergament",
        "insider": "Belegt auf der Fußgängerzone Valtetsiou beide Straßenseiten · Nur 60 m neben strakastrüka und 140 m neben Warehouse Exarchia!",
        "lat": 37.98578,
        "lng": 23.73512,
    },
    18: {
        "short_title": "STRAKASTRÜKA & SPIRTO (LATE NIGHT)",
        "subtitle": "Rock- & Craft-Beer-Joint (Andrea Metaxa 19) + Exarchia-Spätnacht-Achse",
        "district": "Exarchia",
        "district_tag": "exarchia",
        "cats": ["beer", "late", "cocktails"],
        "cat_label": "CRAFT BEER / ROCK & LATE NIGHT",
        "address": "Andrea Metaxa 19 & Tzavella 9–13, Exarchia",
        "walk_min": 19,
        "walk_text": "1,7 km · 19 Min.",
        "hours_short": "strakastrüka bis 01:00/03:00 · Spirto bis 03:00/05:00",
        "food_status": "HOT DOGS & BARFOOD",
        "food_note": "Legendärer 'Straka Hot Dog' zum Craft Beer",
        "signature": "9 griechische Craft-Taps bei strakastrüka + Absacker bis 4 Uhr morgens im Spirto",
        "insider": "WICHTIG: strakastrüka sitzt auf der Andrea Metaxa 19 (Ecke Valtetsiou, nicht Nr. 2!) · Danach 2 Min. rüber auf die Koletti-/Tzavella-Achse.",
        "lat": 37.98595,
        "lng": 23.73475,
    },
    19: {
        "short_title": "KLIMATARIA",
        "subtitle": "Historische Weinfass-Taverne seit 1927 mit Gastra-Schmortöpfen & Live-Rembetiko",
        "district": "Psyri / Markt (Home-Kiez)",
        "district_tag": "psyri",
        "cats": ["food", "wine"],
        "cat_label": "1927 TAVERNA / LIVE REMBETIKO",
        "address": "Platia Theatrou 2, 105 52 Athen",
        "walk_min": 2,
        "walk_text": "180 m · 2 Min.!",
        "hours_short": "Di–So 12:00–01:00/02:00 (Mo geschlossen)",
        "food_status": "FULL FEAST / GASTRA",
        "food_note": "Stundenlang geschmorte Schweinshaxe & Lamm aus dem Gastra-Topf",
        "signature": "Kotsi (Schweinshaxe) & Lamm mit Zitronenkartoffeln + Fasswein zwischen riesigen Holzfässern",
        "insider": "Nur 180 Meter von eurer Haustür! Komplett überdachter & beheizter Hof · Do/Fr/Sa Abend & So Mittag Live-Bouzouki-Musik.",
        "lat": 37.98042,
        "lng": 23.72485,
    },
    20: {
        "short_title": "DIPORTO",
        "subtitle": "Legendäre schilderlose Untergrund-Kellertaverne von 1887 (Nur tagsüber!)",
        "district": "Psyri / Markt (Home-Kiez)",
        "district_tag": "psyri",
        "cats": ["food", "daydrinking"],
        "cat_label": "1887 CELLAR CULT / LUNCH ONLY",
        "address": "Sokratous 9 & Theatrou, 105 52 Athen",
        "walk_min": 2,
        "walk_text": "200 m · 2 Min.!",
        "hours_short": "Mo–Sa ca. 10:00–18:00 (So geschlossen)",
        "food_status": "NO-MENU LUNCH",
        "food_note": "Keine Karte: Es kommt auf den Tisch, was morgens gekocht wurde",
        "signature": "Revithia (Kichererbseneintopf), gebratene Sardinen, Fava & kühler Fass-Retsina im Blechkrug",
        "insider": "Durch eine der zwei unbeschilderten Holztüren die steile Steintreppe in den Keller hinabsteigen · Cash only · Perfekter Mittags-Quickie!",
        "lat": 37.98035,
        "lng": 23.72512,
    },
    21: {
        "short_title": "TA KARAMANLIDIKA TOU FANI",
        "subtitle": "Byzantinisch-Anatolisches Feinkost-Mezedopolio & Pastirma-Himmel",
        "district": "Psyri / Markt (Home-Kiez)",
        "district_tag": "psyri",
        "cats": ["food", "daydrinking", "wine"],
        "cat_label": "BYZANTINE DELI & MEZEDOPOLIO",
        "address": "Sokratous 1 & Evripidou 52 (+ Ermou 119)",
        "walk_min": 4,
        "walk_text": "300 m · 4 Min.",
        "hours_short": "Sokratous: Mo–Sa 12–23 · Ermou 119: Mo–So 12–23!",
        "food_status": "FULL MEZE & DELI",
        "food_note": "Gusseisenpfannen, gereifte Würste, Käse & Gratis-Karottenhalva",
        "signature": "Sahanaki Karamanlidiko (Pastirma, Sudjuk & Bio-Spiegeleier in der Pfanne) + gereifter Tsipouro",
        "insider": "Stammhaus Sokratous 1 ist sonntags zu, aber das Schwesterhaus 'Ergastiri' auf der Ermou 119 (350 m ab Apartment) hat auch sonntags offen!",
        "lat": 37.98018,
        "lng": 23.72615,
    },
    22: {
        "short_title": "FEYROUZ",
        "subtitle": "Levantinisch-Anatolischer Streetfood-Kult (Handgerolltes Steinofen-Lahmacun)",
        "district": "Zentrum / Monastiraki",
        "district_tag": "zentrum",
        "cats": ["food", "daydrinking"],
        "cat_label": "LEVANTINE STREETFOOD / BAKERY",
        "address": "Karori 23 & Agathonos 1, 105 51 Athen",
        "walk_min": 8,
        "walk_text": "650 m · 8 Min.",
        "hours_short": "Mo–Do 12:00–22:00 · Fr/Sa 12:00–23:00 (So zu)",
        "food_status": "BEST STREETFOOD",
        "food_note": "Perfekte schnelle Unterlage (5,50–5,80 €) vor den Cocktailbars",
        "signature": "Feyrouz Lahmacun (mit geräuchertem Babaganoush!), Pastirma-Peinirli & heißes Künefe gegenüber",
        "insider": "Liegt nur 160 m neben The Clumsies & Tales of Ales — ideal als 20-Minuten-Boxenstopp vor der großen Cocktailrunde.",
        "lat": 37.97762,
        "lng": 23.72812,
    },
    23: {
        "short_title": "BOLIVAR BEACH CLUB",
        "subtitle": "Palmen-Landzunge & Strandpromenade an der Athener Riviera (Alimos)",
        "district": "Riviera (Alimos)",
        "district_tag": "riviera",
        "cats": ["riviera", "daydrinking", "food"],
        "cat_label": "RIVIERA PENINSULA / BEACH WALK",
        "address": "Akti tou Iliou, 174 55 Alimos",
        "walk_min": 14,
        "walk_text": "10,6 km · 14 Min. Uber",
        "hours_short": "So–Do 08:00–20:00 · Fr/Sa 08:00–05:00",
        "food_status": "BEACH RESTAURANT",
        "food_note": "Überdachter Holz-Pavillon mit Meeresfrüchten, Burger & Sushi",
        "signature": "Spaziergang über die Landzunge + Freddo Cappuccino oder erster Cocktail direkt am Meer",
        "insider": "Im November kein Badewetter: Erst im Bolivar bei Herbstsonne über die Landzunge schlendern, dann zum Sunset 250 m weiter ins wetterfeste Peñarrubia!",
        "lat": 37.90785,
        "lng": 23.71312,
    },
    24: {
        "short_title": "PEÑARRUBIA LOUNGE",
        "subtitle": "365-Tage-Riviera-Flaggschiff mit Sunset-Holzdeck & beheizter Tropen-Lounge",
        "district": "Riviera (Alimos)",
        "district_tag": "riviera",
        "cats": ["riviera", "daydrinking", "food", "cocktails"],
        "cat_label": "RIVIERA SUNSET DECK / ALL-WEATHER",
        "address": "Leof. Poseidonos 20/43, 174 55 Alimos",
        "walk_min": 14,
        "walk_text": "10,4 km · 14 Min. Uber",
        "hours_short": "365 Tage/Jahr · Tägl. 08:30–02:00 (0 € Eintritt)",
        "food_status": "FULL ALL-DAY MENU",
        "food_note": "Brunch bis 14:00, danach Black-Angus-Burger, Pinsa, Steaks & Sushi",
        "signature": "Sunset-Drinks um 17:20 Uhr auf dem Holzdeck direkt über den Wellen",
        "insider": "Euer 100 % wetterfester Küsten-Anker im November (voll verglaster & beheizter Innenbereich falls Seewind aufkommt) · Auf dem Rückweg beim SNFCC halten!",
        "lat": 37.90969,
        "lng": 23.71106,
    },
    25: {
        "short_title": "WAREHOUSE (EXARCHIA & CO2)",
        "subtitle": "Industrial All-Day Specialty-Coffee-, Wein- & Cocktailbar (80+ offene Weine)",
        "district": "Exarchia & Syntagma",
        "district_tag": "exarchia",
        "cats": ["wine", "cocktails", "food", "daydrinking"],
        "cat_label": "WINE GIANT / ALL-DAY BISTRO",
        "address": "Valtetsiou 21, Exarchia (+ Ypereidou 1, Syntagma)",
        "walk_min": 18,
        "walk_text": "1,6 km · 18 Min.",
        "hours_short": "Tägl. 09:00–02:30 (Küche bis 23:30)",
        "food_status": "GASTRO BISTRO",
        "food_note": "Gehobene Sharing-Küche, Burrata mit Avgotaracho & frische Pasta",
        "signature": "Weinverkostung nach Glas (80+ offene Positionen) & Spritz/Pet-Nat in der Fußgängerzone",
        "insider": "Sitzt direkt am Eingang der Fußgängerzone Valtetsiou (nur 140 m vor Rozalia & strakastrüka) · Perfekter Aperitivo-Stopp in Exarchia.",
        "lat": 37.98448,
        "lng": 23.73488,
    },
    26: {
        "short_title": "FRÜHSTÜCK & KATER-BRUNCH PSYRI",
        "subtitle": "Minu (2 Min.), Usurum (ab 07:30!), Bougatsadiko, Koulouri & I Stani (seit 1931)",
        "district": "Psyri (Home-Kiez)",
        "district_tag": "psyri",
        "cats": ["breakfast", "food"],
        "cat_label": "MORNING COMPASS / 2–5 MIN WALK",
        "address": "Sarri 50 / Lepeniotou 19 / Platia Iroon 1, Psyri",
        "walk_min": 2,
        "walk_text": "190–450 m · 2–5 Min.!",
        "hours_short": "Usurum ab 07:30 · Minu ab 08:30 · Bäcker ab 06:30",
        "food_status": "FULL BREAKFAST",
        "food_note": "Specialty Coffee, Eggs Benedict, ofenheiße Bougatsa & Schafsjoghurt",
        "signature": "Minu 'Happy Egg Bowl', Usurum 'Shakshuka & Bloody Mary' oder heiße Bougatsa auf die Hand",
        "insider": "Da das Apartment kein Frühstück hat, stolpert ihr aus der Korinnis 11 in 2 Minuten direkt zu Minu (Sarri 50) oder Usurum (Lepeniotou 19).",
        "lat": 37.97925,
        "lng": 23.72318,
    }
}

ROUTES_DATA = [
    {
        "id": "do-a",
        "day": "DONNERSTAG · 05.11.",
        "title": "OPTION A — ZENTRUM & PSYRI ACHSE",
        "subtitle": "Kurze Wege ab Apartment · Touchdown, Weltklasse-Drinks & Hinterhof-Finale",
        "stops": [
            {
                "time": "16:00",
                "name": "TOUCHDOWN @ ATHINUM 1 (KORINNIS 11)",
                "desc": "Check-in im Basecamp. Taschen abwerfen, frisch machen. Optionaler 2-Minuten-Snack bei Feyrouz oder Karamanlidika.",
                "dist": "START · 0 m",
                "spot_id": None
            },
            {
                "time": "16:30 – 19:00",
                "name": "BLACK DUCK GARDEN",
                "desc": "Ankommen im versteckten Palmen-Innenhof des Stadtmuseums. Erste Runde Bier, Wein & Platten unter freiem Himmel.",
                "dist": "820 m · 10 Min. Fußweg ab Apartment",
                "spot_id": 11
            },
            {
                "time": "19:00 – 21:30",
                "name": "THE CLUMSIES (+ BARRO NEGRO / TALES OF ALES)",
                "desc": "Donnerstags entspannter Einlass ohne Wochenend-Schlange. Aegean Negroni an der Holztheke oder im Innenhof (Barro Negro & Tales of Ales liegen 90 m daneben).",
                "dist": "180 m · 2 Min. Fußweg",
                "spot_id": 7
            },
            {
                "time": "21:30 – 23:15",
                "name": "AVLI PSYRRI ODER KLIMATARIA",
                "desc": "Ehrliches Abendessen: Entweder durch die blaue Tür in den weiß-blauen Hof der Avli Psyrri (Pfannen-Meze) oder in die Weinfass-Taverne Klimataria bei Live-Rembetiko.",
                "dist": "350 m · 4 Min. Fußweg",
                "spot_id": 13
            },
            {
                "time": "23:15 – 02:30",
                "name": "TAF (THE ART FOUNDATION) & COULEUR LOCALE",
                "desc": "Finale im historischen Hinterhof von 1870 bei DJ-Sets (oder ein Stockwerk höher auf dem Couleur-Locale-Dach mit beleuchteter Akropolis).",
                "dist": "350 m · 4 Min. Fußweg (danach 10 Min. heim)",
                "spot_id": 4
            }
        ]
    },
    {
        "id": "do-b",
        "day": "DONNERSTAG · 05.11.",
        "title": "OPTION B — WEST-LINIE (PETRALONA & INDUSTRIAL)",
        "subtitle": "Warehouse-Vibe, Fermentation & Akropolis-Nachtblick auf dem Heimweg",
        "stops": [
            {
                "time": "18:00 – 20:30",
                "name": "UPUPA EPOPS (PETRALONA)",
                "desc": "Start im farbenfrohen 1930er-Innenhof. Starke Signature-Cocktails plus Sauerteig-Pizza & Barfood als Grundlage.",
                "dist": "1,6 km · 20 Min. Fußweg oder 5 Min. Uber",
                "spot_id": 2
            },
            {
                "time": "20:30 – 00:30",
                "name": "LINE ATHENS (#6 WORLD'S 50 BEST)",
                "desc": "5 Minuten weiter in die ehemalige Kunstgalerie. Hauseigene Fruchtweine, 'Line's Hot Dog' und ab 21:30 Uhr DJ-Set.",
                "dist": "400 m · 5 Min. Fußweg",
                "spot_id": 3
            },
            {
                "time": "00:30 – 02:00",
                "name": "BIOS ROOFTOP (PIREOS 84)",
                "desc": "Liegt exakt auf dem Rückweg zum Apartment: Letzter Papoto-Slush oder kaltes Bier in den Liegestühlen mit Frontalblick auf die Akropolis.",
                "dist": "1,3 km Richtung Apartment (danach 5 Min. ins Bett)",
                "spot_id": 1
            }
        ]
    },
    {
        "id": "fr-riviera",
        "day": "FREITAG · 06.11.",
        "title": "MARKT, KÜSTEN-SUNSET (ALIMOS) & COCKTAIL-MEILE",
        "subtitle": "Kater-Brunch in Psyri, Meerblick ohne Badewetter & Europe's 50 Best Bars bei Nacht",
        "stops": [
            {
                "time": "09:30 – 11:30",
                "name": "KATER-BRUNCH: MINU ODER USURUM (PSYRI)",
                "desc": "2–3 Minuten aus der Haustür: Specialty Coffee & Eggs im Pflanzen-Hof von Minu (Sarri 50) oder ab 07:30 Uhr im Usurum (Lepeniotou 19).",
                "dist": "190 m · 2 Min. ab Apartment",
                "spot_id": 26
            },
            {
                "time": "12:30 – 14:15",
                "name": "DIPORTO ODER TA KARAMANLIDIKA TOU FANI",
                "desc": "Mittags-Kult direkt neben dem Apartment: Entweder Kichererbsensuppe & Fass-Retsina im 1887er-Keller Diporto oder Pastirma-Pfanne & Tsipouro bei Karamanlidika.",
                "dist": "200 m · 2 Min. ab Apartment",
                "spot_id": 20
            },
            {
                "time": "15:00 – 16:30",
                "name": "BOLIVAR BEACH CLUB (ALIMOS RIVIERA)",
                "desc": "14 Min. per Uber ans Meer. Spaziergang über die Palmen-Landzunge und erster Nachmittags-Drink direkt am Wasser.",
                "dist": "10,6 km · 14 Min. Uber (ca. 12–15 €)",
                "spot_id": 23
            },
            {
                "time": "16:30 – 19:30",
                "name": "PEÑARRUBIA LOUNGE (SUNSET UM 17:20 UHR)",
                "desc": "250 m am Strand entlang zum 100 % wetterfesten Riviera-Flaggschiff. Sundowner auf dem Holzdeck über der Brandung & Comfort Food.",
                "dist": "250 m · 3 Min. zu Fuß am Wasser",
                "spot_id": 24
            },
            {
                "time": "21:30 – 03:00",
                "name": "COCKTAIL-DREIECK: BABA AU RUM & BAR IN FRONT OF THE BAR",
                "desc": "Zurück im Zentrum (optional nach Steinofen-Lahmacun bei Feyrouz): Rum-Klassiker im Baba au Rum (#14 Europa) und Street-Drinks vor The Bar in Front of the Bar (#2 Europa).",
                "dist": "90 m zwischen beiden Bars",
                "spot_id": 9
            }
        ]
    },
    {
        "id": "sa-exarchia",
        "day": "SAMSTAG · 07.11.",
        "title": "EXARCHIA DAY & NIGHT (MARKT, HÖFE, NATURWEIN & ROCK)",
        "subtitle": "Vom berühmten Samstagsmarkt über den Grundschul-Hof bis zum Absacker um 4 Uhr früh",
        "stops": [
            {
                "time": "11:00 – 13:30",
                "name": "KALLIDROMIOU SAMSTAGSMARKT (LAIKI AGORA)",
                "desc": "Durch den legendären Wochenmarkt von Exarchia schlendern; erster Tsipouro oder Kaffee in der Herbstsonne.",
                "dist": "1,9 km ab Apartment (oder nach dem Nationalmuseum)",
                "spot_id": 14
            },
            {
                "time": "13:30 – 16:30",
                "name": "AMA LACHEI (SCHULHOF-MEZE)",
                "desc": "Direkt an der Marktstraße (Kallidromiou 69): Große griechisch-kretische Sharing-Tafel im begrünten ehemaligen Grundschulhof.",
                "dist": "Direkt an der Kallidromiou 69",
                "spot_id": 14
            },
            {
                "time": "16:45 – 18:00",
                "name": "STREFI-HÜGEL (SUNSET WEGBIER) ODER WAREHOUSE EXARCHIA",
                "desc": "Entweder 5 Min. hoch auf den felsigen Strefi-Hügel für den Blick bis zur Akropolis — oder direkt auf die Fußgängerzone Valtetsiou ins Warehouse.",
                "dist": "300 m · 4 Min. Fußweg",
                "spot_id": 25
            },
            {
                "time": "18:30 – 21:30",
                "name": "TANINI AGAPI MOU ODER PHARAOH",
                "desc": "100+ offene griechische Naturweine & Sauerteig-Pinsa bei Tanini Agapi Mou (Ippokratous 91) oder Holzfeuer & Vinyl im Pharaoh (Solomou 54).",
                "dist": "450 m · 5 Min. Fußweg",
                "spot_id": 16
            },
            {
                "time": "21:30 – 23:30",
                "name": "ROZALIA EXARCHIA (16-TELLER-TABLETT)",
                "desc": "Spätes Tavernen-Festmahl im winterfest überdachten Gartenhof auf der Valtetsiou 59.",
                "dist": "450 m · 5 Min. Fußweg",
                "spot_id": 17
            },
            {
                "time": "23:30 – 04:00",
                "name": "STRAKASTRÜKA (ANDREA METAXA 19) & SPIRTO",
                "desc": "60 m neben Rozalia: 9 Craft-Beer-Taps & Straka Hot Dog vor dem strakastrüka, danach letzter Absacker auf der Koletti-/Tzavella-Achse im Spirto.",
                "dist": "60 m · 1 Min. Fußweg",
                "spot_id": 18
            }
        ]
    }
]


def clean_markdown_for_html(md_text: str):
    """Extract images and render clean HTML for the full dossier drawer."""
    images = []
    seen_imgs = set()

    # 1. Standard markdown images: ![alt](../images/foo.jpg)
    for m in re.finditer(r'!\[(.*?)\]\((?:\.\./)?images/([^\)]+)\)', md_text):
        alt, fname = m.group(1).strip(), m.group(2).strip()
        if fname not in seen_imgs and os.path.exists(os.path.join(IMAGES_DIR, fname)):
            seen_imgs.add(fname)
            images.append({"src": f"images/{fname}", "caption": alt or fname})

    # 2. Code-path image lists in dossiers 19..26: `/workspace/athen-trip/images/foo.jpg` — Caption
    for m in re.finditer(r'`/workspace/athen-trip/images/([^`]+)`\s*[—–-]\s*(.+)', md_text):
        fname, cap = m.group(1).strip(), m.group(2).strip()
        if fname not in seen_imgs and os.path.exists(os.path.join(IMAGES_DIR, fname)):
            seen_imgs.add(fname)
            images.append({"src": f"images/{fname}", "caption": cap})

    # Strip the trailing image section from markdown body so we render our sharp architectural gallery instead
    body = re.sub(r'\n##+\s*(?:📸\s*Bilder|5\.\s*Verifizierte\s+Raum-).*$', '', md_text, flags=re.S)
    # Also remove top H1 title line
    body = re.sub(r'^#\s+.+?\n+', '', body.strip())
    # Remove any remaining inline ../images/ markdown lines
    body = re.sub(r'^\s*-?\s*!\[.*?\]\((?:\.\./)?images/.*?\)\s*$', '', body, flags=re.M)

    html_body = markdown.markdown(body, extensions=['extra', 'sane_lists'])
    # Open all external links in new tab
    html_body = html_body.replace('<a href="http', '<a target="_blank" rel="noopener" href="http')
    return html_body, images


def parse_all_dossiers():
    spots = []
    files = sorted(glob.glob(os.path.join(DOSSIERS_DIR, "*.md")))
    for fpath in files:
        fname = os.path.basename(fpath)
        num_m = re.match(r'^(\d+)_', fname)
        if not num_m:
            continue
        num = int(num_m.group(1))
        raw = open(fpath, encoding="utf-8").read()
        meta = SPOT_META[num]

        # Extract Google Maps links from markdown
        gmaps_links = []
        for gm in re.finditer(r'\[([^\]]+)\]\((https://www\.google\.com/maps[^\)]+)\)', raw):
            label, url = gm.group(1).strip(), gm.group(2).strip()
            # Skip apartment link in dossier 26 as primary if others exist
            if num == 26 and "ATHINUM" in label:
                continue
            gmaps_links.append({"label": label, "url": url})

        primary_gmaps = gmaps_links[0]["url"] if gmaps_links else f"https://www.google.com/maps/search/?api=1&query={meta['lat']},{meta['lng']}"

        # Extract phone if present
        phone_m = re.search(r'\+30\s*\d[\d\s]{7,12}\d', raw)
        phone = phone_m.group(0).strip() if phone_m else ""

        html_body, images = clean_markdown_for_html(raw)

        spots.append({
            "id": num,
            "num_str": f"{num:02d}",
            "file": fname,
            "title": meta["short_title"],
            "subtitle": meta["subtitle"],
            "district": meta["district"],
            "district_tag": meta["district_tag"],
            "cats": meta["cats"],
            "cat_label": meta["cat_label"],
            "address": meta["address"],
            "walk_min": meta["walk_min"],
            "walk_text": meta["walk_text"],
            "hours_short": meta["hours_short"],
            "food_status": meta["food_status"],
            "food_note": meta["food_note"],
            "signature": meta["signature"],
            "insider": meta["insider"],
            "lat": meta["lat"],
            "lng": meta["lng"],
            "gmaps": primary_gmaps,
            "gmaps_all": gmaps_links,
            "phone": phone,
            "images": images,
            "hero_image": images[0]["src"] if images else "",
            "html": html_body,
            "search_text": re.sub(r'\s+', ' ', raw).lower()
        })
    return spots


def generate_kml(spots):
    placemarks = []
    # Home Base placemark
    placemarks.append(f"""
    <Placemark>
      <name>[00] {html.escape(HOME_BASE['name'])}</name>
      <description><![CDATA[<b>{html.escape(HOME_BASE['subtitle'])}</b><br/>Adresse: {html.escape(HOME_BASE['address'])}<br/><a href="{html.escape(HOME_BASE['gmaps'])}">Google Maps</a>]]></description>
      <Point><coordinates>{HOME_BASE['lng']},{HOME_BASE['lat']},0</coordinates></Point>
    </Placemark>""")

    for s in spots:
        desc = (
            f"<b>{s['cat_label']} — {s['district']}</b><br/>"
            f"<b>Adresse:</b> {s['address']} ({s['walk_text']} ab Apartment)<br/>"
            f"<b>Zeiten:</b> {s['hours_short']}<br/>"
            f"<b>Essen:</b> {s['food_status']} ({s['food_note']})<br/>"
            f"<b>Bestellung:</b> {s['signature']}<br/>"
            f"<b>Insider:</b> {s['insider']}<br/>"
            f"<a href='{s['gmaps']}'>Google Maps öffnen</a>"
        )
        placemarks.append(f"""
    <Placemark>
      <name>[{s['num_str']}] {html.escape(s['title'])}</name>
      <description><![CDATA[{desc}]]></description>
      <Point><coordinates>{s['lng']},{s['lat']},0</coordinates></Point>
    </Placemark>""")

    kml = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>OCHO HERRENTOUR — ATHEN 2026 (Alle 26 Dossiers + Home Base)</name>
    <description>Kuratierter Athen-Kompass der Ochos (05.11.–08.11.2026)</description>
    {''.join(placemarks)}
  </Document>
</kml>
"""
    kml_path = os.path.join(BASE_DIR, "ochos_athen_2026.kml")
    with open(kml_path, "w", encoding="utf-8") as f:
        f.write(kml)
    return kml_path


def build_html(spots, master_html):
    spots_json = json.dumps(spots, ensure_ascii=False)
    routes_json = json.dumps(ROUTES_DATA, ensure_ascii=False)
    home_json = json.dumps(HOME_BASE, ensure_ascii=False)

    html_doc = f"""<!DOCTYPE html>
<html lang="de" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <base href="https://hg-saarlouis.github.io/herrentour-athen/">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
  <meta name="robots" content="noindex, nofollow">
  <meta name="theme-color" content="#0A0A0A">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="OCHOS ATHEN">
  <base href="https://hg-saarlouis.github.io/herrentour-athen/">
  <title>OCHOS — HERRENTOUR ATHEN 2026</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&family=Space+Grotesk:wght@600;700&family=Syne:wght@700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" crossorigin=""/>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin=""></script>
  <style>
    /* ==========================================================================
       SWISS BRUTALIST / EDITORIAL MONOCHROME DESIGN SYSTEM
       Zero rounded corners. Strict 1px architectural grid. Pure Black & White.
       ========================================================================== */
    *, *::before, *::after {{
      box-sizing: border-box;
      border-radius: 0 !important;
      margin: 0;
      padding: 0;
    }}

    :root[data-theme="light"] {{
      --bg: #F7F7F5;
      --surface: #FFFFFF;
      --surface-alt: #EFEFED;
      --fg: #0A0A0A;
      --fg-muted: #525252;
      --fg-subtle: #787878;
      --border: #0A0A0A;
      --border-subtle: #D4D4D0;
      --inv-bg: #0A0A0A;
      --inv-fg: #FFFFFF;
      --backdrop: rgba(10, 10, 10, 0.72);
      --img-filter: grayscale(100%) contrast(1.08);
    }}

    :root[data-theme="dark"] {{
      --bg: #080808;
      --surface: #111111;
      --surface-alt: #181818;
      --fg: #F5F5F3;
      --fg-muted: #A3A3A0;
      --fg-subtle: #6E6E6A;
      --border: #F5F5F3;
      --border-subtle: #2C2C2C;
      --inv-bg: #F5F5F3;
      --inv-fg: #080808;
      --backdrop: rgba(0, 0, 0, 0.84);
      --img-filter: grayscale(100%) contrast(1.12);
    }}

    html, body {{
      background-color: var(--bg);
      color: var(--fg);
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      font-size: 15px;
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
      overflow-x: hidden;
    }}

    ::selection {{
      background: var(--inv-bg);
      color: var(--inv-fg);
    }}

    /* TYPOGRAPHY UTILITIES */
    .font-display {{
      font-family: 'Syne', 'Space Grotesk', sans-serif;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: -0.03em;
    }}
    .font-grotesk {{
      font-family: 'Space Grotesk', sans-serif;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: -0.02em;
    }}
    .font-mono {{
      font-family: 'JetBrains Mono', monospace;
      font-variant-numeric: tabular-nums;
    }}

    /* LAYOUT SHELL */
    .app-shell {{
      max-width: 1280px;
      margin: 0 auto;
      border-left: 1px solid var(--border);
      border-right: 1px solid var(--border);
      min-height: 100vh;
      background: var(--bg);
    }}

    /* TOP STATUS TICKER */
    .top-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border);
      background: var(--inv-bg);
      color: var(--inv-fg);
      padding: 6px 16px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      gap: 12px;
      flex-wrap: wrap;
    }}

    .top-bar-right {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    /* MASTHEAD */
    .masthead {{
      display: grid;
      grid-template-columns: 1fr auto;
      border-bottom: 2px solid var(--border);
      background: var(--surface);
    }}

    .masthead-main {{
      padding: 24px 20px 20px;
    }}

    .masthead-kicker {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: var(--fg-muted);
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .masthead-kicker span.badge {{
      background: var(--inv-bg);
      color: var(--inv-fg);
      padding: 2px 6px;
      font-size: 10px;
    }}

    .masthead-title {{
      font-family: 'Syne', sans-serif;
      font-weight: 800;
      font-size: clamp(2.3rem, 7vw, 4.75rem);
      line-height: 0.92;
      letter-spacing: -0.04em;
      text-transform: uppercase;
      word-break: break-word;
    }}

    .masthead-sub {{
      margin-top: 12px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      color: var(--fg-muted);
      display: flex;
      flex-wrap: wrap;
      gap: 6px 18px;
    }}

    .masthead-actions {{
      display: flex;
      flex-direction: column;
      border-left: 1px solid var(--border);
      min-width: 165px;
    }}

    .ActionBtn {{
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 12px 16px;
      background: var(--surface);
      color: var(--fg);
      border: none;
      border-bottom: 1px solid var(--border);
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      cursor: pointer;
      text-decoration: none;
      transition: background 0.12s ease, color 0.12s ease;
    }}
    .ActionBtn:last-child {{
      border-bottom: none;
    }}
    .ActionBtn:hover, .ActionBtn:active {{
      background: var(--inv-bg);
      color: var(--inv-fg);
    }}

    @media (max-width: 680px) {{
      .masthead {{
        grid-template-columns: 1fr;
      }}
      .masthead-actions {{
        border-left: none;
        border-top: 1px solid var(--border);
        flex-direction: row;
        flex-wrap: wrap;
      }}
      .ActionBtn {{
        flex: 1 1 33%;
        border-bottom: none;
        border-right: 1px solid var(--border);
        justify-content: center;
        padding: 10px 8px;
        font-size: 10px;
      }}
      .ActionBtn:last-child {{
        border-right: none;
      }}
    }}

    /* STICKY PRIMARY NAVIGATION */
    .sticky-nav {{
      position: sticky;
      top: 0;
      z-index: 900;
      background: var(--surface);
      border-bottom: 2px solid var(--border);
    }}

    .mode-tabs {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
    }}

    .mode-tab {{
      appearance: none;
      background: var(--surface);
      color: var(--fg);
      border: none;
      border-right: 1px solid var(--border);
      padding: 14px 10px;
      font-family: 'Space Grotesk', sans-serif;
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      transition: background 0.1s, color 0.1s;
    }}
    .mode-tab:last-child {{
      border-right: none;
    }}
    .mode-tab .tab-num {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      opacity: 0.65;
    }}
    .mode-tab.active {{
      background: var(--inv-bg);
      color: var(--inv-fg);
    }}
    .mode-tab:hover:not(.active) {{
      background: var(--surface-alt);
    }}

    @media (max-width: 640px) {{
      .mode-tab {{
        padding: 12px 4px;
        font-size: 11px;
        flex-direction: column;
        gap: 2px;
      }}
    }}

    /* CONTROL BAR (SEARCH + FILTERS) */
    .controls-panel {{
      background: var(--surface);
      border-bottom: 1px solid var(--border);
    }}

    .search-row {{
      display: grid;
      grid-template-columns: 1fr auto auto;
      border-bottom: 1px solid var(--border-subtle);
    }}

    .search-input-wrap {{
      display: flex;
      align-items: center;
      padding: 0 16px;
      gap: 10px;
    }}

    .search-prefix {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      font-weight: 700;
      color: var(--fg-muted);
      user-select: none;
    }}

    .search-input {{
      width: 100%;
      border: none;
      background: transparent;
      color: var(--fg);
      font-family: 'JetBrains Mono', monospace;
      font-size: 13px;
      padding: 13px 0;
      outline: none;
    }}
    .search-input::placeholder {{
      color: var(--fg-subtle);
    }}

    .ctrl-btn {{
      background: var(--surface);
      color: var(--fg);
      border: none;
      border-left: 1px solid var(--border-subtle);
      padding: 0 16px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      cursor: pointer;
      white-space: nowrap;
    }}
    .ctrl-btn:hover, .ctrl-btn.active {{
      background: var(--inv-bg);
      color: var(--inv-fg);
    }}

    .filter-strip {{
      display: flex;
      overflow-x: auto;
      scrollbar-width: none;
      border-bottom: 1px solid var(--border-subtle);
    }}
    .filter-strip::-webkit-scrollbar {{
      display: none;
    }}
    .filter-strip:last-child {{
      border-bottom: none;
    }}

    .filter-label {{
      padding: 9px 12px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--fg-subtle);
      background: var(--surface-alt);
      border-right: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      white-space: nowrap;
    }}

    .filter-chip {{
      appearance: none;
      background: var(--surface);
      color: var(--fg);
      border: none;
      border-right: 1px solid var(--border-subtle);
      padding: 9px 14px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 500;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      cursor: pointer;
      white-space: nowrap;
      transition: background 0.1s, color 0.1s;
    }}
    .filter-chip:hover {{
      background: var(--surface-alt);
    }}
    .filter-chip.active {{
      background: var(--inv-bg);
      color: var(--inv-fg);
      font-weight: 700;
    }}

    /* RESULTS COUNTER BAR */
    .status-strip {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 16px;
      background: var(--surface-alt);
      border-bottom: 1px solid var(--border);
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: var(--fg-muted);
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }}

    /* DOSSIER GRID */
    .spots-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      background: var(--border);
      gap: 1px;
      border-bottom: 1px solid var(--border);
    }}
    @media (max-width: 860px) {{
      .spots-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    .spot-card {{
      background: var(--surface);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: background 0.12s;
    }}

    .card-top {{
      display: grid;
      grid-template-columns: 76px 1fr;
      border-bottom: 1px solid var(--border-subtle);
    }}

    .card-index {{
      background: var(--inv-bg);
      color: var(--inv-fg);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 12px 6px;
      border-right: 1px solid var(--border);
    }}
    .card-index-num {{
      font-family: 'Syne', sans-serif;
      font-size: 28px;
      font-weight: 800;
      line-height: 1;
      letter-spacing: -0.04em;
    }}
    .card-index-walk {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 9px;
      margin-top: 6px;
      letter-spacing: 0.05em;
      opacity: 0.85;
      text-align: center;
    }}

    .card-head {{
      padding: 14px 16px;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }}

    .card-meta-line {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--fg-muted);
      margin-bottom: 4px;
    }}

    .card-district-tag {{
      border: 1px solid var(--border);
      padding: 1px 6px;
      color: var(--fg);
      font-size: 9.5px;
    }}

    .card-title {{
      font-family: 'Space Grotesk', sans-serif;
      font-size: 22px;
      font-weight: 700;
      line-height: 1.08;
      letter-spacing: -0.02em;
      text-transform: uppercase;
      margin-bottom: 4px;
      cursor: pointer;
    }}
    .card-title:hover {{
      text-decoration: underline;
      text-underline-offset: 3px;
    }}

    .card-subtitle {{
      font-size: 12.5px;
      color: var(--fg-muted);
      line-height: 1.35;
    }}

    /* CARD PHOTO STRIP */
    .card-media {{
      position: relative;
      height: 190px;
      overflow: hidden;
      border-bottom: 1px solid var(--border-subtle);
      background: var(--surface-alt);
      cursor: pointer;
    }}
    .card-media img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      filter: var(--img-filter);
      transition: filter 0.25s ease, transform 0.35s ease;
      display: block;
    }}
    body.color-photos .card-media img,
    .card-media:hover img {{
      filter: grayscale(0%) contrast(1.02);
    }}
    .card-media-badge {{
      position: absolute;
      bottom: 0;
      right: 0;
      background: var(--inv-bg);
      color: var(--inv-fg);
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      font-weight: 700;
      padding: 4px 8px;
      letter-spacing: 0.06em;
    }}
    .card-food-badge {{
      position: absolute;
      top: 0;
      left: 0;
      background: var(--surface);
      color: var(--fg);
      border-right: 1px solid var(--border);
      border-bottom: 1px solid var(--border);
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      font-weight: 700;
      padding: 4px 8px;
      letter-spacing: 0.06em;
    }}

    /* TACTICAL SPECS TABLE INSIDE CARD */
    .card-specs {{
      padding: 14px 16px;
      display: grid;
      gap: 10px;
      font-size: 13px;
      flex: 1;
    }}
    .spec-row {{
      display: grid;
      grid-template-columns: 92px 1fr;
      gap: 8px;
      align-items: baseline;
      border-bottom: 1px dotted var(--border-subtle);
      padding-bottom: 7px;
    }}
    .spec-row:last-child {{
      border-bottom: none;
      padding-bottom: 0;
    }}
    .spec-key {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--fg-muted);
    }}
    .spec-val {{
      color: var(--fg);
      line-height: 1.4;
    }}

    /* CARD ACTIONS FOOTER */
    .card-actions {{
      display: grid;
      grid-template-columns: 1.3fr 1fr auto;
      border-top: 1px solid var(--border);
    }}
    .card-btn {{
      appearance: none;
      background: var(--surface);
      color: var(--fg);
      border: none;
      border-right: 1px solid var(--border);
      padding: 12px 12px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      cursor: pointer;
      text-decoration: none;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      transition: background 0.1s, color 0.1s;
    }}
    .card-btn:last-child {{
      border-right: none;
    }}
    .card-btn.primary {{
      background: var(--inv-bg);
      color: var(--inv-fg);
    }}
    .card-btn.primary:hover {{
      opacity: 0.88;
    }}
    .card-btn:not(.primary):hover {{
      background: var(--inv-bg);
      color: var(--inv-fg);
    }}

    /* ==========================================================================
       VIEW SECTIONS (DOSSIERS / MAP / ROUTES / MASTER)
       ========================================================================== */
    .view-section {{
      display: none;
    }}
    .view-section.active {{
      display: block;
    }}

    /* MAP SECTION */
    .map-toolbar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
      padding: 12px 16px;
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
    }}
    .map-toolbar-btns {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .sharp-btn {{
      background: var(--surface);
      color: var(--fg);
      border: 1px solid var(--border);
      padding: 7px 12px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      cursor: pointer;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .sharp-btn:hover, .sharp-btn.active {{
      background: var(--inv-bg);
      color: var(--inv-fg);
    }}

    #athen-map {{
      width: 100%;
      height: calc(100vh - 230px);
      min-height: 480px;
      background: var(--surface-alt);
      border-bottom: 1px solid var(--border);
    }}

    /* Custom Sharp Leaflet Markers */
    .ocho-pin {{
      background: var(--inv-bg);
      color: var(--inv-fg);
      border: 1.5px solid var(--bg);
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      width: 28px !important;
      height: 28px !important;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 2px 2px 0 var(--border);
    }}
    .ocho-pin.home-pin {{
      background: var(--fg);
      color: var(--bg);
      border: 2px solid var(--bg);
      width: 34px !important;
      height: 34px !important;
      font-size: 12px;
    }}
    .leaflet-popup-content-wrapper,
    .leaflet-popup-tip {{
      background: var(--surface) !important;
      color: var(--fg) !important;
      border: 1px solid var(--border) !important;
      box-shadow: 4px 4px 0 var(--border) !important;
    }}
    .leaflet-container a.leaflet-popup-close-button {{
      color: var(--fg) !important;
      font-family: 'JetBrains Mono', monospace !important;
    }}

    /* ROUTES TIMELINE SECTION */
    .routes-wrap {{
      padding: 24px 20px 48px;
      display: grid;
      gap: 32px;
    }}
    .route-block {{
      border: 1px solid var(--border);
      background: var(--surface);
    }}
    .route-header {{
      background: var(--inv-bg);
      color: var(--inv-fg);
      padding: 16px 20px;
      border-bottom: 1px solid var(--border);
    }}
    .route-day {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      letter-spacing: 0.12em;
      opacity: 0.8;
      margin-bottom: 4px;
    }}
    .route-title {{
      font-family: 'Space Grotesk', sans-serif;
      font-size: 20px;
      font-weight: 700;
      letter-spacing: -0.02em;
    }}
    .route-sub {{
      font-size: 12.5px;
      opacity: 0.85;
      margin-top: 4px;
    }}
    .route-steps {{
      display: grid;
    }}
    .route-step {{
      display: grid;
      grid-template-columns: 140px 1fr auto;
      border-bottom: 1px solid var(--border-subtle);
    }}
    .route-step:last-child {{
      border-bottom: none;
    }}
    .step-time {{
      padding: 16px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      font-weight: 700;
      border-right: 1px solid var(--border-subtle);
      background: var(--surface-alt);
      display: flex;
      flex-direction: column;
      justify-content: center;
    }}
    .step-dist {{
      font-size: 10px;
      font-weight: 400;
      color: var(--fg-muted);
      margin-top: 4px;
    }}
    .step-body {{
      padding: 16px;
    }}
    .step-name {{
      font-family: 'Space Grotesk', sans-serif;
      font-size: 16px;
      font-weight: 700;
      margin-bottom: 4px;
    }}
    .step-desc {{
      font-size: 13.5px;
      color: var(--fg-muted);
    }}
    .step-action {{
      padding: 16px;
      display: flex;
      align-items: center;
    }}
    @media (max-width: 680px) {{
      .route-step {{
        grid-template-columns: 1fr;
      }}
      .step-time {{
        border-right: none;
        border-bottom: 1px solid var(--border-subtle);
        padding: 10px 14px;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
      }}
      .step-dist {{
        margin-top: 0;
      }}
      .step-action {{
        padding: 0 14px 14px;
      }}
    }}

    /* MASTER CONTEXT / LOGISTIK SECTION */
    .master-wrap {{
      padding: 28px 24px 60px;
      max-width: 920px;
      margin: 0 auto;
    }}
    .prose h1, .prose h2, .prose h3, .prose h4 {{
      font-family: 'Space Grotesk', sans-serif;
      text-transform: uppercase;
      letter-spacing: -0.02em;
      margin-top: 28px;
      margin-bottom: 12px;
      line-height: 1.15;
    }}
    .prose h2 {{
      font-size: 20px;
      padding-bottom: 8px;
      border-bottom: 2px solid var(--border);
    }}
    .prose h3 {{
      font-size: 16px;
      padding-top: 6px;
    }}
    .prose p, .prose li {{
      font-size: 14.5px;
      line-height: 1.65;
      color: var(--fg);
    }}
    .prose p {{
      margin-bottom: 12px;
    }}
    .prose ul, .prose ol {{
      padding-left: 20px;
      margin-bottom: 16px;
    }}
    .prose li {{
      margin-bottom: 6px;
    }}
    .prose strong {{
      font-weight: 700;
    }}
    .prose code {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 12.5px;
      background: var(--surface-alt);
      border: 1px solid var(--border-subtle);
      padding: 1px 5px;
    }}
    .prose a {{
      color: var(--fg);
      font-weight: 600;
      text-decoration: underline;
      text-underline-offset: 3px;
    }}
    .prose a:hover {{
      background: var(--inv-bg);
      color: var(--inv-fg);
      text-decoration: none;
    }}
    .prose hr {{
      border: none;
      border-top: 1px solid var(--border);
      margin: 28px 0;
    }}

    /* ==========================================================================
       FULL DOSSIER MODAL DRAWER
       ========================================================================== */
    .drawer-backdrop {{
      position: fixed;
      inset: 0;
      background: var(--backdrop);
      z-index: 2000;
      display: none;
      justify-content: flex-end;
    }}
    .drawer-backdrop.open {{
      display: flex;
    }}
    .drawer-panel {{
      width: min(860px, 100vw);
      height: 100%;
      background: var(--surface);
      border-left: 2px solid var(--border);
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }}
    .drawer-topbar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: var(--inv-bg);
      color: var(--inv-fg);
      border-bottom: 1px solid var(--border);
      padding: 0 0 0 18px;
      min-height: 52px;
      flex-shrink: 0;
    }}
    .drawer-kicker {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    .drawer-top-actions {{
      display: flex;
      height: 52px;
    }}
    .drawer-close-btn {{
      background: var(--inv-bg);
      color: var(--inv-fg);
      border: none;
      border-left: 1px solid var(--border-subtle);
      padding: 0 20px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      cursor: pointer;
    }}
    .drawer-close-btn:hover {{
      background: var(--surface);
      color: var(--fg);
    }}
    .drawer-scroll {{
      flex: 1;
      overflow-y: auto;
      padding: 24px 24px 64px;
    }}
    .drawer-title {{
      font-family: 'Syne', sans-serif;
      font-size: clamp(1.8rem, 4.5vw, 2.75rem);
      font-weight: 800;
      line-height: 0.98;
      letter-spacing: -0.03em;
      text-transform: uppercase;
      margin-bottom: 8px;
    }}
    .drawer-subtitle {{
      font-size: 14px;
      color: var(--fg-muted);
      margin-bottom: 20px;
    }}
    .drawer-quick-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      border: 1px solid var(--border);
      margin-bottom: 24px;
      background: var(--border);
      gap: 1px;
    }}
    @media (max-width: 580px) {{
      .drawer-quick-grid {{
        grid-template-columns: 1fr;
      }}
      .drawer-scroll {{
        padding: 18px 16px 56px;
      }}
    }}
    .dq-cell {{
      background: var(--surface-alt);
      padding: 12px 14px;
    }}
    .dq-label {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 0.08em;
      color: var(--fg-muted);
      text-transform: uppercase;
      margin-bottom: 4px;
    }}
    .dq-val {{
      font-size: 13px;
      font-weight: 600;
    }}

    /* DRAWER PHOTO GALLERY */
    .drawer-gallery {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
      gap: 1px;
      background: var(--border);
      border: 1px solid var(--border);
      margin-bottom: 28px;
    }}
    .gallery-item {{
      background: var(--surface);
      display: flex;
      flex-direction: column;
      cursor: pointer;
    }}
    .gallery-item img {{
      width: 100%;
      height: 160px;
      object-fit: cover;
      filter: var(--img-filter);
      transition: filter 0.2s;
      display: block;
    }}
    body.color-photos .gallery-item img,
    .gallery-item:hover img {{
      filter: grayscale(0%);
    }}
    .gallery-cap {{
      padding: 8px 10px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 10.5px;
      color: var(--fg-muted);
      border-top: 1px solid var(--border-subtle);
      line-height: 1.35;
      flex: 1;
    }}

    /* LIGHTBOX */
    .lightbox {{
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.94);
      z-index: 3000;
      display: none;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      padding: 20px;
    }}
    .lightbox.open {{
      display: flex;
    }}
    .lightbox img {{
      max-width: 95vw;
      max-height: 80vh;
      border: 1px solid #FFFFFF;
      object-fit: contain;
    }}
    .lightbox-cap {{
      margin-top: 14px;
      color: #FFFFFF;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      max-width: 680px;
      text-align: center;
    }}
    .lightbox-close {{
      position: absolute;
      top: 16px;
      right: 16px;
      background: #FFFFFF;
      color: #000000;
      border: none;
      padding: 10px 16px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      text-transform: uppercase;
    }}

    /* FOOTER */
    .app-footer {{
      border-top: 2px solid var(--border);
      padding: 24px 20px;
      background: var(--surface);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: var(--fg-muted);
    }}
  </style>
</head>
<body>
  <div class="app-shell">
    <!-- TOP STATUS TICKER -->
    <div class="top-bar">
      <div>OCHO HERRENTOUR // ATHEN 05.11.–08.11.2026</div>
      <div class="top-bar-right">
        <span>BASE: ATHINUM 1 · KORINNIS 11</span>
        <span>·</span>
        <span>26 DOSSIERS · 134 FOTOS</span>
      </div>
    </div>

    <!-- ARCHITECTURAL MASTHEAD -->
    <header class="masthead">
      <div class="masthead-main">
        <div class="masthead-kicker">
          <span class="badge">OCHOS</span>
          <span>FIELD MANUAL &amp; TACTICAL POCKET GUIDE</span>
        </div>
        <h1 class="masthead-title">OCHO HERRENTOUR</h1>
        <div class="masthead-sub">
          <span>ATHEN, GRIECHENLAND (37.9807° N, 23.7226° E)</span>
          <span>·</span>
          <span>ABFLUG DO 14:25 FRA</span>
          <span>·</span>
          <span>HOME-PIN: KORINNIS 11 (PSYRI)</span>
        </div>
      </div>
      <div class="masthead-actions">
        <button class="ActionBtn" id="themeToggleBtn" onclick="toggleTheme()" title="Light / Dark Mode umschalten">
          <span>MODE</span>
          <span id="themeLabel">[DARK]</span>
        </button>
        <button class="ActionBtn" id="photoModeBtn" onclick="togglePhotoColor()" title="Fotos S/W oder Farbe">
          <span>FOTOS</span>
          <span id="photoModeLabel">[S/W]</span>
        </button>
        <a class="ActionBtn" href="ochos_athen_2026.kml" download="ochos_athen_2026.kml">
          <span>KML PINS</span>
          <span>[↓]</span>
        </a>
      </div>
    </header>

    <!-- STICKY MODE NAVIGATION -->
    <nav class="sticky-nav">
      <div class="mode-tabs">
        <button class="mode-tab active" data-view="dossiers" onclick="switchView('dossiers')">
          <span class="tab-num">01</span>
          <span>DOSSIERS (26)</span>
        </button>
        <button class="mode-tab" data-view="map" onclick="switchView('map')">
          <span class="tab-num">02</span>
          <span>RADAR / KARTE</span>
        </button>
        <button class="mode-tab" data-view="routes" onclick="switchView('routes')">
          <span class="tab-num">03</span>
          <span>ROUTEN (DO–SA)</span>
        </button>
        <button class="mode-tab" data-view="master" onclick="switchView('master')">
          <span class="tab-num">04</span>
          <span>MASTER-GUIDE</span>
        </button>
      </div>
    </nav>

    <!-- ======================================================================
         VIEW 01: DOSSIERS (FILTERABLE ARCHITECTURAL GRID)
         ====================================================================== -->
    <section id="view-dossiers" class="view-section active">
      <div class="controls-panel">
        <div class="search-row">
          <div class="search-input-wrap">
            <span class="search-prefix">SUCHE //</span>
            <input type="search" id="searchInput" class="search-input" placeholder="Spot, Drink, Gericht, Straße (z.B. Pastirma, Negroni, Rooftop, Walk-in)..." oninput="renderSpots()">
          </div>
          <button class="ctrl-btn" id="sortWalkBtn" onclick="toggleSortWalk()" title="Nach Entfernung zum Apartment sortieren">
            SORT: #01–#26
          </button>
          <button class="ctrl-btn" onclick="resetFilters()">
            RESET
          </button>
        </div>

        <!-- SITUATION FILTER -->
        <div class="filter-strip" id="catFilterStrip">
          <div class="filter-label">EINSATZ</div>
          <button class="filter-chip active" data-cat="all" onclick="setCatFilter('all')">ALLE (26)</button>
          <button class="filter-chip" data-cat="breakfast" onclick="setCatFilter('breakfast')">FRÜHSTÜCK / BRUNCH</button>
          <button class="filter-chip" data-cat="daydrinking" onclick="setCatFilter('daydrinking')">DAYDRINKING &amp; HÖFE</button>
          <button class="filter-chip" data-cat="food" onclick="setCatFilter('food')">ESSEN / MEZE / TAVERNEN</button>
          <button class="filter-chip" data-cat="cocktails" onclick="setCatFilter('cocktails')">50-BEST COCKTAILS</button>
          <button class="filter-chip" data-cat="rooftop" onclick="setCatFilter('rooftop')">ROOFTOPS</button>
          <button class="filter-chip" data-cat="wine" onclick="setCatFilter('wine')">NATURWEIN</button>
          <button class="filter-chip" data-cat="beer" onclick="setCatFilter('beer')">CRAFT BEER</button>
          <button class="filter-chip" data-cat="late" onclick="setCatFilter('late')">SPÄTNACHT / ABSACKER</button>
        </div>

        <!-- DISTRICT FILTER -->
        <div class="filter-strip" id="distFilterStrip">
          <div class="filter-label">VIERTEL</div>
          <button class="filter-chip active" data-dist="all" onclick="setDistFilter('all')">ALLE VIERTEL</button>
          <button class="filter-chip" data-dist="psyri" onclick="setDistFilter('psyri')">PSYRI / UMS APARTMENT</button>
          <button class="filter-chip" data-dist="zentrum" onclick="setDistFilter('zentrum')">ZENTRUM / COCKTAILMEILE</button>
          <button class="filter-chip" data-dist="monastiraki" onclick="setDistFilter('monastiraki')">MONASTIRAKI</button>
          <button class="filter-chip" data-dist="exarchia" onclick="setDistFilter('exarchia')">EXARCHIA</button>
          <button class="filter-chip" data-dist="petralona" onclick="setDistFilter('petralona')">PETRALONA (WEST)</button>
          <button class="filter-chip" data-dist="riviera" onclick="setDistFilter('riviera')">RIVIERA (ALIMOS)</button>
        </div>
      </div>

      <div class="status-strip">
        <span id="resultsCountLabel">ZEIGE 26 VON 26 DOSSIERS</span>
        <span>HOME-PIN: ATHINUM 1 (KORINNIS 11)</span>
      </div>

      <div id="spotsGrid" class="spots-grid"></div>
    </section>

    <!-- ======================================================================
         VIEW 02: INTERACTIVE MONOCHROME RADAR MAP
         ====================================================================== -->
    <section id="view-map" class="view-section">
      <div class="map-toolbar">
        <div>
          <strong>GPS RADAR //</strong> <span id="gpsStatus">Klicke auf einen Pin (#01–#26) für Details oder [HOME] für Korinnis 11.</span>
        </div>
        <div class="map-toolbar-btns">
          <button class="sharp-btn" onclick="focusHomeBase()">[00] HOME BASE (KORINNIS 11)</button>
          <button class="sharp-btn" onclick="locateUser()">MEIN GPS-STANDORT</button>
          <button class="sharp-btn" onclick="fitAllMarkers()">ALLE 26 PINS ZEIGEN</button>
        </div>
      </div>
      <div id="athen-map"></div>
    </section>

    <!-- ======================================================================
         VIEW 03: TACTICAL ROUTES (DO OPTION A/B, FR KÜSTE, SA EXARCHIA)
         ====================================================================== -->
    <section id="view-routes" class="view-section">
      <div class="status-strip">
        <span>GEPLANTE ROUTEN-OPTIONEN (DO – SA)</span>
        <span>TIPPE AUF EINEN STOPP FÜR DAS VOLLE DOSSIER</span>
      </div>
      <div class="routes-wrap" id="routesContainer"></div>
    </section>

    <!-- ======================================================================
         VIEW 04: FULL MASTER CONTEXT & LOGISTICS
         ====================================================================== -->
    <section id="view-master" class="view-section">
      <div class="status-strip">
        <span>00_ATHEN_MASTER_CONTEXT.MD // GESAMTÜBERSICHT</span>
        <a href="https://www.google.com/maps/place/ATHINUM+1+%7C+by+Valenci/@37.9806589,23.7223653,61m/data=!3m1!1e3!4m6!3m5!1s0x14a1bd007b9342ff:0x8d7f2bb0512213cf!8m2!3d37.9806698!4d23.7225669!16s%2Fg%2F11xz165djq" target="_blank" rel="noopener" style="color:inherit;">APARTMENT AUF GOOGLE MAPS ↗</a>
      </div>
      <div class="master-wrap prose">
        {master_html}
      </div>
    </section>

    <!-- FOOTER -->
    <footer class="app-footer">
      <div>OCHO HERRENTOUR · ATHEN 2026 · SCHWARZ/WEISS EDITION</div>
      <div>HOME BASE: ATHINUM 1 · KORINNIS 11, 105 53 ATHEN</div>
    </footer>
  </div>

  <!-- ========================================================================
       FULL DOSSIER SLIDE-OVER DRAWER
       ======================================================================== -->
  <div id="dossierDrawer" class="drawer-backdrop" onclick="if(event.target===this) closeDrawer()">
    <div class="drawer-panel">
      <div class="drawer-topbar">
        <div class="drawer-kicker" id="drawerKicker">DOSSIER #01</div>
        <div class="drawer-top-actions">
          <button class="drawer-close-btn" onclick="prevNextSpot(-1)" title="Vorheriges Dossier">←</button>
          <button class="drawer-close-btn" onclick="prevNextSpot(1)" title="Nächstes Dossier">→</button>
          <button class="drawer-close-btn" onclick="closeDrawer()">SCHLIESSEN [ESC]</button>
        </div>
      </div>
      <div class="drawer-scroll" id="drawerBody"></div>
    </div>
  </div>

  <!-- ========================================================================
       LIGHTBOX FOR FULLSCREEN PHOTOS
       ======================================================================== -->
  <div id="lightbox" class="lightbox" onclick="closeLightbox()">
    <button class="lightbox-close" onclick="closeLightbox()">SCHLIESSEN [×]</button>
    <img id="lightboxImg" src="" alt="">
    <div id="lightboxCap" class="lightbox-cap"></div>
  </div>

  <script>
    const SPOTS = {spots_json};
    const ROUTES = {routes_json};
    const HOME_BASE = {home_json};

    let activeCat = 'all';
    let activeDist = 'all';
    let sortByWalk = false;
    let currentSpotId = null;
    let mapInstance = null;
    let tileLayer = null;
    let markersById = {{}};
    let userMarker = null;

    // THEME MANAGEMENT (LIGHT / DARK)
    function applyTheme(theme) {{
      document.documentElement.setAttribute('data-theme', theme);
      localStorage.setItem('ocho_theme', theme);
      const lbl = document.getElementById('themeLabel');
      if (lbl) lbl.textContent = theme === 'dark' ? '[DARK]' : '[LIGHT]';
      const metaTheme = document.querySelector('meta[name="theme-color"]');
      if (metaTheme) metaTheme.setAttribute('content', theme === 'dark' ? '#080808' : '#F7F7F5');
      updateMapTiles();
    }}

    function toggleTheme() {{
      const cur = document.documentElement.getAttribute('data-theme') || 'dark';
      applyTheme(cur === 'dark' ? 'light' : 'dark');
    }}

    function togglePhotoColor() {{
      document.body.classList.toggle('color-photos');
      const isColor = document.body.classList.contains('color-photos');
      localStorage.setItem('ocho_photos', isColor ? 'color' : 'bw');
      document.getElementById('photoModeLabel').textContent = isColor ? '[FARBE]' : '[S/W]';
    }}

    // VIEW SWITCHING
    function switchView(viewName) {{
      document.querySelectorAll('.mode-tab').forEach(btn => {{
        btn.classList.toggle('active', btn.dataset.view === viewName);
      }});
      document.querySelectorAll('.view-section').forEach(sec => {{
        sec.classList.toggle('active', sec.id === 'view-' + viewName);
      }});
      if (viewName === 'map') {{
        initMapIfNeeded();
        setTimeout(() => mapInstance.invalidateSize(), 80);
      }}
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    // FILTERING & SORTING
    function setCatFilter(cat) {{
      activeCat = cat;
      document.querySelectorAll('#catFilterStrip .filter-chip').forEach(c => {{
        c.classList.toggle('active', c.dataset.cat === cat);
      }});
      renderSpots();
    }}

    function setDistFilter(dist) {{
      activeDist = dist;
      document.querySelectorAll('#distFilterStrip .filter-chip').forEach(c => {{
        c.classList.toggle('active', c.dataset.dist === dist);
      }});
      renderSpots();
    }}

    function toggleSortWalk() {{
      sortByWalk = !sortByWalk;
      const btn = document.getElementById('sortWalkBtn');
      btn.textContent = sortByWalk ? 'SORT: ENTFERNUNG ↑' : 'SORT: #01–#26';
      btn.classList.toggle('active', sortByWalk);
      renderSpots();
    }}

    function resetFilters() {{
      activeCat = 'all';
      activeDist = 'all';
      sortByWalk = false;
      document.getElementById('searchInput').value = '';
      document.getElementById('sortWalkBtn').textContent = 'SORT: #01–#26';
      document.getElementById('sortWalkBtn').classList.remove('active');
      document.querySelectorAll('#catFilterStrip .filter-chip').forEach(c => c.classList.toggle('active', c.dataset.cat === 'all'));
      document.querySelectorAll('#distFilterStrip .filter-chip').forEach(c => c.classList.toggle('active', c.dataset.dist === 'all'));
      renderSpots();
    }}

    function renderSpots() {{
      const q = (document.getElementById('searchInput').value || '').trim().toLowerCase();
      let list = SPOTS.filter(s => {{
        if (activeCat !== 'all' && !s.cats.includes(activeCat)) return false;
        if (activeDist !== 'all' && s.district_tag !== activeDist) return false;
        if (q) {{
          const hay = (s.title + ' ' + s.subtitle + ' ' + s.district + ' ' + s.address + ' ' + s.signature + ' ' + s.insider + ' ' + s.search_text).toLowerCase();
          if (!hay.includes(q)) return false;
        }}
        return true;
      }});

      if (sortByWalk) {{
        list = [...list].sort((a, b) => a.walk_min - b.walk_min || a.id - b.id);
      }}

      document.getElementById('resultsCountLabel').textContent = `ZEIGE ${{list.length}} VON ${{SPOTS.length}} DOSSIERS`;

      const grid = document.getElementById('spotsGrid');
      if (!list.length) {{
        grid.innerHTML = `<div style="grid-column: 1 / -1; padding: 48px 20px; text-align: center; background: var(--surface); font-family: 'JetBrains Mono', monospace;">KEINE TREFFER FÜR DIESEN FILTER. <button class="sharp-btn" style="margin-left:12px;" onclick="resetFilters()">FILTER ZURÜCKSETZEN</button></div>`;
        return;
      }}

      grid.innerHTML = list.map(s => `
        <article class="spot-card" id="spot-card-${{s.id}}">
          <div>
            <div class="card-top">
              <div class="card-index">
                <span class="card-index-num">${{s.num_str}}</span>
                <span class="card-index-walk">${{s.walk_min}} MIN</span>
              </div>
              <div class="card-head">
                <div class="card-meta-line">
                  <span>${{s.cat_label}}</span>
                  <span class="card-district-tag">${{s.district}}</span>
                </div>
                <h2 class="card-title" onclick="openDrawer(${{s.id}})">${{s.title}}</h2>
                <div class="card-subtitle">${{s.subtitle}}</div>
              </div>
            </div>

            ${{s.hero_image ? `
            <div class="card-media" onclick="openDrawer(${{s.id}})">
              <img src="${{s.hero_image}}" alt="${{s.title}}" loading="lazy">
              <span class="card-food-badge">${{s.food_status}}</span>
              <span class="card-media-badge">${{s.images.length}} FOTOS →</span>
            </div>` : ''}}

            <div class="card-specs">
              <div class="spec-row">
                <span class="spec-key">DISTANZ</span>
                <span class="spec-val"><strong>${{s.walk_text}}</strong> ab Apartment · ${{s.address}}</span>
              </div>
              <div class="spec-row">
                <span class="spec-key">ZEITEN</span>
                <span class="spec-val">${{s.hours_short}}</span>
              </div>
              <div class="spec-row">
                <span class="spec-key">ESSEN</span>
                <span class="spec-val">${{s.food_note}}</span>
              </div>
              <div class="spec-row">
                <span class="spec-key">BESTELLEN</span>
                <span class="spec-val">${{s.signature}}</span>
              </div>
              <div class="spec-row">
                <span class="spec-key">INSIDER</span>
                <span class="spec-val">${{s.insider}}</span>
              </div>
            </div>
          </div>

          <div class="card-actions">
            <button class="card-btn primary" onclick="openDrawer(${{s.id}})">
              DOSSIER LESEN + ${{s.images.length}} FOTOS
            </button>
            <a class="card-btn" href="${{s.gmaps}}" target="_blank" rel="noopener">
              GOOGLE MAPS ↗
            </a>
            <button class="card-btn" onclick="showSpotOnMap(${{s.id}})" title="Auf der App-Karte zeigen">
              PIN
            </button>
          </div>
        </article>
      `).join('');
    }}

    // DRAWER (FULL DOSSIER VIEW)
    function openDrawer(spotId) {{
      const s = SPOTS.find(x => x.id === spotId);
      if (!s) return;
      currentSpotId = spotId;
      document.getElementById('drawerKicker').textContent = `DOSSIER #${{s.num_str}} // ${{s.district.toUpperCase()}}`;

      const extraMaps = (s.gmaps_all && s.gmaps_all.length > 1)
        ? `<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:20px;">` +
          s.gmaps_all.map(g => `<a class="sharp-btn" href="${{g.url}}" target="_blank" rel="noopener">📍 ${{g.label}} ↗</a>`).join('') +
          `</div>`
        : '';

      const galleryHtml = s.images.length ? `
        <div class="drawer-gallery">
          ${{s.images.map(img => `
            <div class="gallery-item" onclick="openLightbox('${{img.src.replace(/'/g, "\'")}}', '${{img.caption.replace(/'/g, "\'")}}')">
              <img src="${{img.src}}" alt="${{img.caption}}" loading="lazy">
              <div class="gallery-cap">${{img.caption}}</div>
            </div>
          `).join('')}}
        </div>
      ` : '';

      const body = document.getElementById('drawerBody');
      body.innerHTML = `
        <h2 class="drawer-title">${{s.title}}</h2>
        <div class="drawer-subtitle">${{s.subtitle}}</div>

        <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:20px;">
          <a class="sharp-btn active" href="${{s.gmaps}}" target="_blank" rel="noopener">GOOGLE MAPS NAVIGATION ↗</a>
          <button class="sharp-btn" onclick="closeDrawer();showSpotOnMap(${{s.id}})">AUF KARTE ZEIGEN</button>
          ${{s.phone ? `<a class="sharp-btn" href="tel:${{s.phone.replace(/\s+/g, '')}}">TEL: ${{s.phone}}</a>` : ''}}
        </div>
        ${{extraMaps}}

        <div class="drawer-quick-grid">
          <div class="dq-cell">
            <div class="dq-label">ADRESSE &amp; LAUFWEG AB KORINNIS 11</div>
            <div class="dq-val">${{s.address}} (${{s.walk_text}})</div>
          </div>
          <div class="dq-cell">
            <div class="dq-label">ÖFFNUNGSZEITEN</div>
            <div class="dq-val">${{s.hours_short}}</div>
          </div>
          <div class="dq-cell">
            <div class="dq-label">ESSEN-AMPEL</div>
            <div class="dq-val">${{s.food_status}} — ${{s.food_note}}</div>
          </div>
          <div class="dq-cell">
            <div class="dq-label">SIGNATURE BESTELLUNG</div>
            <div class="dq-val">${{s.signature}}</div>
          </div>
        </div>

        ${{galleryHtml}}

        <div class="prose">
          ${{s.html}}
        </div>
      `;
      body.scrollTop = 0;
      document.getElementById('dossierDrawer').classList.add('open');
      document.body.style.overflow = 'hidden';
    }}

    function closeDrawer() {{
      document.getElementById('dossierDrawer').classList.remove('open');
      document.body.style.overflow = '';
    }}

    function prevNextSpot(delta) {{
      if (!currentSpotId) return;
      let nextId = currentSpotId + delta;
      if (nextId < 1) nextId = SPOTS.length;
      if (nextId > SPOTS.length) nextId = 1;
      openDrawer(nextId);
    }}

    // LIGHTBOX
    function openLightbox(src, cap) {{
      document.getElementById('lightboxImg').src = src;
      document.getElementById('lightboxCap').textContent = cap || '';
      document.getElementById('lightbox').classList.add('open');
    }}
    function closeLightbox() {{
      document.getElementById('lightbox').classList.remove('open');
    }}

    // ROUTES RENDERING
    function renderRoutes() {{
      const container = document.getElementById('routesContainer');
      container.innerHTML = ROUTES.map(r => `
        <div class="route-block">
          <div class="route-header">
            <div class="route-day">${{r.day}}</div>
            <div class="route-title">${{r.title}}</div>
            <div class="route-sub">${{r.subtitle}}</div>
          </div>
          <div class="route-steps">
            ${{r.stops.map(st => `
              <div class="route-step">
                <div class="step-time">
                  <span>${{st.time}}</span>
                  <span class="step-dist">${{st.dist}}</span>
                </div>
                <div class="step-body">
                  <div class="step-name">${{st.name}}</div>
                  <div class="step-desc">${{st.desc}}</div>
                </div>
                <div class="step-action">
                  ${{st.spot_id ? `<button class="sharp-btn" onclick="openDrawer(${{st.spot_id}})">DOSSIER #${{String(st.spot_id).padStart(2,'0')}} →</button>` : `<a class="sharp-btn" href="${{HOME_BASE.gmaps}}" target="_blank" rel="noopener">HOME PIN ↗</a>`}}
                </div>
              </div>
            `).join('')}}
          </div>
        </div>
      `).join('');
    }}

    // INTERACTIVE LEAFLET MAP
    function updateMapTiles() {{
      if (!mapInstance) return;
      const theme = document.documentElement.getAttribute('data-theme') || 'dark';
      const url = theme === 'dark'
        ? 'https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png'
        : 'https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png';
      if (tileLayer) mapInstance.removeLayer(tileLayer);
      tileLayer = L.tileLayer(url, {{
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        subdomains: 'abcd',
        maxZoom: 20
      }}).addTo(mapInstance);
    }}

    function initMapIfNeeded() {{
      if (mapInstance) return;
      mapInstance = L.map('athen-map', {{
        center: [HOME_BASE.lat, HOME_BASE.lng],
        zoom: 15,
        zoomControl: true
      }});
      updateMapTiles();

      // Home Base Marker
      const homeIcon = L.divIcon({{
        className: 'ocho-pin home-pin',
        html: 'H',
        iconSize: [34, 34],
        iconAnchor: [17, 17]
      }});
      const homeM = L.marker([HOME_BASE.lat, HOME_BASE.lng], {{ icon: homeIcon, zIndexOffset: 1000 }}).addTo(mapInstance);
      homeM.bindPopup(`
        <div style="font-family:'JetBrains Mono',monospace;min-width:210px;">
          <div style="font-size:10px;font-weight:700;opacity:0.7;">[00] EURE HOME BASE</div>
          <div style="font-size:14px;font-weight:700;margin:4px 0;">ATHINUM 1 | KORINNIS 11</div>
          <div style="font-size:11px;margin-bottom:8px;">Platia Eleftherias / Psyri</div>
          <a href="${{HOME_BASE.gmaps}}" target="_blank" rel="noopener" class="sharp-btn active" style="width:100%;justify-content:center;">GOOGLE MAPS ↗</a>
        </div>
      `);
      markersById['home'] = homeM;

      // All 26 Spot Markers
      SPOTS.forEach(s => {{
        const icon = L.divIcon({{
          className: 'ocho-pin',
          html: s.num_str,
          iconSize: [28, 28],
          iconAnchor: [14, 14]
        }});
        const m = L.marker([s.lat, s.lng], {{ icon }}).addTo(mapInstance);
        m.bindPopup(`
          <div style="font-family:'JetBrains Mono',monospace;min-width:230px;">
            <div style="font-size:10px;font-weight:700;opacity:0.75;">#${{s.num_str}} · ${{s.district}}</div>
            <div style="font-family:'Space Grotesk',sans-serif;font-size:15px;font-weight:700;margin:3px 0;">${{s.title}}</div>
            <div style="font-size:11px;margin-bottom:6px;">${{s.walk_text}} ab Apartment · ${{s.food_status}}</div>
            <div style="font-size:11px;opacity:0.85;margin-bottom:10px;"><strong>Tipp:</strong> ${{s.signature}}</div>
            <div style="display:flex;gap:6px;">
              <button class="sharp-btn active" style="flex:1;justify-content:center;" onclick="openDrawer(${{s.id}})">DOSSIER</button>
              <a class="sharp-btn" href="${{s.gmaps}}" target="_blank" rel="noopener">MAPS ↗</a>
            </div>
          </div>
        `);
        markersById[s.id] = m;
      }});
    }}

    function showSpotOnMap(spotId) {{
      const s = SPOTS.find(x => x.id === spotId);
      if (!s) return;
      switchView('map');
      setTimeout(() => {{
        mapInstance.setView([s.lat, s.lng], 17, {{ animate: true }});
        if (markersById[spotId]) markersById[spotId].openPopup();
      }}, 120);
    }}

    function focusHomeBase() {{
      initMapIfNeeded();
      mapInstance.setView([HOME_BASE.lat, HOME_BASE.lng], 16, {{ animate: true }});
      if (markersById['home']) markersById['home'].openPopup();
    }}

    function fitAllMarkers() {{
      initMapIfNeeded();
      const latlngs = [[HOME_BASE.lat, HOME_BASE.lng], ...SPOTS.map(s => [s.lat, s.lng])];
      mapInstance.fitBounds(latlngs, {{ padding: [30, 30] }});
    }}

    function locateUser() {{
      initMapIfNeeded();
      const statusEl = document.getElementById('gpsStatus');
      if (!navigator.geolocation) {{
        statusEl.textContent = 'GPS wird vom Browser nicht unterstützt.';
        return;
      }}
      statusEl.textContent = 'Orte GPS-Signal...';
      navigator.geolocation.getCurrentPosition(pos => {{
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        if (userMarker) mapInstance.removeLayer(userMarker);
        const uIcon = L.divIcon({{
          className: 'ocho-pin',
          html: 'GPS',
          iconSize: [36, 28],
          iconAnchor: [18, 14]
        }});
        userMarker = L.marker([lat, lng], {{ icon: uIcon }}).addTo(mapInstance);
        userMarker.bindPopup('<strong>DEIN AKTUELLER STANDORT</strong>').openPopup();
        mapInstance.setView([lat, lng], 16);
        statusEl.textContent = `GPS aktiv (${{lat.toFixed(4)}}, ${{lng.toFixed(4)}})`;
      }}, () => {{
        statusEl.textContent = 'GPS-Zugriff nicht freigegeben.';
      }}, {{ enableHighAccuracy: true, timeout: 8000 }});
    }}

    // KEYBOARD SHORTCUTS
    document.addEventListener('keydown', e => {{
      if (e.key === 'Escape') {{
        if (document.getElementById('lightbox').classList.contains('open')) {{
          closeLightbox();
        }} else if (document.getElementById('dossierDrawer').classList.contains('open')) {{
          closeDrawer();
        }}
      }} else if (document.getElementById('dossierDrawer').classList.contains('open')) {{
        if (e.key === 'ArrowLeft') prevNextSpot(-1);
        if (e.key === 'ArrowRight') prevNextSpot(1);
      }}
    }});

    // INITIALIZE
    (function init() {{
      const savedTheme = localStorage.getItem('ocho_theme') || 'dark';
      applyTheme(savedTheme);
      const savedPhotos = localStorage.getItem('ocho_photos') || 'bw';
      if (savedPhotos === 'color') {{
        document.body.classList.add('color-photos');
        document.getElementById('photoModeLabel').textContent = '[FARBE]';
      }}
      renderSpots();
      renderRoutes();
    }})();
  </script>
</body>
</html>
"""
    out_path = os.path.join(BASE_DIR, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_doc)
    return out_path


def main():
    spots = parse_all_dossiers()
    master_raw = open(os.path.join(BASE_DIR, "00_Athen_Master_Context.md"), encoding="utf-8").read()
    # Strip YAML frontmatter
    master_body = re.sub(r'^---\n.*?\n---\n+', '', master_raw, flags=re.S)
    master_html = markdown.markdown(master_body, extensions=['extra', 'sane_lists'])
    master_html = master_html.replace('<a href="http', '<a target="_blank" rel="noopener" href="http')

    kml_path = generate_kml(spots)
    html_path = build_html(spots, master_html)
    total_imgs = sum(len(s["images"]) for s in spots)
    print(f"Built {{html_path}} ({{os.path.getsize(html_path):,}} bytes) with {{len(spots)}} dossiers and {{total_imgs}} linked photos.")
    print(f"Built {{kml_path}} ({{os.path.getsize(kml_path):,}} bytes).")


if __name__ == "__main__":
    main()
