"""Wochen- und Tagesplan (regelbasiert, deterministisch).

Grundlage: Christian_Heimtraining_Wissensbasis.md – langsamer Aufbau, keine Sprünge/Laufen,
erst Verträglichkeit, dann Dauer, dann Intensität.
"""
from datetime import date, timedelta

START = date(2026, 11, 2)  # Montag, Woche 1
WEEKS = 8
WD = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

PHASES = {
    1: ("Eingewöhnen", "1 Satz je Übung. Ziel: Verträglichkeit testen, nichts beweisen."),
    2: ("Aufbauen", "Gut vertragene Übungen auf 2 Sätze. Gehen langsam verlängern."),
    3: ("Festigen", "Neue Band-/Hantelübungen dazu. Dauer vor Intensität."),
    4: ("Feiertage", "Volumen bewusst runter, Routine halten statt steigern."),
}


def week_no(d: date) -> int:
    return (d - START).days // 7 + 1


def phase_of(w: int) -> int:
    if w <= 2:
        return 1
    if w <= 4:
        return 2
    if w <= 7:
        return 3
    return 4


W = [("N33", "1 Min."), ("N34", "je 8"), ("N32", "8 Wdh.")]

WORKOUTS = {
    "A": {
        1: W + [("K01", "6–8 Wdh."), ("K04", "8 × 2 Sek."), ("K07", "4–6 Wdh. – nur beschwerdefrei"),
                ("K12", "8–10 Wdh."), ("K15", "5 Durchgänge")],
        2: W + [("K01", "2 × 8"), ("K03", "1 × 10"), ("K04", "2 × 8"), ("K07", "2 × 5 – nur beschwerdefrei"),
                ("K12", "2 × 10"), ("K15", "5 Durchgänge")],
        3: W + [("K02", "2 × 8 (oder K01)"), ("K03", "2 × 10"), ("N21", "2 × 10"), ("K07", "2 × 6"),
                ("K12", "2 × 12"), ("K18", "3 × 10 Sek."), ("K15", "5 Durchgänge")],
    },
    "B": {
        1: W + [("K01", "6–8 Wdh."), ("K06", "8 Wdh."), ("K08", "6–8 je Seite"), ("K13", "8 × 3 Sek."),
                ("K19", "10 Wdh.")],
        2: W + [("K01", "2 × 8"), ("K06", "2 × 8"), ("K08", "2 × 8 je Seite"), ("K11", "1 × 6 je Seite"),
                ("K13", "8 × 3 Sek."), ("K14", "1 × 6 – nur wenn Boden ok"), ("K19", "2 × 10")],
        3: W + [("N24", "2 × 8 je Seite"), ("N23", "2 × 10"), ("K06", "2 × 10"), ("N25", "2 × 8 je Seite"),
                ("K08", "2 × 10 je Seite"), ("K11", "2 × 8 je Seite"), ("K14", "2 × 8"), ("K19", "2 × 12")],
    },
    "C": {
        1: [("N33", "1 Min."), ("K16", "5 je Seite"), ("K17", "5 je Seite"), ("N30", "2 × 20 Sek."),
            ("N31", "2 × 20 Sek. je Seite"), ("K15", "5 Durchgänge")],
        2: [("N33", "1 Min."), ("N21", "1 × 10"), ("N22", "1 × 10 je Seite"), ("K03", "1 × 10"),
            ("N27", "1 × 10"), ("K18", "3 × 5–10 Sek."), ("N30", "2 × 20 Sek.")],
        3: [("N33", "1 Min."), ("N21", "2 × 10"), ("N22", "2 × 10 je Seite"), ("K03", "2 × 10"),
            ("N27", "2 × 10"), ("K18", "3 × 10 Sek."), ("N30", "2 × 20 Sek."), ("N31", "2 × 20 Sek.")],
    },
    "M": {  # kurze Mobilität
        0: [("N30", "2 × 20 Sek."), ("N31", "2 × 20 Sek. je Seite"), ("N32", "10 Wdh."), ("N34", "je 8")],
    },
}
WORKOUT_TITLE = {"A": "Kraft A", "B": "Kraft B", "C": "Band & Haltung", "M": "Mobilität"}

