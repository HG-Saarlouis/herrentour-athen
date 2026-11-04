#!/usr/bin/env python3
"""
OCHO HERRENTOUR — ATHEN 2026
Static Web-App & KML Generator (build.py)
Reads 00_Athen_Master_Context.md + dossiers/01..34.md + images/
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

# Curated tactical metadata + exact coordinates for all 34 dossiers
SPOT_META = {
    1: {
        "short_title": "BIOS",
        "subtitle": "Legendäre Dachterrasse mit unverbautem Akropolis-Blick & ehrlichen Drinks im Liegestuhl",
        "district": "Psyri / West",
        "district_tag": "psyri",
        "cats": ["rooftop", "late", "cocktails"],
        "cat_label": "ROOFTOP / SPÄTNACHT & DRINKS",
        "address": "Pireos 84, 104 35 Athen",
        "walk_min": 5,
        "walk_text": "400 m · 5 Min.",
        "hours_short": "Tägl. 10:00–02:00 (Fr/Sa bis 03:00)",
        "food_status": "SNACKS ONLY",
        "food_note": "Reine Tränke für den Durst — die Grundlage schaffen wir uns vorher im Kiez!",
        "signature": "Eiskalter Papoto-Slush (mit echtem Eis am Stiel im Glas!) & frisch gezapftes Fassbier",
        "insider": "Wir nehmen den Seiteneingang auf der Salaminos 13 und fahren direkt hoch aufs Dach: 5 Minuten vorm Bett noch ein letztes Glas mit beleuchteter Akropolis vor der Nase.",
        "lat": 37.97918,
        "lng": 23.71915,
    },
    2: {
        "short_title": "UPUPA EPOPS",
        "subtitle": "Prachtvoller 1930er-Innenhof für den ersten großen Durst & handgemachte Bar-Küche",
        "district": "Petralona",
        "district_tag": "petralona",
        "cats": ["cocktails", "daydrinking"],
        "cat_label": "COCKTAILS / HOF & DAYDRINKING",
        "address": "Alkminis 7, 118 54 Kato Petralona",
        "walk_min": 20,
        "walk_text": "1,6 km · 20 Min.",
        "hours_short": "Tägl. 10:00–02:00 (Fr/Sa bis 03:00)",
        "food_status": "BARFOOD / PIZZA",
        "food_note": "Deftiges Barfood & knusprige Sauerteig-Pizza bis nach Mitternacht (00:30 Uhr)",
        "signature": "Upupa Epops Haus-Cocktail im großen Kelch & Trüffel-Pilz-Pinsa zum Teilen",
        "insider": "Drei zusammengebaute 1930er-Steinhäuser voller Charakter: Unser perfekter Auftakt auf der West-Route, bevor wir 400 Meter weiter ins Line Athens marschieren.",
        "lat": 37.97152,
        "lng": 23.71184,
    },
    3: {
        "short_title": "LINE ATHENS",
        "subtitle": "Weltklasse-Barhandwerk (#6 World's 50 Best Bars) mit eigener Braukunst & hoher Trinkkultur",
        "district": "Petralona",
        "district_tag": "petralona",
        "cats": ["50best", "cocktails", "late"],
        "cat_label": "EU'S 50 BEST / HIGH-END BAR",
        "address": "Agathodaimonos 37, 118 53 Kato Petralona",
        "walk_min": 22,
        "walk_text": "1,7 km · 22 Min.",
        "hours_short": "Mo–Do 17:00–02:00 · Fr 17:00–03:00 · Sa/So ab 10:30",
        "food_status": "GASTRO BARFOOD",
        "food_note": "Hauseigene Sauerteig-Bäckerei & handgemachte Bar-Klassiker auf Spitzenniveau",
        "signature": "Hausgemachte Fruchtweine ('Why Not' Erdbeer/Feige/Granatapfel) & der legendäre 'Line's Hot Dog'",
        "insider": "Riesige historische Werkhalle mit ordentlich Wumms: Ab 21:30 Uhr dreht der DJ auf, und wir stehen goldrichtig an der langen Tafel.",
        "lat": 37.96885,
        "lng": 23.70995,
    },
    4: {
        "short_title": "TAF (THE ART FOUNDATION)",
        "subtitle": "Versteckter historischer Innenhof von 1870 & urige Traditions-Bar mitten im Trubel",
        "district": "Monastiraki / Psyri",
        "district_tag": "monastiraki",
        "cats": ["daydrinking", "cocktails", "late"],
        "cat_label": "HISTORISCHER HOF / KULT-BAR",
        "address": "Normanou 5, 105 55 Monastiraki",
        "walk_min": 10,
        "walk_text": "800 m · 10 Min.",
        "hours_short": "Mo–Do 11:00–02:00 · Fr/Sa bis 03:00",
        "food_status": "DRINKS ONLY",
        "food_note": "Hier wird flüssig ernährt — gegessen haben wir vorher ordentlich in Psyri!",
        "signature": "Starker Freddo Espresso am Nachmittag · Eiskalte Highballs & ehrliche Gin-Tonics bei Nacht",
        "insider": "Einfach durch den unscheinbaren Torbogen auf der Flohmarktgasse Normanou 5 schlüpfen — und falls wir Höhenluft wollen, liegt Couleur Locale direkt Haus an Haus auf der Nr. 3!",
        "lat": 37.97622,
        "lng": 23.72438,
    },
    5: {
        "short_title": "COULEUR LOCALE",
        "subtitle": "Sonniges Panorama-Dach mit Postkartenblick auf die Akropolis & besten Sundowner-Drinks",
        "district": "Monastiraki",
        "district_tag": "monastiraki",
        "cats": ["rooftop", "daydrinking", "cocktails"],
        "cat_label": "ROOFTOP / SUNDOWNER & DRINKS",
        "address": "Normanou 3, 105 55 Monastiraki",
        "walk_min": 10,
        "walk_text": "800 m · 10 Min.",
        "hours_short": "Tägl. 09:30–02:00 (Fr/Sa bis 03:00)",
        "food_status": "BRUNCH & BARFOOD",
        "food_note": "Solide Stärkung mit Burgern, Pinsa & Fingerfood direkt zum Glas",
        "signature": "Erfrischender Mediterranean Mule & die volle Ladung Akropolis-Abendsonne um 17:00 Uhr",
        "insider": "Rein in die Ladenpassage Normanou 3 und mit dem Aufzug in den 3. Stock: Dank Windschutz und Heizstrahlern sitzen wir hier auch im November wie die Könige.",
        "lat": 37.97628,
        "lng": 23.72452,
    },
    6: {
        "short_title": "360 COCKTAIL BAR",
        "subtitle": "Riesiger Dachgarten direkt über dem Monastiraki-Platz für die große Herrenrunde",
        "district": "Monastiraki",
        "district_tag": "monastiraki",
        "cats": ["rooftop", "cocktails", "daydrinking"],
        "cat_label": "ROOFTOP-GARTEN / PANORAMA-BAR",
        "address": "Ifestou 2, 105 55 Monastiraki",
        "walk_min": 10,
        "walk_text": "820 m · 10 Min.",
        "hours_short": "Tägl. 09:00–03:00 (Fr/Sa bis 04:00)",
        "food_status": "FULL RESTAURANT",
        "food_note": "Warme Küche und handfeste Bar-Snacks für den kleinen oder großen Hunger zwischendurch",
        "signature": "360 Passion & würzige Mastiha-Cocktails direkt an der runden 360°-Insel-Theke",
        "insider": "Mit 8 Mann steuern wir ohne Umwege die langen Hochtische an der offenen Bar an — kein Reservierungsstress, beste Aussicht, volle Gläser.",
        "lat": 37.97621,
        "lng": 23.72548,
    },
    7: {
        "short_title": "THE CLUMSIES",
        "subtitle": "Legendäre All-Day-Herrenhaus-Bar aus den internationalen Top-Rankings mit Vollgas-Gastfreundschaft",
        "district": "Zentrum / Psyri",
        "district_tag": "zentrum",
        "cats": ["50best", "cocktails", "daydrinking", "late"],
        "cat_label": "EU'S 50 BEST / HERRENHAUS-BAR",
        "address": "Praxitelous 30, 105 61 Athen",
        "walk_min": 9,
        "walk_text": "750 m · 9 Min.",
        "hours_short": "Tägl. 10:00–02:00 (Fr/Sa bis 04:00)",
        "food_status": "BRUNCH & BARFOOD",
        "food_note": "Erstklassiges Barfood bis 23:30 Uhr, falls der Magen beim zweiten Negroni knurrt",
        "signature": "Aegean Negroni (mit Fenchel, Mastiha & Diktamos) & Popeye Smash — da bleibt kein Auge trocken",
        "insider": "Donnerstagabend zwischen 19:00 und 21:30 Uhr marschieren wir hier ganz entspannt ohne Wochenend-Schlange rein und kapern die lange Holztheke oder den warmen Innenhof.",
        "lat": 37.97896,
        "lng": 23.72942,
    },
    8: {
        "short_title": "BABA AU RUM",
        "subtitle": "Athens oberster Rum- & Tiki-Tempel (#14 Europe's 50 Best Bars) für hochprozentige Seefahrer-Laune",
        "district": "Zentrum",
        "district_tag": "zentrum",
        "cats": ["50best", "cocktails", "late"],
        "cat_label": "EU'S 50 BEST / RUM & TIKI",
        "address": "Klitiou 6, 105 60 Athen",
        "walk_min": 11,
        "walk_text": "850 m · 11 Min.",
        "hours_short": "So–Fr 19:00–03:00 · Sa 19:00–03:30",
        "food_status": "DRINKS ONLY",
        "food_note": "Reine Edel-Tränke mit Nüssen und Oliven — der Rum hat hier das alleinige Sagen",
        "signature": "Baba Zombie (Vorsicht, Umdrehungen!), Mai Tai nach 1944er-Originalrezept & Spicy Baba",
        "insider": "Mit unserer 8er-Truppe stellen wir uns abends standesgemäß an die Stehtische auf der Fußgängerzone Klitiou — und bis zur Bar in Front of the Bar sind es nur 90 Meter!",
        "lat": 37.97748,
        "lng": 23.72985,
    },
    9: {
        "short_title": "THE BAR IN FRONT OF THE BAR",
        "subtitle": "Legendäre Straßenbar & verstecktes Speakeasy (#2 Europe's 50 Best Bars) mit täglich wechselnder Karte",
        "district": "Zentrum",
        "district_tag": "zentrum",
        "cats": ["50best", "cocktails", "late"],
        "cat_label": "#2 EU'S 50 BEST / STREET BAR",
        "address": "Petraki 1, 105 63 Athen",
        "walk_min": 12,
        "walk_text": "950 m · 12 Min.",
        "hours_short": "Tägl. 18:00–02:00/03:00",
        "food_status": "DRINKS ONLY",
        "food_note": "Hier zählt nur das flüssige Handwerk direkt auf der Gasse",
        "signature": "Täglich komplett neue 8-Drinks-Karte, serviert in auf -24 °C tiefgefrorenen Gläsern",
        "insider": "Zwei Fliegen mit einer Klappe: Vorne auf der Fußgängerzone Petraki perfektes Stehtrinken für 8 Mann, und hinter der Spiegeltür wartet die Geheimbar 'Rumble in the Jungle'.",
        "lat": 37.97654,
        "lng": 23.73162,
    },
    10: {
        "short_title": "BARRO NEGRO",
        "subtitle": "Athens erste Adresse für Tequila, Mezcal & Weltklasse-Palomas (#13 Europe's 50 Best Bars)",
        "district": "Zentrum",
        "district_tag": "zentrum",
        "cats": ["50best", "cocktails", "late"],
        "cat_label": "EU'S 50 BEST / AGAVE & PALOMA",
        "address": "Ioannou Paparrigopoulou 15, 105 61 Athen",
        "walk_min": 10,
        "walk_text": "800 m · 10 Min.",
        "hours_short": "Mo–Do 18:00–02:00 · Fr 18:00–03:00 · Sa/So ab 16:00",
        "food_status": "DRINKS ONLY",
        "food_note": "Reine Agaven-Botschaft — hier wird der Durst mexikanisch-griechisch gelöscht",
        "signature": "Barro Negro Paloma (11 €), rauchiger Mezcal Negroni & würzige Michelada (7 €)",
        "insider": "Liegt direkt neben dem Black Duck Garden und nur 100 Meter vom Clumsies entfernt — ideal für einen strammen Boxenstopp auf unserer Zentrum-Runde.",
        "lat": 37.97938,
        "lng": 23.73082,
    },
    11: {
        "short_title": "BLACK DUCK GARDEN",
        "subtitle": "Versteckter Palmen-Innenhof von 1836 für den gepflegten ersten Anstoß nach der Landung",
        "district": "Zentrum",
        "district_tag": "zentrum",
        "cats": ["daydrinking", "food", "cocktails"],
        "cat_label": "PALMEN-HOF / BISTRO & DRINKS",
        "address": "Ioannou Paparrigopoulou 5–7, 105 61 Athen",
        "walk_min": 10,
        "walk_text": "820 m · 10 Min.",
        "hours_short": "Tägl. 10:00–01:00 (Fr/Sa bis 02:00)",
        "food_status": "BISTRO & PLATTERS",
        "food_note": "Deftige Käse- und Wurstplatten sowie warme Bistro-Küche unter freiem Himmel",
        "signature": "Große Wein- und Käseplatte für die ganze Tafel unterm historischen Palmenbaum von Königin Amalia",
        "insider": "Unser perfekter erster Landeplatz am Donnerstagnachmittag um 16:30 Uhr: Ankommen, Gläser heben und den Reisestaub runterspülen.",
        "lat": 37.97912,
        "lng": 23.73118,
    },
    12: {
        "short_title": "TALES OF ALES",
        "subtitle": "Ehrliche Hopfen-Oase mit 10 frisch gezapften Fassbieren & über 170 griechischen Brauerei-Dosen",
        "district": "Commercial Triangle / Syntagma",
        "district_tag": "zentrum",
        "cats": ["beer", "daydrinking", "late"],
        "cat_label": "CRAFT BEER / ZAPFHAHN & FLASCHEN",
        "address": "Miltiadou 19, 105 60 Athen",
        "walk_min": 8,
        "walk_text": "750 m · 8 Min.",
        "hours_short": "Mo–Do 14:00–01:00 · Fr/Sa 14:00–02:00 · So 17:00–01:00",
        "food_status": "STREETFOOD NEXT DOOR",
        "food_note": "Genialer Schachzug: Gegenüber auf der Nr. 22 heißes 'Feta Me Meli' im knusprigen Filo-Hörnchen zum Bier holen!",
        "signature": "Frisch gezapftes Strange Brew 'Jasmine IPA', Seven Islands & Kykao direkt vom Hahn",
        "insider": "Sitzt mitten im Bermudadreieck zwischen Clumsies (90 m) und Baba au Rum (140 m) — wenn wir zwischen zwei Cocktails mal ein ehrliches Herrenpils brauchen, sind wir hier daheim.",
        "lat": 37.97765,
        "lng": 23.72940,
    },
    13: {
        "short_title": "AVLI PSYRRI",
        "subtitle": "Uriges weiß-blaues Hinterhof-Kafeneio seit 1985 — wie eine geheime griechische Insel mitten in Psyri",
        "district": "Psyri (Home-Kiez)",
        "district_tag": "psyri",
        "cats": ["food", "daydrinking"],
        "cat_label": "URIGER HINTERHOF / MEZEDOPOLEIO",
        "address": "Agiou Dimitriou 12, 105 54 Psyri",
        "walk_min": 5,
        "walk_text": "550 m · 5 Min.",
        "hours_short": "Mi–Mo 13:00–02:00 (Di geschlossen)",
        "food_status": "FULL MEZE TABLE",
        "food_note": "Handfeste Pfannen-Meze für schlanke 4–7 € pro Teller — hier wird der ganze Tisch vollgepackt!",
        "signature": "Brutzelnde Tigania (Schweinefleisch aus der Gusseisenpfanne), würzige Keftedes & Tsipouro auf Eis",
        "insider": "Aufgepasst beim Eingang: Wir müssen durch die schmale blaue Eisentür auf der Agiou Dimitriou 12 (nicht Agion Anargyron!). Keine Reservierung, Bares in die Tasche und rein ins Glück.",
        "lat": 37.97815,
        "lng": 23.72555,
    },
    14: {
        "short_title": "AMA LACHEI (STIS NEFELIS)",
        "subtitle": "Herrliches Meze-Gelage im begrünten Pausenhof einer alten Grundschule",
        "district": "Exarchia",
        "district_tag": "exarchia",
        "cats": ["food", "daydrinking"],
        "cat_label": "MEZE-TAFEL / SCHULHOF-GARTEN",
        "address": "Kallidromiou 69, 106 83 Exarchia",
        "walk_min": 22,
        "walk_text": "1,9 km · 22 Min. (6 Min. Uber)",
        "hours_short": "Mo–Mi 12:00–23:30 · Do–So 12:00–00:00",
        "food_status": "FULL MEZE FEAST",
        "food_note": "Üppige griechisch-kretische Sharing-Tafel — draußen unterm Blätterdach oder drinnen in den alten Klassenzimmern",
        "signature": "Geschmolzener Mastelo-Grillkäse mit Tomatenmarmelade, geräuchertes Apaki & butterzartes Schmorfleisch",
        "insider": "Nachsitzen war noch nie so schön: Unser Pflicht-Stopp nach dem Samstagsmarkt auf der Kallidromiou. Für 8 hungrige Ochos rufen wir kurz vorher durch (+30 210 3845978).",
        "lat": 37.98692,
        "lng": 23.73815,
    },
    15: {
        "short_title": "PHARAOH",
        "subtitle": "Archaische Holzfeuer-Küche (Michelin Bib Gourmand), 400+ Weine & satter Vinyl-Sound",
        "district": "Exarchia",
        "district_tag": "exarchia",
        "cats": ["food", "wine"],
        "cat_label": "HOLZFEUER-KÜCHE / WEIN & VINYL",
        "address": "Solomou 54, 106 82 Exarchia",
        "walk_min": 13,
        "walk_text": "1,2 km · 13 Min.",
        "hours_short": "Mo–Do 17:30–02:00 · Fr/Sa 13:30–02:00 (So zu!)",
        "food_status": "MICHELIN WOODFIRE",
        "food_note": "Hier wird ohne Strom und Gas ausschließlich über offenem Olivenholzfeuer und im Holzofen gekocht",
        "signature": "Warmes Sauerteigbrot mit geräucherter Butter, knusprige Hortopita aus dem Ofen & charakterstarker griechischer Wein",
        "insider": "Selbst wenn die Tische voll sind: Ab 21:30 Uhr kapern wir einfach als Walk-in die breite Edelstahl-Theke direkt vor dem offenen Feuer und der Plattensammlung!",
        "lat": 37.98542,
        "lng": 23.72995,
    },
    16: {
        "short_title": "TANINI AGAPI MOU",
        "subtitle": "Herzliche, bodenständige griechische Weinbar mit über 100 offenen Tropfen & Fasswein",
        "district": "Exarchia",
        "district_tag": "exarchia",
        "cats": ["wine", "daydrinking"],
        "cat_label": "WEINBAR / 100+ OFFENE WEINE",
        "address": "Ippokratous 91 & Methonis, 106 80 Exarchia",
        "walk_min": 22,
        "walk_text": "1,9 km · 22 Min.",
        "hours_short": "So–Do 17:00–01:00 · Fr/Sa 17:00–02:00",
        "food_status": "PINSA & PLATTERS",
        "food_note": "Ofenfrische Sauerteig-Pinsa und reich beladene griechische Käse- und Wurstbretter",
        "signature": "Süffiger Orange Wine vom Fass (6,50 €), kräftige Xinomavro-Runde & Trüffel-Pinsa",
        "insider": "Null Wein-Snobismus, 100 % Trinkfreude: Jede einzelne der über 100 Flaschen machen sie uns auch glasweise auf!",
        "lat": 37.98562,
        "lng": 23.73992,
    },
    17: {
        "short_title": "ROZALIA EXARCHIA",
        "subtitle": "Legendäre Traditions-Taverne seit 1978 mit dem berühmten 16er-Vorspeisen-Silbertablett",
        "district": "Exarchia",
        "district_tag": "exarchia",
        "cats": ["food"],
        "cat_label": "TRADITIONS-TAVERNE / MEZE-TABLETT",
        "address": "Valtetsiou 54–59, 106 81 Exarchia",
        "walk_min": 19,
        "walk_text": "1,7 km · 19 Min.",
        "hours_short": "Tägl. 12:00–01:00 (Fr/Sa bis 02:00)",
        "food_status": "FULL TAVERNA",
        "food_note": "Warme Hausmannskost bis tief in die Nacht — wie geschaffen für acht hungrige Männer",
        "signature": "Einmal quer übers große 16-Teller-Vorspeisentablett zeigen + butterweiches Lamm im Pergamentpapier",
        "insider": "Auf der belebten Fußgängerzone Valtetsiou gehört Rozalia quasi die halbe Straße — und zum Nachspülen liegt strakastrüka nur 60 Meter weiter!",
        "lat": 37.98578,
        "lng": 23.73512,
    },
    18: {
        "short_title": "STRAKASTRÜKA",
        "subtitle": "Ehrliche Rock-Kneipe mit 9 griechischen Craft-Beer-Hähnen im lebendigen Ausgehviertel",
        "district": "Exarchia",
        "district_tag": "exarchia",
        "cats": ["beer", "late"],
        "cat_label": "CRAFT BEER / ROCK-KNEIPE",
        "address": "Andrea Metaxa 19, 106 81 Exarchia",
        "walk_min": 19,
        "walk_text": "1,7 km · 19 Min.",
        "hours_short": "Di–Do 18:00–01:00 · Fr/Sa 16:00–03:00 · So 16:00–01:00 (Mo zu)",
        "food_status": "HOT DOGS & BARFOOD",
        "food_note": "Handfester 'Straka Hot Dog' im Brioche-Brötchen & knusprige Bar-Pizza zum Bier",
        "signature": "Frisch Gezapftes von 9 griechischen Hähnen (Voreia Stout, Jasmine IPA, Kyria Toula) + Straka Hot Dog",
        "insider": "Liegt direkt am Eck zur Fußgängerzone Valtetsiou, keine 60 Meter neben Rozalia: Nach dem Tavernen-Festmahl rollen wir hier direkt an die Zapfhähne.",
        "lat": 37.98542,
        "lng": 23.73510,
    },
    19: {
        "short_title": "KLIMATARIA",
        "subtitle": "Urige Weinfass-Taverne seit 1927 mit schweren Schmortöpfen & handgemachter Live-Musik",
        "district": "Psyri / Markt (Home-Kiez)",
        "district_tag": "psyri",
        "cats": ["food", "wine"],
        "cat_label": "WEINFASS-TAVERNE / LIVE-MUSIK",
        "address": "Platia Theatrou 2, 105 52 Athen",
        "walk_min": 2,
        "walk_text": "180 m · 2 Min.!",
        "hours_short": "Di–So 12:00–01:00/02:00 (Mo geschlossen)",
        "food_status": "FULL FEAST / GASTRA",
        "food_note": "Stundenlang geschmorte Schweinshaxe und Lammkeule aus dem traditionellen Gastra-Schmortopf",
        "signature": "Kotsi (riesige Schweinshaxe) & Lamm mit Zitronenkartoffeln + kühler Fasswein zwischen den alten Holzfässern",
        "insider": "Lächerliche 180 Meter von unserem Apartment entfernt! Wetterfester, beheizter Hof, Live-Bouzouki und am Ende nur zwei Minuten Heimweg ins Bett.",
        "lat": 37.98042,
        "lng": 23.72485,
    },
    20: {
        "short_title": "DIPORTO",
        "subtitle": "Legendäre schilderlose Kellertaverne von 1887 — authentischer geht Athen nicht!",
        "district": "Psyri / Markt (Home-Kiez)",
        "district_tag": "psyri",
        "cats": ["food", "daydrinking"],
        "cat_label": "KELLER-LEGENDE VON 1887 / MITTAGS",
        "address": "Sokratous 9 & Theatrou, 105 52 Athen",
        "walk_min": 2,
        "walk_text": "200 m · 2 Min.!",
        "hours_short": "Mo–Sa ca. 10:00–18:00 (So geschlossen)",
        "food_status": "NO-MENU LUNCH",
        "food_note": "Keine Speisekarte, kein Schnickschnack: Es kommt heiß auf den Tisch, was morgens im Kessel schmort",
        "signature": "Deftiger Kichererbseneintopf (Revithia), krosse Sardinen, Fava & eiskalter Fass-Retsina aus dem Blechkrug",
        "insider": "Zwei Minuten ab Haustür die steile Steintreppe in den historischen Weinkeller hinabsteigen, Bargeld bereithalten und den besten Mittags-Boxenstopp der Stadt feiern.",
        "lat": 37.98035,
        "lng": 23.72512,
    },
    21: {
        "short_title": "TA KARAMANLIDIKA TOU FANI",
        "subtitle": "Paradies für Pfannen-Meze, luftgetrockneten Pastirma-Schinken & edle Tropfen direkt ums Eck",
        "district": "Psyri / Markt (Home-Kiez)",
        "district_tag": "psyri",
        "cats": ["food", "daydrinking", "wine"],
        "cat_label": "FEINKOST-TAVERNE & PFANNEN-MEZE",
        "address": "Sokratous 1 & Evripidou 52 (+ Ermou 119)",
        "walk_min": 4,
        "walk_text": "300 m · 4 Min.",
        "hours_short": "Sokratous: Mo–Sa 12–23 · Ermou 119: Mo–So 12–23!",
        "food_status": "FULL MEZE & DELI",
        "food_note": "Heiße Gusseisenpfannen, würzige Reifewürste, Bergkäse & zum Abschied Karottenhalva aufs Haus",
        "signature": "Sahanaki Karamanlidiko (Pastirma, Sudjuk & Spiegeleier brutzeln in der Pfanne) + gereifter Tsipouro",
        "insider": "Keine 4 Minuten vom Apartment: Wenn das Stammhaus Sokratous 1 am Sonntag pausiert, hat das Schwesterhaus 'Ergastiri' auf der Ermou 119 trotzdem für uns offen!",
        "lat": 37.98018,
        "lng": 23.72615,
    },
    22: {
        "short_title": "FEYROUZ",
        "subtitle": "Handgerolltes Steinofen-Lahmacun — unsere schnellste und beste Grundlage vor der Bar-Tour",
        "district": "Zentrum / Monastiraki",
        "district_tag": "zentrum",
        "cats": ["food", "daydrinking"],
        "cat_label": "STEINOFEN-STREETFOOD / HANDGEMACHT",
        "address": "Karori 23 & Agathonos 1, 105 51 Athen",
        "walk_min": 8,
        "walk_text": "650 m · 8 Min.",
        "hours_short": "Mo–Do 12:00–22:00 · Fr/Sa 12:00–23:00 (So zu)",
        "food_status": "BEST STREETFOOD",
        "food_note": "Unschlagbare 15-Minuten-Unterlage (ca. 5,50 €) direkt auf die Hand, bevor es an die großen Theken geht",
        "signature": "Feyrouz Lahmacun mit geräuchertem Babaganoush, Pastirma-Peinirli (Teigschiffchen) & heißes Künefe",
        "insider": "Liegt nur 160 Meter neben The Clumsies und Tales of Ales — hier tanken wir in Rekordzeit auf, damit später kein Ocho bei den Cocktails schwächelt.",
        "lat": 37.97762,
        "lng": 23.72812,
    },
    23: {
        "short_title": "BOLIVAR BEACH CLUB",
        "subtitle": "Weitläufige Palmen-Landzunge an der Athener Riviera für Seeluft & den ersten Drink am Meer",
        "district": "Riviera (Alimos)",
        "district_tag": "riviera",
        "cats": ["daydrinking", "food"],
        "cat_label": "RIVIERA-LANDZUNGE / STRAND-DRINKS",
        "address": "Akti tou Iliou, 174 55 Alimos",
        "walk_min": 14,
        "walk_text": "10,6 km · 14 Min. Uber",
        "hours_short": "So–Do 08:00–20:00 · Fr/Sa 08:00–05:00",
        "food_status": "BEACH RESTAURANT",
        "food_note": "Überdachter Holz-Pavillon mit Meeresfrüchten, saftigen Burgern & kühlen Getränken direkt am Strand",
        "signature": "Runde über die Landzunge drehen + eiskalter Freddo Cappuccino oder das erste Helle mit Wellenblick",
        "insider": "Im November lassen wir die Badehose im Koffer: Erst hier bei Herbstsonne die Meeresbrise schnuppern und dann zum Sonnenuntergang 250 Meter weiter ins Peñarrubia ziehen!",
        "lat": 37.90785,
        "lng": 23.71312,
    },
    24: {
        "short_title": "PEÑARRUBIA LOUNGE",
        "subtitle": "Wetterfestes Riviera-Flaggschiff mit großem Holzdeck direkt über der Brandung",
        "district": "Riviera (Alimos)",
        "district_tag": "riviera",
        "cats": ["daydrinking", "food", "cocktails"],
        "cat_label": "RIVIERA SUNSET DECK / ALL-DAY LOUNGE",
        "address": "Leof. Poseidonos 20/43, 174 55 Alimos",
        "walk_min": 14,
        "walk_text": "10,4 km · 14 Min. Uber",
        "hours_short": "365 Tage/Jahr · Tägl. 08:30–02:00 (0 € Eintritt)",
        "food_status": "FULL ALL-DAY MENU",
        "food_note": "Durchgehend warme Küche mit Black-Angus-Burgern, Pinsa, Steaks & Sushi",
        "signature": "Sundowner-Cocktails um Schlag 17:20 Uhr auf dem Holzdeck, wenn die Sonne im Saronischen Golf versinkt",
        "insider": "Unser 100 % wetterfester Küsten-Anker an 365 Tagen im Jahr: Selbst wenn im November eine steife Brise weht, sitzen wir hier hinter Glas und unterm Heizstrahler in der ersten Reihe.",
        "lat": 37.90969,
        "lng": 23.71106,
    },
    25: {
        "short_title": "WAREHOUSE EXARCHIA",
        "subtitle": "Lebendige Eck-Institution für starken Kaffee, über 80 offene Weine & erstklassige Bistro-Teller",
        "district": "Exarchia",
        "district_tag": "exarchia",
        "cats": ["wine", "food", "daydrinking"],
        "cat_label": "WEIN-INSTITUTION / ALL-DAY BISTRO",
        "address": "Valtetsiou 21 & Mavromichali 41, 106 80 Exarchia",
        "walk_min": 18,
        "walk_text": "1,6 km · 18 Min.",
        "hours_short": "Tägl. 09:00–02:30 (Küche bis 23:30)",
        "food_status": "GASTRO BISTRO",
        "food_note": "Feine, handfeste Bistro-Küche von Burrata mit Avgotaracho bis zu frischer Pasta und Steaks",
        "signature": "Wein-Runde nach Glas (über 80 offene Positionen!), Burrata-Avgotaracho & starker Freddo Espresso",
        "insider": "Ehemaliges Verlagshaus direkt am Eingang der Fußgängerzone Valtetsiou: Wir schnappen uns draußen die urigen Holzkabeltrommel-Tische und beobachten das bunte Treiben.",
        "lat": 37.98455,
        "lng": 23.73475,
    },
    26: {
        "short_title": "MINU",
        "subtitle": "Grüne Hof-Oase & erstklassiger Kater-Brunch, nur 2 Minuten Stolperdistanz vom Apartment",
        "district": "Psyri (Home-Kiez)",
        "district_tag": "psyri",
        "cats": ["breakfast", "daydrinking", "food"],
        "cat_label": "HOF-BRUNCH & KAFFEE / DIREKT UMS ECK",
        "address": "Sarri 50, 105 53 Psyri",
        "walk_min": 2,
        "walk_text": "190 m · 2 Min.!",
        "hours_short": "Tägl. 08:30–21:30",
        "food_status": "FULL BRUNCH & CAFÉ",
        "food_note": "Rettung am Morgen: Pochierte Eier, Rührei auf Sauerteig, saftiges Katsu Sando & starker Kaffee",
        "signature": "'Happy Egg Bowl', 'Scrambleness' auf Sauerteig, deftiges Pork Katsu Sando & doppelter Freddo Cappuccino",
        "insider": "Einmal aus der Haustür über den Platz fallen und wir sitzen im grünen Innenhof: Perfekt, um nach einer langen Nacht die Lebensgeister der Ochos wieder hochzufahren.",
        "lat": 37.97945,
        "lng": 23.72295,
    },
    27: {
        "short_title": "BREW STR",
        "subtitle": "Ehrlicher Craft-Beer-Boxenstopp mit Zapfhähnen am Übergang von Plaka und Syntagma",
        "district": "Syntagma / Plaka",
        "district_tag": "zentrum",
        "cats": ["beer", "daydrinking"],
        "cat_label": "CRAFT BEER BAR & BOTTLE SHOP",
        "address": "Nikis 50, 105 58 Syntagma / Plaka",
        "walk_min": 15,
        "walk_text": "1,35 km · 15 Min.",
        "hours_short": "Mo–Mi 12:00–23:30 · Do bis 01:00 · Fr/Sa bis 02:00 · So 17:00–23:30",
        "food_status": "BEER SNACKS ONLY",
        "food_note": "Hier geht es ums flüssige Gold vom Fass und aus den Kühlschränken (kleine Snacks zum Bier)",
        "signature": "Frisch gezapfte griechische IPAs & Pale Ales direkt im Stehen auf dem Gehweg der Nikis-Straße",
        "insider": "Genau der richtige Durstlöscher nach dem Akropolis-Spaziergang — und falls jemand in der Gruppe lieber Schaumwein trinkt, liegt Warehouse CO2 nur 120 Meter weiter.",
        "lat": 37.97360,
        "lng": 23.73360,
    },
    28: {
        "short_title": "STRANGE BREW TAPROOM",
        "subtitle": "Offizielles Wohnzimmer der legendären Athener Brauerei mit 10 frischen Zapfhähnen",
        "district": "Koukaki / Süd-Zentrum",
        "district_tag": "zentrum",
        "cats": ["beer"],
        "cat_label": "BRAUEREI-TAPROOM / 10 ZAPFHÄHNE",
        "address": "Falirou 86, 117 41 Koukaki",
        "walk_min": 26,
        "walk_text": "2,3 km · 26 Min.",
        "hours_short": "Mo–Do 17:30–01:00 · Fr 17:30–02:00 · Sa 14:00–02:00 · So 14:00–01:00",
        "food_status": "TAPROOM SNACKS",
        "food_note": "Ehrlicher Brauerei-Ausschank mit Knabbereien zum frisch gezapften Hopfen",
        "signature": "Das berühmte hausgebraute 'Jasmine IPA' (6,2 %), 'Dr. Haze' Double NEIPA & 'Uncle Jam's' direkt ab Quelle",
        "insider": "Überall in Athen trinken wir ihr Jasmine IPA — hier in Koukaki südlich der Akropolis stehen wir direkt an den 10 Hähnen der Braumeister!",
        "lat": 37.96340,
        "lng": 23.72480,
    },
    29: {
        "short_title": "TO SPIRTO & KOLETTI-ACHSE",
        "subtitle": "Ehrliche Kneipenkultur bis 5 Uhr früh & lebendige Straßenbar-Meile für die letzte Runde",
        "district": "Exarchia",
        "district_tag": "exarchia",
        "cats": ["late"],
        "cat_label": "SPÄTNACHT-KNEIPEN / BIS 05:00 UHR",
        "address": "Tzavella 9–13 & Koletti 25–42, 106 81 Exarchia",
        "walk_min": 18,
        "walk_text": "1,6 km · 18 Min.",
        "hours_short": "Mo–Do 12:00–03:00 · Fr/Sa 13:00–05:00 · So 15:00–03:00",
        "food_status": "DRINKS ONLY",
        "food_note": "Klassische Nachtkneipen — die feste Nahrung haben wir vorher bei Rozalia und strakastrüka erledigt",
        "signature": "Anständige Longdrinks (6–7 €) & kaltes Bier im 'to Spirto' oder Blues an der 12-Meter-Holztheke im 'Mavros Gatos'",
        "insider": "Wenn überall sonst schon die Stühle hochgestellt werden, brennt hier am Wochenende bis 05:00 Uhr morgens noch das Licht — keine 3 Minuten vom strakastrüka entfernt.",
        "lat": 37.98485,
        "lng": 23.73365,
    },
    30: {
        "short_title": "SPIRTOKOUTO BAR",
        "subtitle": "Urige 80er/90er-Rock-Kneipe voller Musikkassetten & ehrlicher Tresenkultur bis tief in die Nacht",
        "district": "Kato Petralona",
        "district_tag": "petralona",
        "cats": ["late"],
        "cat_label": "RETRO-ROCK-KNEIPE / SPÄTNACHT-KULT",
        "address": "Keiriadon 15, 118 54 Kato Petralona",
        "walk_min": 20,
        "walk_text": "1,6 km · 20 Min.",
        "hours_short": "So–Do 18:00–02:00 · Fr/Sa 18:00–04:00",
        "food_status": "DRINKS ONLY",
        "food_note": "Reine Spätnacht-Kneipe — gegessen wird vorher im Upupa Epops oder Line Athens",
        "signature": "Eiskaltes Bier, ehrliche Kurze & geradeaus gemixte Longdrinks zwischen tausenden alten Musikkassetten",
        "insider": "Liegt nur 150 Meter neben dem Upupa Epops: Wenn uns auf der West-Route nach Mitternacht noch nach Gitarrenmusik und einem herzhaften Absacker ist, fallen wir hier ein.",
        "lat": 37.97620,
        "lng": 23.71150,
    },
    31: {
        "short_title": "WAREHOUSE CO2",
        "subtitle": "Spritzige Wein- & Schaumwein-Bar unter großen Platanen für den gepflegten Nachmittags-Durst",
        "district": "Syntagma / Plaka",
        "district_tag": "zentrum",
        "cats": ["wine", "daydrinking"],
        "cat_label": "SCHAUMWEIN & WEINBAR / PLATANEN-ECKE",
        "address": "Ypereidou 1 & Nikis 21, 105 58 Syntagma / Plaka",
        "walk_min": 16,
        "walk_text": "1,4 km · 16 Min.",
        "hours_short": "Tägl. 08:30–01:00",
        "food_status": "DELI PLATTERS & BITES",
        "food_note": "Feinkost-Platten, Rinder-Carpaccio, Bruschetta & frische Burrata zum Glas",
        "signature": "Griechische Pet-Nats & Winzer-Schaumweine im offenen Ausschank (29+ Sorten!) + Burrata mit Avgotaracho",
        "insider": "Der kleine Bruder des Warehouse Exarchia unter schattigen Platanen — und für die Biertrinker unter uns liegt Brew Str nur 120 Meter die Straße runter.",
        "lat": 37.97425,
        "lng": 23.73380,
    },
    32: {
        "short_title": "USURUM BRUNCH & COCKTAILS",
        "subtitle": "Großer begrünter Garten-Innenhof & herzhafter Kater-Brunch schon ab 07:30 Uhr morgens",
        "district": "Psyri (Home-Kiez)",
        "district_tag": "psyri",
        "cats": ["breakfast", "daydrinking", "food"],
        "cat_label": "KATER-BRUNCH IM HOF / AB 07:30 UHR",
        "address": "Lepeniotou 19, 105 54 Psyri",
        "walk_min": 3,
        "walk_text": "280 m · 3 Min.",
        "hours_short": "Mo–Fr 07:30–18:00 · Sa/So 07:30–19:00 (Küche bis 17:00)",
        "food_status": "FULL HANGOVER BRUNCH",
        "food_note": "Durchgehend warme Frühstücks- und Brunch-Küche von 07:30 bis 17:00 Uhr für angeschlagene Matrosen",
        "signature": "Würzige Shakshuka-Pfanne, Buttermilk Chicken Waffle, Eggs Benedict auf Sauerteig & eine scharfe Bloody Mary",
        "insider": "Nur 3 Minuten vom Apartment: Sperrt schon um 07:30 Uhr für die Frühaufsteher auf und hat im großen Innenhof immer Platz für unsere komplette 8er-Mannschaft.",
        "lat": 37.97820,
        "lng": 23.72360,
    },
    33: {
        "short_title": "BOUGATSADIKO THESSALONIKI & KOULOURI",
        "subtitle": "Handgeschleuderte Filoteig-Bougatsa am Iroon-Platz & ofenwarme Sesamringe seit 1962",
        "district": "Psyri (Home-Kiez)",
        "district_tag": "psyri",
        "cats": ["breakfast", "food"],
        "cat_label": "HANDWERKS-BÄCKEREI / AB 06:30 UHR",
        "address": "Platia Iroon 1 & Karaiskaki 27, 105 54 Psyri",
        "walk_min": 4,
        "walk_text": "350 m · 4 Min.",
        "hours_short": "Tägl. ab 06:30 / 07:00 Uhr",
        "food_status": "AUTHENTIC STREET BREAKFAST",
        "food_note": "Dampfend heiße Bougatsa aus dem Blech (2,80–4,20 €) & knusprige Sesamringe für ein paar Cent",
        "signature": "Deftige Bougatsa mit Hackfleisch (Kima) oder Feta + süße Grießcreme-Bougatsa & frisches Koulouri nebenan",
        "insider": "Hier fliegt der handgemachte Filoteig morgens noch live durch die Backstube — und 50 Meter weiter auf der Karaiskaki 27 holen wir uns die besten Sesamringe seit 1962.",
        "lat": 37.97810,
        "lng": 23.72485,
    },
    34: {
        "short_title": "GALAKTOPOLEIO I STANI (seit 1931)",
        "subtitle": "Athens letztes historisches Molkerei-Frühstückshaus von 1931 — gelebte Tradition pur",
        "district": "Omonia / Psyri-Nord",
        "district_tag": "psyri",
        "cats": ["breakfast", "food"],
        "cat_label": "TRADITIONS-MOLKEREI SEIT 1931 / FRÜHSTÜCK",
        "address": "Marikas Kotopouli 10, 104 32 Omonia",
        "walk_min": 5,
        "walk_text": "500 m · 5 Min.",
        "hours_short": "Mo–Sa 07:00–22:30 · So 07:30–22:30",
        "food_status": "TRADITIONAL DAIRY & PIES",
        "food_note": "Stichfester Schafsjoghurt, goldene Käsepasteten (Tiropita) & warme Honigbällchen wie vor 90 Jahren",
        "signature": "Schafsjoghurt mit dicker Rahmhaut, Thymianhonig & Walnüssen + frisch ausgebackene Loukoumades",
        "insider": "Seit 1931 in dritter Familiengeneration geführt: Wer morgens in 5 Minuten Fußweg echtes, unverfälschtes Alt-Athen schmecken will, setzt sich hier an die Marmortische.",
        "lat": 37.98410,
        "lng": 23.72690,
    }
}

ROUTES_DATA = [
    {
        "id": "do-a",
        "day": "DONNERSTAG · 05.11.",
        "title": "OPTION A — ZENTRUM & PSYRI-HERRENRUNDE",
        "subtitle": "Kurze Wege ab Basecamp · Ankommen, ehrliche Hof-Drinks, Weltklasse-Tresen & krönender Abschluss",
        "stops": [
            {
                "time": "16:00",
                "name": "TOUCHDOWN @ ATHINUM 1 (KORINNIS 11)",
                "desc": "Einrücken im Hauptquartier! Taschen in die Ecke werfen, kurz frisch machen und bei Bedarf 2 Minuten ums Eck bei Karamanlidika oder Feyrouz den ersten Happen schnappen.",
                "dist": "START · 0 m",
                "spot_id": None
            },
            {
                "time": "16:30 – 19:00",
                "name": "BLACK DUCK GARDEN",
                "desc": "Feucht-fröhlicher Auftakt im versteckten Palmen-Innenhof von 1836: Wir stoßen unter freiem Himmel mit den ersten kühlen Gläsern und großen Käse-/Wurstplatten auf Athen an.",
                "dist": "820 m · 10 Min. Fußweg ab Apartment",
                "spot_id": 11
            },
            {
                "time": "19:00 – 21:30",
                "name": "THE CLUMSIES (+ BARRO NEGRO / TALES OF ALES)",
                "desc": "Donnerstags spazieren wir ohne Wochenend-Schlange direkt ins Herrenhaus: Aegean Negroni an der Holztheke, und wer zwischendurch ein frisch gezapftes IPA oder eine Paloma will, hat Tales of Ales und Barro Negro direkt nebenan.",
                "dist": "180 m · 2 Min. Fußweg",
                "spot_id": 7
            },
            {
                "time": "21:30 – 23:15",
                "name": "AVLI PSYRRI ODER KLIMATARIA",
                "desc": "Deftige Grundlage für acht Männer: Entweder durch die blaue Eisentür in den urigen Hinterhof der Avli Psyrri (heiße Pfannen-Meze & Tsipouro) oder zwischen die riesigen Weinfässer der Klimataria zu Schweinshaxe und Live-Musik.",
                "dist": "350 m · 4 Min. Fußweg",
                "spot_id": 13
            },
            {
                "time": "23:15 – 02:30",
                "name": "TAF & COULEUR LOCALE",
                "desc": "Starker Ausklang im historischen Kopfsteinpflaster-Hof von 1870 oder direkt nebenan mit dem Aufzug aufs Dach von Couleur Locale — beleuchtete Akropolis inklusive.",
                "dist": "350 m · 4 Min. Fußweg (danach 10 Min. heim)",
                "spot_id": 4
            }
        ]
    },
    {
        "id": "do-b",
        "day": "DONNERSTAG · 05.11.",
        "title": "OPTION B — WEST-ROUTE (PETRALONA & BAR-GIGANTEN)",
        "subtitle": "Charakterstarke Höfe, große Handwerkskunst im Glas & ein letzter Absacker über den Dächern",
        "stops": [
            {
                "time": "18:00 – 20:30",
                "name": "UPUPA EPOPS (PETRALONA)",
                "desc": "Wir starten im prächtigen 1930er-Innenhof: Erstklassige Cocktails und ofenfrische Sauerteig-Pinsa schaffen die perfekte Basis für den Abend.",
                "dist": "1,6 km · 20 Min. Fußweg oder 5 Min. Uber",
                "spot_id": 2
            },
            {
                "time": "20:30 – 00:30",
                "name": "LINE ATHENS (#6 WORLD'S 50 BEST)",
                "desc": "5 Minuten weiter in die hohe Backsteinhalle: Wir testen uns durch die hausgemachten Fruchtweine, bestellen den berühmten 'Line's Hot Dog' und feiern ab 21:30 Uhr zum DJ-Set.",
                "dist": "400 m · 5 Min. Fußweg",
                "spot_id": 3
            },
            {
                "time": "00:30 – 02:00",
                "name": "BIOS ROOFTOP (PIREOS 84)",
                "desc": "Liegt goldrichtig auf dem Heimweg zum Basecamp: Ein letzter eiskalter Papoto-Slush oder ein frisch Gezapftes im Liegestuhl mit freiem Blick auf die Akropolis.",
                "dist": "1,3 km Richtung Apartment (danach 5 Min. ins Bett)",
                "spot_id": 1
            }
        ]
    },
    {
        "id": "fr-riviera",
        "day": "FREITAG · 06.11.",
        "title": "KELLER-KULT, RIVIERA-SUNSET & GROSSE COCKTAIL-MEILE",
        "subtitle": "Starker Kater-Brunch, ehrlicher Mittags-Retsina, Sundowner am Meer & Athens beste Theken bei Nacht",
        "stops": [
            {
                "time": "09:30 – 11:30",
                "name": "KATER-BRUNCH: MINU ODER USURUM (PSYRI)",
                "desc": "Keine 3 Minuten aus den Federn: Doppelter Freddo Cappuccino, Shakshuka und Eier-Gerichte im grünen Hof vom Minu oder schon ab 07:30 Uhr im Usurum.",
                "dist": "190 m · 2 Min. ab Apartment",
                "spot_id": 26
            },
            {
                "time": "12:30 – 14:15",
                "name": "DIPORTO ODER TA KARAMANLIDIKA TOU FANI",
                "desc": "Legendäres Mittagsprogramm ums Eck: Entweder Kichererbseneintopf & Fass-Retsina im 1887er-Weinkeller Diporto oder heiße Pastirma-Pfanne mit Tsipouro bei Karamanlidika.",
                "dist": "200 m · 2 Min. ab Apartment",
                "spot_id": 20
            },
            {
                "time": "15:00 – 16:30",
                "name": "BOLIVAR BEACH CLUB (ALIMOS RIVIERA)",
                "desc": "In 14 Minuten per Uber ans Meer: Wir vertreten uns die Beine auf der Palmen-Landzunge und genehmigen uns den ersten Nachmittags-Drink direkt am Wasser.",
                "dist": "10,6 km · 14 Min. Uber (ca. 12–15 €)",
                "spot_id": 23
            },
            {
                "time": "16:30 – 19:30",
                "name": "PEÑARRUBIA LOUNGE (SUNSET UM 17:20 UHR)",
                "desc": "250 Meter weiter am Strand ins wetterfeste Riviera-Flaggschiff: Sundowner-Drinks auf dem großen Holzdeck über den Wellen und deftige Burger als Stärkung.",
                "dist": "250 m · 3 Min. zu Fuß am Wasser",
                "spot_id": 24
            },
            {
                "time": "21:30 – 03:00",
                "name": "COCKTAIL-DREIECK: BABA AU RUM & BAR IN FRONT OF THE BAR",
                "desc": "Zurück im Zentrum (gerne nach schnellem Steinofen-Lahmacun bei Feyrouz): Hochprozentige Rum-Klassiker im Baba au Rum und eiskalte Street-Drinks vor The Bar in Front of the Bar.",
                "dist": "90 m zwischen beiden Bars",
                "spot_id": 9
            }
        ]
    },
    {
        "id": "sa-exarchia",
        "day": "SAMSTAG · 07.11.",
        "title": "EXARCHIA KOMPLETT (WOCHENMARKT, SCHULHOF-MEZE, WEIN & ZAPFHAHN)",
        "subtitle": "Vom bunten Samstagsmarkt über die große Meze-Tafel bis zum ehrlichen Kneipen-Finale",
        "stops": [
            {
                "time": "11:00 – 13:30",
                "name": "KALLIDROMIOU SAMSTAGSMARKT (LAIKI AGORA)",
                "desc": "Wir schlendern mitten durch den berühmten Wochenmarkt auf der Kallidromiou-Straße, probieren uns durch Oliven und Käse und heben den ersten Tsipouro in der Herbstsonne.",
                "dist": "1,9 km ab Apartment (oder nach dem Nationalmuseum)",
                "spot_id": 14
            },
            {
                "time": "13:30 – 16:30",
                "name": "AMA LACHEI (SCHULHOF-MEZE)",
                "desc": "Direkt an der Marktstraße (Kallidromiou 69): Wir lassen den Tisch im begrünten alten Grundschulhof mit Grillkäse, Apaki und geschmortem Lamm volldecken.",
                "dist": "Direkt an der Kallidromiou 69",
                "spot_id": 14
            },
            {
                "time": "16:45 – 18:00",
                "name": "STREFI-HÜGEL (WEGBIER MIT AUSSICHT) ODER WAREHOUSE EXARCHIA",
                "desc": "Entweder 5 Minuten hoch auf den felsigen Strefi-Hügel für den Blick bis zur Akropolis — oder direkt an die Holzkabeltrommeln vorm Warehouse auf der Fußgängerzone Valtetsiou.",
                "dist": "300 m · 4 Min. Fußweg",
                "spot_id": 25
            },
            {
                "time": "18:30 – 21:30",
                "name": "TANINI AGAPI MOU ODER PHARAOH",
                "desc": "Große Weinrunde: Über 100 offene griechische Weine und knusprige Pinsa bei Tanini Agapi Mou oder offenes Olivenholzfeuer und satte Vinyl-Klänge an der Theke im Pharaoh.",
                "dist": "450 m · 5 Min. Fußweg",
                "spot_id": 16
            },
            {
                "time": "21:30 – 23:30",
                "name": "ROZALIA EXARCHIA (16-TELLER-TABLETT)",
                "desc": "Zünftiges Abendmahl in der Traditions-Taverne seit 1978: Das große Silbertablett mit 16 Vorspeisen fährt vor, dazu Lamm im Pergamentpapier.",
                "dist": "450 m · 5 Min. Fußweg",
                "spot_id": 17
            },
            {
                "time": "23:30 – 04:00",
                "name": "STRAKASTRÜKA (ANDREA METAXA 19) & SPIRTO",
                "desc": "Keine 60 Meter neben Rozalia warten 9 frische Craft-Beer-Hähne und der Straka Hot Dog, bevor wir auf der Koletti- und Tzavella-Achse im Spirto die Lichter ausmachen.",
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
            # Skip apartment link as primary if others exist
            if "ATHINUM" in label:
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
            f"<b>Voraussichtliche Zeiten:</b> {s['hours_short']}<br/>"
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
    <name>OCHO HERRENTOUR — ATHEN 2026 (Alle 34 Dossiers + Home Base)</name>
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
<html lang="de" data-theme="light">
<head>
  <meta charset="UTF-8">
  <base href="https://hg-saarlouis.github.io/herrentour-athen/">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
  <meta name="robots" content="noindex, nofollow">
  <meta name="theme-color" content="#F7F7F5">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="default">
  <meta name="apple-mobile-web-app-title" content="OCHOS ATHEN">
  <title>OCHOS — HERRENTOUR ATHEN 2026</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&family=Space+Grotesk:wght@600;700&display=swap" rel="stylesheet">
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
      font-family: 'Inter Tight', -apple-system, BlinkMacSystemFont, sans-serif;
      font-weight: 700;
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
      user-select: text;
      -webkit-user-select: text;
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
      padding: 24px 20px 22px;
    }}

    .masthead-kicker {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: var(--fg-muted);
      margin-bottom: 8px;
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
      font-family: 'Inter Tight', -apple-system, BlinkMacSystemFont, sans-serif;
      font-weight: 700;
      font-size: clamp(2.4rem, 6.8vw, 4.6rem);
      line-height: 0.94;
      letter-spacing: -0.035em;
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

    /* CONTROL BAR (RESET + FILTERS) */
    .controls-panel {{
      background: var(--surface);
      border-bottom: 1px solid var(--border);
    }}

    .reset-full-btn {{
      background: var(--inv-bg);
      color: var(--inv-fg);
      width: 100%;
      padding: 14px 20px;
      border: none;
      border-bottom: 1px solid var(--border);
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      cursor: pointer;
      display: block;
      text-align: center;
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
      background: var(--bg);
      gap: 20px;
      padding: 20px;
      border-bottom: 1px solid var(--border);
    }}
    @media (max-width: 860px) {{
      .spots-grid {{
        grid-template-columns: 1fr;
        gap: 16px;
        padding: 14px;
      }}
    }}

    .spot-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: background 0.12s;
    }}

    .card-top {{
      display: block;
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
      grid-template-columns: 112px 1fr;
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
      justify-content: flex-end;
      align-items: center;
      background: var(--inv-bg);
      color: var(--inv-fg);
      border-bottom: 1px solid var(--border);
      padding: 0;
      min-height: 58px;
      flex-shrink: 0;
    }}
    .drawer-top-actions {{
      display: flex;
      width: 100%;
      height: 58px;
    }}
    .drawer-close-btn {{
      background: var(--inv-bg);
      color: var(--inv-fg);
      width: 100%;
      height: 58px;
      border: none;
      padding: 0 22px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 14px;
      font-weight: 700;
      letter-spacing: 0.12em;
      text-align: center;
      justify-content: center;
      display: flex;
      align-items: center;
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
      font-family: 'Inter Tight', -apple-system, BlinkMacSystemFont, sans-serif;
      font-size: clamp(1.8rem, 4.5vw, 2.75rem);
      font-weight: 700;
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
<body class="color-photos">
  <div class="app-shell">
    <!-- TOP STATUS TICKER -->
    <div class="top-bar">
      <div>ATHEN · 05.11.–08.11.2026</div>
      <div class="top-bar-right">
        <span>BASIS: ATHINUM 1 · KORINNIS 11</span>
      </div>
    </div>

    <!-- ARCHITECTURAL MASTHEAD -->
    <header class="masthead">
      <div class="masthead-main">
        <div class="masthead-kicker">
          <span class="badge">OCHOS</span>
          <span>GASTRO &amp; NIGHTLIFE GUIDE</span>
        </div>
        <h1 class="masthead-title">OCHO HERRENTOUR</h1>
      </div>
      <div class="masthead-actions">
        <button class="ActionBtn" id="themeToggleBtn" onclick="toggleTheme()" title="Light / Dark Mode umschalten">
          <span>MODE</span>
          <span id="themeLabel">[LIGHT]</span>
        </button>
        <button class="ActionBtn" id="photoModeBtn" onclick="togglePhotoColor()" title="Fotos S/W oder Farbe">
          <span>FOTOS</span>
          <span id="photoModeLabel">[FARBE]</span>
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
          <span>DOSSIERS</span>
        </button>
        <button class="mode-tab" data-view="map" onclick="switchView('map')">
          <span>KARTE</span>
        </button>
        <button class="mode-tab" data-view="routes" onclick="switchView('routes')">
          <span>ROUTEN</span>
        </button>
        <button class="mode-tab" data-view="master" onclick="switchView('master')">
          <span>MASTER-GUIDE</span>
        </button>
      </div>
    </nav>

    <!-- ======================================================================
         VIEW 01: DOSSIERS (FILTERABLE ARCHITECTURAL GRID)
         ====================================================================== -->
    <section id="view-dossiers" class="view-section active">
      <div class="controls-panel">
        <button class="reset-full-btn" onclick="resetFilters()">RESET FILTER</button>

        <!-- SITUATION FILTER -->
        <div class="filter-strip" id="catFilterStrip">
          <div class="filter-label">TYP</div>
          <button class="filter-chip active" data-cat="all" onclick="setCatFilter('all')">ALLE</button>
          <button class="filter-chip" data-cat="breakfast" onclick="setCatFilter('breakfast')">FRÜHSTÜCK / BRUNCH</button>
          <button class="filter-chip" data-cat="daydrinking" onclick="setCatFilter('daydrinking')">DAYDRINKING &amp; HÖFE</button>
          <button class="filter-chip" data-cat="food" onclick="setCatFilter('food')">ESSEN / MEZE / TAVERNEN</button>
          <button class="filter-chip" data-cat="50best" onclick="setCatFilter('50best')">EU'S 50 BEST BARS</button>
          <button class="filter-chip" data-cat="cocktails" onclick="setCatFilter('cocktails')">COCKTAILS &amp; BARS</button>
          <button class="filter-chip" data-cat="rooftop" onclick="setCatFilter('rooftop')">ROOFTOPS</button>
          <button class="filter-chip" data-cat="wine" onclick="setCatFilter('wine')">WEINBARS</button>
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
        <span id="resultsCountLabel">ZEIGE 34 VON 34 DOSSIERS</span>
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
          <strong>GPS RADAR //</strong> <span id="gpsStatus">Klicke auf einen Pin (#01–#34) für Details oder [HOME] für Korinnis 11.</span>
        </div>
        <div class="map-toolbar-btns">
          <button class="sharp-btn" onclick="focusHomeBase()">[00] HOME BASE (KORINNIS 11)</button>
          <button class="sharp-btn" onclick="locateUser()">MEIN GPS-STANDORT</button>
          <button class="sharp-btn" onclick="fitAllMarkers()">ALLE 34 PINS ZEIGEN</button>
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
        <div class="drawer-top-actions">
          <button class="drawer-close-btn" onclick="closeDrawer()">SCHLIESSEN [×]</button>
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
      localStorage.setItem('ocho_theme_v2', theme);
      const lbl = document.getElementById('themeLabel');
      if (lbl) lbl.textContent = theme === 'dark' ? '[DARK]' : '[LIGHT]';
      const metaTheme = document.querySelector('meta[name="theme-color"]');
      if (metaTheme) metaTheme.setAttribute('content', theme === 'dark' ? '#080808' : '#F7F7F5');
      updateMapTiles();
    }}

    function toggleTheme() {{
      const cur = document.documentElement.getAttribute('data-theme') || 'light';
      applyTheme(cur === 'dark' ? 'light' : 'dark');
    }}

    function togglePhotoColor() {{
      document.body.classList.toggle('color-photos');
      const isColor = document.body.classList.contains('color-photos');
      localStorage.setItem('ocho_photos_v2', isColor ? 'color' : 'bw');
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

    function resetFilters() {{
      activeCat = 'all';
      activeDist = 'all';
      document.querySelectorAll('#catFilterStrip .filter-chip').forEach(c => c.classList.toggle('active', c.dataset.cat === 'all'));
      document.querySelectorAll('#distFilterStrip .filter-chip').forEach(c => c.classList.toggle('active', c.dataset.dist === 'all'));
      renderSpots();
    }}

    function renderSpots() {{
      const list = SPOTS.filter(s => {{
        if (activeCat !== 'all' && !s.cats.includes(activeCat)) return false;
        if (activeDist !== 'all' && s.district_tag !== activeDist) return false;
        return true;
      }});

      document.getElementById('resultsCountLabel').textContent = `ZEIGE ${{list.length}} VON ${{SPOTS.length}} DOSSIERS`;

      const grid = document.getElementById('spotsGrid');
      if (!list.length) {{
        grid.innerHTML = `<div style="grid-column: 1 / -1; padding: 48px 20px; text-align: center; background: var(--surface); border: 1px solid var(--border); font-family: 'JetBrains Mono', monospace;">KEINE TREFFER FÜR DIESEN FILTER. <button class="sharp-btn" style="margin-left:12px;" onclick="resetFilters()">FILTER ZURÜCKSETZEN</button></div>`;
        return;
      }}

      grid.innerHTML = list.map(s => `
        <article class="spot-card" id="spot-card-${{s.id}}">
          <div>
            <div class="card-top">
              <div class="card-head">
                <div class="card-meta-line">
                  <span>${{s.cat_label}} · ${{s.walk_min}} MIN FUSSWEG</span>
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
                <span class="spec-key">VORAUSSICHTLICHE ÖFFNUNGSZEITEN</span>
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
            <div class="dq-label">VORAUSSICHTLICHE ÖFFNUNGSZEITEN</div>
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
      const theme = document.documentElement.getAttribute('data-theme') || 'light';
      const tilePane = mapInstance.getPane('tilePane');
      if (tilePane) {{
        tilePane.style.filter = theme === 'dark'
          ? 'invert(100%) hue-rotate(180deg) brightness(95%) contrast(90%)'
          : 'none';
      }}
      if (!tileLayer) {{
        tileLayer = L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
          attribution: '&copy; OpenStreetMap',
          maxZoom: 19
        }}).addTo(mapInstance);
      }}
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

      // All 34 Spot Markers
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
      const savedTheme = localStorage.getItem('ocho_theme_v2') || 'light';
      applyTheme(savedTheme);
      const savedPhotos = localStorage.getItem('ocho_photos_v2') || 'color';
      if (savedPhotos === 'color') {{
        document.body.classList.add('color-photos');
        document.getElementById('photoModeLabel').textContent = '[FARBE]';
      }} else {{
        document.body.classList.remove('color-photos');
        document.getElementById('photoModeLabel').textContent = '[S/W]';
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