WALK_DI_DO = [5, 8, 10, 12, 15, 15, 18, 15]
WALK_FR = [5, 8, 10, 10, 12, 15, 15, 10]

# ---------------------------------------------------------------- Essen
R_MO = ["hahnchen-gyros-aus-der-heissluftfritteuse", "black-garlic-chicken-bowl", "green-lachs-bowl",
        "teriyaki-rindfleisch-mit-zwiebeln-und-brokkoli-fertig-in-30-minuten",
        "gefullte-paprika-aus-der-heissluftfritteuse", "gemusecurry-ohne-kokosmilch", "geflugel-curry",
        "hahnchen-one-pot-mit-reis"]
R_FR = ["crispy-lachs-bowl-aus-dem-airfryer", "burrito-bowl-mexikanisches-rezept", "taxi-teller",
        "sushi-bowl-einfach-und-so-lecker", "paprika-reis-mit-putenfleisch", "bolognese-sauce-selber-machen",
        "garnelen-rezept-aus-dem-wok", "lachs-in-zitronensauce"]
R_SO = ["mediterranes-huhn", "shakshuka-mit-hackballchen", "souvlaki", "gefullte-zucchini-vegetarisch-mit-feta",
        "lachssteak-mit-gemusereis", "mediterrane-hahnchenspiesse", "fisch-mit-krauterkruste",
        "griechische-riesenbohnen"]
R_DI = ["hahnchenbrust-in-der-heissluftfritteuse", "lachs-aus-der-heissluftfritteuse",
        "gemuse-hahnchen-aus-der-heissluftfritteuse", "zucchini-frittata",
        "kurbis-mit-feta-aus-der-heissluftfritteuse-so-einfach-so-gut", "asia-sesam-hahnchen-salat-mit-glasnudeln",
        "rote-linsen-bratlinge-einfach-gesund", "meine-beste-salat-bowl-bunt-gesund-in-20-minuten-fertig-grundrezept-ideen",
        "gemusepfanne-rezept-einfach-und-so-schnell", "vegane-buddha-bowl", "griechischer-halloumi-mit-gemuse"]
R_DO = ["chicken-vegetable-soup", "rote-linsensuppe-mit-kokosmilch-und-ingwer", "white-bean-chicken-soup",
        "tomatensuppe-mit-reis-einfach-und-so-lecker", "greek-lemon-chicken-soup-quick-easy", "kurbissuppe-rezept",
        "toskanische-gemusesuppe", "cabbage-roll-soup"]
SIDES = ["gemuse-in-der-heissluftfritteuse", "rosenkohl-aus-der-heissluftfritteuse", "brokkoli-salat-roh-mit-feta-apfel",
         "bunter-paprikasalat-mit-feta", "rote-bete-salat-roh-mit-feta-walnussen"]

TIPS_RECIPE = {
    "taxi-teller": "Leichte Version: Fleisch + großer Salat, Pommes nur eine kleine Handvoll aus dem Airfryer, Soße separat.",
    "bolognese-sauce-selber-machen": "Halb Hack, halb Linsen/Gemüse (Karotte, Sellerie, Zucchini). Vollkornnudeln, Portion ~80 g roh, dazu Salat.",
    "burrito-bowl-mexikanisches-rezept": "Mehr Bohnen & Gemüse, Reis halbieren, Sour Cream durch Skyr ersetzen.",
    "sushi-bowl-einfach-und-so-lecker": "Reis halbe Portion, mehr Gurke/Edamame, Mayo-Soße sparsam.",
    "shakshuka-mit-hackballchen": "Brot nur eine Scheibe zum Tunken.",
}

FR_BUERO = [
    ("Skyr-Becher", "Kaffee schwarz + 200 g Skyr/Magerquark mit Beeren (im Büro-Kühlschrank deponieren)."),
    ("Eier to go", "Kaffee + 2 gekochte Eier + Paprika/Gurke."),
    ("Eier-Wrap", "Am Vorabend: Vollkorn-Wrap mit Rührei, Putenbrust und Paprika – morgens mitnehmen."),
    ("Kaffee + Brot", "Kaffee + 1 Scheibe Vollkornbrot mit Hüttenkäse und Tomate."),
]
FR_HOME = [
    ("Rührei", "2–3 Eier mit Tomate/Spinat, 1 Scheibe Vollkornbrot.", None),
    ("Baked Oats", "Aus dem Airfryer – gut vorzubereiten.", "baked-oats-aus-dem-airfryer"),
    ("Skyr-Bowl", "Skyr, Beeren, 1 EL Nüsse, etwas Haferflocken.", None),
    ("Fitnessbrot", "2 Scheiben mit Frischkäse light, Gurke, Kochschinken.", "fitnessbrot-in-der-heissluftfritteuse"),
]
MI_BUERO = [
    ("Edeka-Salat + Protein", "Salat mit Hähnchen, Ei, Feta oder Thunfisch. Dressing separat, nur die Hälfte."),
    ("Belegtes Vollkornbrot", "Vollkornbrot/-brötchen mit Käse, Ei, Schinken oder Hähnchen + Rohkost (Paprika, Gurke)."),
    ("Salattheke + Hüttenkäse", "Große Schale Salat/Gemüse + 200 g Hüttenkäse + 1 Vollkornbrötchen."),
]
BROT_ABEND = [
    "Vollkornbrot + Hüttenkäse/Frischkäse, 2 Eier, Tomate & Gurke – Wurst nur als Beilage.",
    "Schafskäse aus dem Airfryer mit Paprika, Tomaten, Zwiebeln + 1 Scheibe Brot.",
    "Vollkornbrot mit Putenbrust/Kochschinken + großer Rohkostteller + Zaziki als Dip.",
    "Reste-Suppe vom Mittag + 1 Scheibe Brot.",
]
SNACKS = ["Apfel oder Birne", "Gemüsesticks mit Zaziki", "Geröstete Kichererbsen (Airfryer)",
          "30 g Nüsse (eine kleine Handvoll)", "Skyr natur mit Zimt", "Grünkohl-Chips (Airfryer)"]

TIPS = [
    "Wasser zuerst: ein großes Glas vor jedem Kaffee.",
    "Teller-Regel: halb Gemüse, ein Viertel Protein, ein Viertel Beilage.",
    "Heute zählt Wiederholbarkeit, nicht Perfektion.",
    "Training darf anstrengend sein – aber keine Schmerzen verstärken.",
    "Beim Drücken ausatmen, nie die Luft anhalten (Blutdruck).",
    "Nach dem Essen 5 Minuten aufstehen und herumgehen hilft dem Blutzucker.",
    "Süßes nur nach dem Essen, nicht zwischendurch und nicht als Belohnung fürs Training.",
    "Kompressionsstrümpfe: bei langem Stehen und auf Wegen tragen (Arzt fragen, ob auch beim Training).",
    "Achilles-Check am Morgen danach: Wird es schlechter, war's zu viel – zurück auf die Vorstufe.",
    "Eiweiß zu jeder Mahlzeit: Skyr, Eier, Hüttenkäse, Hähnchen, Fisch, Hülsenfrüchte.",
    "Vor dem Einkauf: Wochenplan in der App ansehen, Einkaufsliste in Mealie füllen.",
    "Alkohol: höchstens zwei Anlässe pro Woche – an Trainerabenden keiner.",
    "Schlaf ist Training: 30 Minuten vor dem Bett kein Handy.",
    "Kleine Portion auf den Teller, Rest gleich wegstellen – Nachschlag erst nach 10 Minuten.",
]

WEEK_TASKS = {
    1: ["Hausarzttermin vereinbaren (Bauch, Ödeme, Blutdruck, Medikamente, Achilles)",
        "Physio-Termin anfragen (Achilles, Knie, HWS/LWS)", "Stehtisch zu Hause freiräumen",
        "MSM bis zur Abklärung pausieren", "Skyr/Eier für Büro-Frühstück einkaufen"],
    2: ["Arztfragen aus dem Supplement-Tab mitnehmen", "Stehtisch zu Hause in Betrieb nehmen",
        "Bauchumfang messen (Mo)"],
    3: ["Erste Bilanz: Was lief gut? Eine Sache anpassen", "Band-Befestigung (Türanker) besorgen, falls nötig"],
    4: ["Leichte Kurzhanteln prüfen (2–5 kg reichen)"],
    5: ["Zwischenbilanz Gewicht & Umfang", "Phase 3 nur bei ruhigen Gelenken starten"],
    6: ["Weihnachtsfeiern: Regeln für auswärts vorher festlegen"],
    7: ["Plan für die Feiertage festlegen (Gehen mit Familie)"],
    8: ["Feiertage genießen – Routine light halten", "Plan ab Januar mit Coach neu aufsetzen"],
}

DEFAULT_LOCATIONS = {0: "buero", 1: "home", 2: "buero", 3: "home", 4: "buero", 5: "frei", 6: "frei"}
LOC_LABEL = {"buero": "Büro", "home": "Homeoffice", "frei": "Frei"}


def pick(lst, i):
    return lst[i % len(lst)]


def d3k2_day(d: date) -> bool:
    return (d - START).days % 5 == 0


# Zusatzübungen, wenn mehr Zeit eingestellt ist (nur Status plan/frei, gelenkschonend)
EXTRA = {
    "A": [("K05", "2 × 10"), ("N21", "2 × 10"), ("N22", "2 × 10 je Seite"), ("K10", "2 × 8 je Seite"),
          ("N23", "2 × 10"), ("K09", "2 × 6 je Seite")],
    "B": [("N27", "2 × 10"), ("K10", "2 × 8 je Seite"), ("N22", "2 × 10 je Seite"), ("K18", "3 × 10 Sek."),
          ("K12", "2 × 12"), ("N21", "2 × 10")],
    "C": [("K04", "2 × 8"), ("K12", "2 × 10"), ("K13", "8 × 3 Sek."), ("N31", "2 × 20 Sek.")],
}
# Kraft-Wochentage je nach Einstellung (0 = Mo) -> Einheit
STRENGTH_DAYS = {2: {0: "A", 2: "B"}, 3: {0: "A", 2: "B", 5: "A"}, 4: {0: "A", 2: "B", 3: "C", 5: "A"}}


def more_sets(dose):
    return dose.replace("1 × ", "2 × ").replace("2 × ", "3 × ", 1) if "×" in dose else dose


def workout(key, phase, minutes=20, wi=0):
    p = 0 if key == "M" else (2 if phase == 4 else phase)
    items = [{"ex": e, "dose": dose} for e, dose in WORKOUTS[key][p]]
    if key in EXTRA and phase > 1 and minutes >= 30:
        n = 2 if minutes < 45 else 4
        have = {i["ex"] for i in items}
        pool = [x for x in EXTRA[key] if x[0] not in have]
        for k in range(min(n, len(pool))):
            e, dose = pool[(wi + k) % len(pool)]
            items.append({"ex": e, "dose": dose, "extra": True})
        if minutes >= 45 and phase >= 2:
            for i in items:
                if not i.get("extra") and i["ex"] not in ("N33", "N34", "N32"):
                    i["dose"] = more_sets(i["dose"])
    return {"key": key, "title": WORKOUT_TITLE[key], "minutes": minutes, "items": items}


def build_day(d: date, settings: dict, events: list, hold: bool = False):
    wd = d.weekday()
    w = week_no(d)
    in_plan = 1 <= w <= WEEKS
    wi = max(w, 1) - 1
    phase = phase_of(max(w, 1)) if w <= WEEKS else 3
    lvl = str(settings.get("level", "auto"))
    if lvl in ("1", "2", "3"):
        phase = int(lvl)
    if hold and phase in (2, 3):
        phase -= 1
    minutes = int(settings.get("minutes", 20))
    sdays = STRENGTH_DAYS.get(int(settings.get("strength_days", 2)), STRENGTH_DAYS[2])
    locs = settings.get("locations") or DEFAULT_LOCATIONS
    loc = locs.get(str(wd), locs.get(wd, "frei"))
    day_events = [e for e in events if e.get("date") == d.isoformat()]
    game = next((e for e in day_events if e.get("kind") == "game"), None)
    training = next((e for e in day_events if e.get("kind") == "training"), None)
    blocks = []

    def add(time, kind, title, text="", **kw):
        bid = f"{kw.get('meal') or kind}-{(time or 'x').replace(':', '')}"  # stabil, damit Haken beim Umstellen bleiben
        blocks.append(dict(id=bid, time=time, kind=kind, title=title, text=text, **kw))

    # --- Morgen
    if wd == 0:
        add("06:45", "check", "Wiegen", "Nüchtern, nach dem Bad, gleiche Waage. Wert unten eintragen.", metric="weight")
        if w in (1, 3, 5, 7):
            add("06:46", "check", "Bauchumfang messen", "Auf Nabelhöhe, ausatmen, Maßband locker.", metric="waist")
    if loc == "buero":
        name, txt = pick(FR_BUERO, wi + wd)
        add("07:30", "meal", f"Frühstück: {name}", txt, meal="breakfast")
    elif loc == "home":
        name, txt, slug = pick(FR_HOME, wi + wd)
        add("07:30", "meal", f"Frühstück: {name}", txt, meal="breakfast", recipe=slug)
    elif wd == 6:
        add("09:30", "meal", "Sonntagsfrühstück – leichter",
            "1 Salzweck, 2 Spiegeleier (wenig Fett), Putenbrust/Kochschinken statt Salami, viel Tomate & Gurke.",
            meal="breakfast")
    else:
        add("08:30", "meal", "Frühstück", "Eiweiß + Gemüse/Obst: z. B. Rührei mit Tomate oder Skyr-Bowl.", meal="breakfast")
    add("08:00", "supp", "Supplements morgens", "", supp="morning")

    # --- Arbeit / Vormittag
    if loc == "buero":
        add("09:00", "move", "Stehtisch Büro",
            "3–4 Blöcke à 20–30 Min. stehen, dazwischen sitzen. Stündlich 2 Min.: Schulterkreisen + "
            "Schulterblätter zurück (K04). Gewicht öfter verlagern (Achilles).", ex=["K04", "N33"])
    elif loc == "home":
        stand = "Stehtisch zu Hause nutzen (sobald freigeräumt): 2–3 Blöcke à 20–30 Min." if w >= 2 else \
            "Diese Woche: Stehtisch zu Hause freiräumen."
        add("09:00", "move", "Homeoffice", stand)
        c = workout("C", phase, minutes, wi)
        if not (wd == 3 and 3 in sdays):
            add("10:00", "workout", f"Optional: {c['title']} (15 Min.)",
            "Wenn's zeitlich passt. Sonst abends vor dem Gehen.", workout=c, optional=True)

    # --- Mittag
    if loc == "buero":
        if wd == 2 and in_plan:
            add("12:30", "meal", "Mittag: Reste vom Montag",
                "Montags doppelt kochen, eine Portion ins Glas – spart Edeka.", meal="lunch",
                recipe=pick(R_MO, wi))
        elif wd == 4:
            add("12:30", "meal", "Mittag: Brauerei oder Edeka",
                "Brauerei nur mit Regeln: keine Pommes, keine Extra-Soße, keine Vorspeise – Fleisch/Fisch mit Gemüse/Salat. "
                "Taxiteller: Pommes gegen Salat tauschen.", meal="lunch")
        else:
            name, txt = pick(MI_BUERO, wi + wd)
            add("12:30", "meal", f"Mittag: {name}", txt + " Kein Fleischkäsweck/Cheeseburger.", meal="lunch")
    elif loc == "home":
        slug = pick(R_DI, wi) if wd == 1 else pick(R_DO, wi)
        add("12:15", "meal", "Mittag kochen", "Großzügig Gemüse; Suppe gleich für abends mitkochen." if wd == 3 else
            "Dazu Salat oder Ofengemüse.", meal="lunch", recipe=slug, side=pick(SIDES, wi + wd))
    elif wd == 5:
        add("12:30", "meal", "Mittag", "Flexibel – Teller-Regel anwenden.", meal="lunch")
    add("15:30", "meal", "Snack (optional)", pick(SNACKS, wi * 7 + wd), meal="snack", optional=True)

    # --- Abend: Training
    if wd in sdays and wd not in (5, 3):
        wk = workout(sdays[wd], phase, minutes, wi)
        add("18:15", "workout", f"{wk['title']} ({minutes}–{minutes + 5} Min.)",
            "Vor dem Kochen/Abendbrot, vor dem Trainerabend.", workout=wk)
    if wd == 3 and 3 in sdays:
        wk = workout(sdays[3], phase, minutes, wi)
        add("17:30", "workout", f"{wk['title']} – fester Termin ({minutes} Min.)",
            "4-Tage-Modus: heute fix (statt optional am Vormittag), danach Gehen.", workout=wk)
    if wd in (0, 2):
        pass
    elif wd in (1, 3):
        mins = pick(WALK_DI_DO, wi) if in_plan else 15
        add("18:15" if (wd == 3 and 3 in sdays) else "17:45", "walk", f"Gehen {mins} Min.",
            "Flach, Sprechtempo, Laufband ohne Steigung. Falls Band & Haltung morgens ausgefallen: jetzt davor.",
            minutes=mins, ex=["K20"])
    elif wd == 4:
        mins = pick(WALK_FR, wi) if in_plan else 10
        add("19:00", "walk", f"Gehen {mins} Min. + Mobilität",
            "Nach dem Abholen der Tochter. Danach 5 Min. Mobilität.", minutes=mins, ex=["K20"],
            workout=workout("M", phase, minutes, wi))
    elif wd == 5:
        if 5 in sdays:
            wk = workout(sdays[5], phase, minutes, wi)
            add("10:00", "workout", f"{wk['title']} – Wochenende ({minutes} Min.)", "Vormittags, vor dem Spaziergang.",
                workout=wk)
        mins = "10–15" if w <= 2 else "20–30"
        add("14:00", "walk", f"Familienspaziergang {mins} Min.", "Gemütlich und flach – nur wenn Achilles ≤ 3/10.",
            ex=["K20"])
    else:
        add("17:00", "workout", "Mobilität (5 Min., optional)", "Und: Wochencheck unten ausfüllen.",
            workout=workout("M", phase, minutes, wi), optional=True)

    # --- Abendessen
    if wd == 0:
        add("19:00", "meal", "Abendessen: Kochabend (doppelt für Mittwoch)", "", meal="dinner", recipe=pick(R_MO, wi),
            side=pick(SIDES, wi))
    elif wd == 2:
        add("19:00", "meal", "Abendbrot", pick(BROT_ABEND, wi), meal="dinner")
    elif wd in (1, 3):
        txt = "Rest der Mittagssuppe + 1 Scheibe Brot." if wd == 3 else pick(BROT_ABEND, wi + 1)
        add("18:45", "meal", "Abendbrot", txt, meal="dinner")
    elif wd == 4:
        add("19:30", "meal", "Abendessen: Familien-Kochabend", "", meal="dinner", recipe=pick(R_FR, wi))
    elif wd == 5:
        add("19:00", "meal", "Abend: Event / Gäste",
            "Regeln: erst Salat/Gemüse, eine Portion, Soße sparsam. Wenn Alkohol, dann heute – 1–2 Gläser, dazwischen Wasser.",
            meal="dinner")
    else:
        add("12:30", "meal", "Sonntagsessen (Familie)", "", meal="dinner", recipe=pick(R_SO, wi), side=pick(SIDES, wi + 2))

    # --- Handball
    if training and wd in (0, 2):
        add(training.get("start", "19:45"), "event", "Handball-Training (Trainer)",
            f"{training.get('title', '')} – viel Stehen/Gehen zählt mit. Kein Alkohol danach.")
    if game:
        add(game.get("start", ""), "event", "Spieltag", f"{game.get('title', '')}. Wasserflasche mit, Snack statt Bratwurst.")

    add("21:00", "supp", "Supplements abends", "", supp="evening")
    add("22:30", "check", "Tagescheck", "Schmerzen (0–10), Energie, Notiz – unten eintragen.")

    blocks.sort(key=lambda b: b["time"] or "99")
    alcohol = "Kein Alkohol (Trainerabend)" if wd in (0, 2) else ("Wenn, dann heute: max. 1–2 Gläser" if wd == 5 else
                                                                  "Alkoholfrei")
    return {
        "date": d.isoformat(), "weekday": WD[wd], "week": w if in_plan else None, "phase": phase,
        "phase_name": PHASES[phase][0], "phase_text": PHASES[phase][1], "hold": hold, "location": loc,
        "location_label": LOC_LABEL.get(loc, loc), "blocks": blocks, "alcohol": alcohol,
        "tip": pick(TIPS, (d - START).days), "d3k2": d3k2_day(d), "recipe_tips": TIPS_RECIPE,
        "tasks": WEEK_TASKS.get(w, []) if wd == 0 and in_plan else [],
        "events": day_events,
    }
