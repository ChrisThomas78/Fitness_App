"""Baut app/data/exercises.json und lädt die Bilder nach app/static/img/ex/.

Quellen:
- eigene Karten K01–K20 aus der Wissensbasis (Christian_Heimtraining_Wissensbasis.md)
- Zusatzkarten N21+ (Band, Kurzhantel, Mobilität) – deutsch geschrieben
- Bibliothek aus free-exercise-db (github.com/yuhonas/free-exercise-db, Unlicense/Public Domain)

Aufruf:  python -I -X utf8 tools/build_exercises.py <pfad/zu/exercises.json>
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "app" / "data" / "exercises.json"
IMG = ROOT / "app" / "static" / "img" / "ex"
RAW = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/"

# Status: plan = steht im Plan · frei = passt jetzt · vorsicht = nur beschwerdefrei/leicht
#         spaeter = erst nach Arzt/Physio bzw. ab späterer Phase · nein = aktuell ungeeignet
OWN = [
    dict(id="K01", name="Wandliegestütz", group="Oberkörper", equip="Wand", status="plan",
         start="6–8 Wdh.", img="Incline_Push-Up",
         steps=["Hände etwa auf Schulterhöhe an die Wand setzen.", "Füße etwas zurückstellen.",
                "Ellbogen beugen und den Körper langsam zur Wand bewegen.", "Kontrolliert zurückdrücken."],
         cues=["Kopf in Verlängerung des Körpers, Schultern nicht hochziehen.",
               "Je näher die Füße an der Wand, desto leichter."]),
    dict(id="K02", name="Liegestütz an der Arbeitsplatte", group="Oberkörper", equip="Arbeitsplatte", status="frei",
         start="5–8 Wdh.", img="Incline_Push-Up_Medium",
         steps=["Hände schulterbreit auf die fest montierte Arbeitsplatte.", "Körper gerade, Füße zurück.",
                "Brust Richtung Kante absenken.", "Kontrolliert zurückdrücken."],
         cues=["Erst wenn Wandliegestütze problemlos gehen.", "Kein beweglicher Tisch, keine Stuhllehne."]),
    dict(id="K03", name="Bandrudern im Sitzen", group="Oberkörper", equip="Band", status="plan",
         start="8–10 Wdh., leichter Widerstand", img="Seated_Cable_Rows",
         steps=["Aufrecht sitzen, Knie leicht gebeugt.", "Band sicher um die beschuhten Mittelfüße führen.",
                "Ellbogen Richtung Hüfte ziehen, Schulterblätter zurück.", "Langsam wieder strecken."],
         cues=["Nicht rund werden oder nach hinten reißen.",
               "Alternative im Stehen: Band um ein Tischbein / Türanker auf Brusthöhe.",
               "Nur wenn Bandlänge und Herstelleranleitung das erlauben – sonst K04."]),
    dict(id="K04", name="Schulterblätter zurückführen", group="Haltung", equip="Stuhl", status="plan",
         start="8 Wdh. à 2 Sek.", img="Elbows_Back",
         steps=["Aufrecht sitzen, Arme entspannt neben dem Körper.", "Schulterblätter sanft nach hinten-unten führen.",
                "2 Sekunden halten, lösen."],
         cues=["Kein gewaltsames Zusammenpressen, kein Hohlkreuz.", "Schultern bleiben unten – gut auch im Büro."]),
    dict(id="K05", name="Bizepscurl im Sitzen", group="Arme", equip="Kurzhantel", status="frei",
         start="8 Wdh.", img="Seated_Dumbbell_Curl",
         steps=["Aufrecht sitzen, Ellbogen neben dem Körper.", "Hanteln langsam Richtung Schultern heben.",
                "Langsam absenken."],
         cues=["Kein Schwung, kein Schulterhochziehen.", "Bei Nackenspannung Gewicht reduzieren."]),
    dict(id="K06", name="Hammercurl im Sitzen", group="Arme", equip="Kurzhantel", status="plan",
         start="8 Wdh.", img="Hammer_Curls",
         steps=["Wie Bizepscurl, Handflächen zeigen die ganze Zeit zueinander."],
         cues=["Handgelenke gerade.", "Alternative zu K05, nicht zusätzlich nötig."]),
    dict(id="K07", name="Aufstehen vom Stuhl", group="Beine & Hüfte", equip="Stuhl", status="plan",
         start="4–6 Wdh.", img="Sit_Squats",
         steps=["Stabiler Stuhl gegen die Wand, Füße hüftbreit.", "Oberkörper aus der Hüfte leicht vorlehnen.",
                "Aufstehen.", "Langsam wieder hinsetzen."],
         cues=["Hände dürfen helfen, kein Schwung nötig.",
               "Bei Knie- oder Achillesschmerz auslassen; niedrige Sitzfläche = schwerer."]),
    dict(id="K08", name="Kniestrecken im Sitzen", group="Beine & Hüfte", equip="Stuhl", status="plan",
         start="6–8 Wdh. je Seite", img="Leg_Extensions",
         steps=["Aufrecht sitzen.", "Einen Unterschenkel langsam nach vorne strecken.", "Wieder absetzen, Seite wechseln."],
         cues=["Nur im angenehmen Bereich.", "Knie nicht mit Kraft durchdrücken."]),
    dict(id="K09", name="Knieheben im Sitzen", group="Rumpf", equip="Stuhl", status="frei",
         start="6 Wdh. je Seite", img=None,
         steps=["Aufrecht sitzen.", "Einen Fuß wenige Zentimeter vom Boden anheben.", "Absetzen, Seite wechseln."],
         cues=["Nicht nach hinten kippen.", "Bei Druck oder Schmerzen im Bauch auslassen."]),
    dict(id="K10", name="Seitliches Beinheben", group="Beine & Hüfte", equip="Arbeitsplatte", status="frei",
         start="6 Wdh. je Seite", img="Standing_Hip_Circles",
         steps=["An der Arbeitsplatte festhalten.", "Ein Bein ein kleines Stück seitlich führen.", "Zurückstellen."],
         cues=["Zehenspitzen nach vorne, Oberkörper aufrecht.", "Bei Achilles-/Knieschmerz im Standbein K12 nehmen."]),
    dict(id="K11", name="Bein nach hinten führen", group="Beine & Hüfte", equip="Arbeitsplatte", status="plan",
         start="6 Wdh. je Seite", img="Hip_Extension_with_Bands",
         steps=["An der Arbeitsplatte festhalten.", "Ein Bein fast gestreckt wenige Zentimeter nach hinten führen.",
                "Zurückstellen."],
         cues=["Bewegung klein halten, kein Hohlkreuz.", "Bei Beschwerden im Standbein auslassen."]),
    dict(id="K12", name="Knie nach außen öffnen", group="Beine & Hüfte", equip="Stuhl", status="plan",
         start="8–10 Wdh.", img="Thigh_Abductor",
         steps=["Sitzen, Füße bleiben am Boden.", "Knie langsam ein wenig auseinanderführen.", "Zurückbringen."],
         cues=["Becken und Oberkörper ruhig.", "Später mit Miniband um die Knie steigern."]),
    dict(id="K13", name="Gesäß anspannen", group="Beine & Hüfte", equip="Stuhl/Boden", status="plan",
         start="8 Wdh. à 3 Sek.", img=None,
         steps=["Gesäß leicht anspannen.", "3 Sekunden halten.", "Vollständig lösen."],
         cues=["Ruhig weiteratmen.", "Nicht maximal anspannen."]),
    dict(id="K14", name="Kleine Gesäßbrücke", group="Beine & Hüfte", equip="Boden", status="plan",
         start="6–8 Wdh.", img="Butt_Lift_Bridge",
         steps=["Rückenlage, Knie angewinkelt, Füße aufgestellt.", "Gesäß anspannen.",
                "Becken ein kleines Stück anheben.", "Ablegen."],
         cues=["Nicht möglichst hoch drücken.", "Kopf bleibt liegen – nicht auf Nacken stützen. Bei Nackenbeschwerden K13."]),
    dict(id="K15", name="Bauchspannung mit Atmung", group="Rumpf", equip="Stuhl/Boden", status="plan",
         start="5 Durchgänge à 2–3 Atemzüge", img=None,
         steps=["Beim Ausatmen den Bauch sanft anspannen – wie einen engen Hosenbund schließen.",
                "2–3 ruhige Atemzüge weiteratmen.", "Lösen."],
         cues=["Nicht pressen, nicht gewaltsam einziehen.", "Bei ungeklärten Bauchschmerzen nur, wenn beschwerdefrei."]),
    dict(id="K16", name="Ferse auf dem Boden schieben", group="Rumpf", equip="Boden", status="plan",
         start="5 Wdh. je Seite", img=None,
         steps=["Rückenlage, beide Füße aufgestellt.", "Eine Ferse langsam nach vorne schieben.", "Zurückziehen."],
         cues=["Nur so weit, wie Rücken und Becken ruhig bleiben."]),
    dict(id="K17", name="Knie nach außen sinken lassen", group="Mobilität", equip="Boden", status="plan",
         start="5 Wdh. je Seite", img=None,
         steps=["Rückenlage, Füße aufgestellt.", "Ein Knie ein kleines Stück nach außen sinken lassen.", "Zurückführen."],
         cues=["Becken nicht mitdrehen.", "Keine große Dehnung erzwingen."]),
    dict(id="K18", name="Unterarmstütz an der Wand", group="Rumpf", equip="Wand", status="plan",
         start="3 × 5–10 Sek.", img=None,
         steps=["Unterarme an die Wand, Füße einen kleinen Schritt zurück.",
                "Körper gerade ausrichten und leicht gegen die Wand lehnen.", "Halten, ruhig atmen."],
         cues=["Kopf nicht nach vorne schieben; bei Nackendruck auslassen.", "Vorerst kein Bodenplank."]),
    dict(id="K19", name="Fußspitzen heben im Sitzen", group="Beine & Hüfte", equip="Stuhl", status="plan",
         start="10 Wdh.", img=None,
         steps=["Sitzen, Fersen bleiben am Boden.", "Vorfüße langsam anheben.", "Absenken."],
         cues=["Kleiner Bewegungsumfang, kein Zusatzgewicht.", "Bei Zug/Schmerz im operierten Sprunggelenk stoppen."]),
    dict(id="K20", name="Langsames Gehen", group="Ausdauer", equip="Laufband/draußen", status="plan",
         start="3–5 Min. als Test", img="Trail_Running_Walking",
         steps=["Tempo, bei dem du problemlos sprechen kannst.", "Laufband zunächst ohne Steigung.",
                "Minuten laut Tagesplan."],
         cues=["Bei Hinken oder zunehmendem Achilles-/Knieschmerz stoppen.", "Nicht automatisch länger durchziehen."]),
    # ---- Zusatzkarten (neu, ab Phase 2/3) ----
    dict(id="N21", name="Band auseinanderziehen (Pull-Apart)", group="Haltung", equip="Band", status="plan",
         start="10 Wdh.", img="Band_Pull_Apart",
         steps=["Stehen oder sitzen, Band schulterbreit vor der Brust greifen, Arme fast gestreckt.",
                "Band auseinanderziehen, bis die Hände etwa schulterbreit außen sind.", "Langsam zurück."],
         cues=["Arme auf Brusthöhe, nicht über Kopf.", "Schultern unten lassen – gut für die HWS-Haltung."]),
    dict(id="N22", name="Außenrotation mit Band", group="Haltung", equip="Band", status="plan",
         start="10 Wdh. je Seite", img="External_Rotation_with_Band",
         steps=["Ellbogen 90° gebeugt eng am Körper (Handtuchrolle dazwischen).",
                "Unterarm gegen das Band nach außen drehen.", "Langsam zurück."],
         cues=["Ellbogen bleibt am Körper.", "Sehr leichtes Band."]),
    dict(id="N23", name="Brustpresse mit Band", group="Oberkörper", equip="Band", status="frei",
         start="8–10 Wdh.", img="Bench_Press_-_With_Bands",
         steps=["Band hinter dem oberen Rücken, Enden in den Händen.", "Im Stehen/Sitzen nach vorne drücken.",
                "Langsam zurück."],
         cues=["Alternative zu Liegestützen an der Platte.", "Nicht pressen – ausatmen beim Drücken."]),
    dict(id="N24", name="Einarmiges Rudern an der Arbeitsplatte", group="Oberkörper", equip="Kurzhantel", status="plan",
         start="8 Wdh. je Seite, leicht", img="One-Arm_Dumbbell_Row",
         steps=["Eine Hand auf der Arbeitsplatte abstützen, leichte Schrittstellung.",
                "Rücken gerade, Hantel hängt.", "Ellbogen Richtung Hüfte ziehen.", "Langsam absenken."],
         cues=["Rücken bleibt ruhig, kein Verdrehen (LWS!).", "Leichtes Gewicht, Kopf in Verlängerung."]),
    dict(id="N25", name="Trizeps-Kickback abgestützt", group="Arme", equip="Kurzhantel", status="plan",
         start="8 Wdh. je Seite", img="Tricep_Dumbbell_Kickback",
         steps=["Wie N24 abstützen, Oberarm parallel zum Körper.", "Unterarm nach hinten strecken.", "Zurück."],
         cues=["Oberarm bleibt ruhig.", "Leichtes Gewicht."]),
    dict(id="N26", name="Seitheben im Sitzen (leicht)", group="Oberkörper", equip="Kurzhantel", status="vorsicht",
         start="8 Wdh., sehr leicht", img="Seated_Side_Lateral_Raise",
         steps=["Aufrecht sitzen.", "Arme seitlich bis maximal Schulterhöhe heben.", "Langsam senken."],
         cues=["Nicht über Schulterhöhe.", "Bei Nacken-/Schulterziehen weglassen (HWS)."]),
    dict(id="N27", name="Bizepscurl mit Band", group="Arme", equip="Band", status="frei",
         start="10 Wdh.", img="Dumbbell_Bicep_Curl",
         steps=["Auf das Band stellen (beide Füße), Enden greifen.", "Ellbogen am Körper, Hände Richtung Schultern.",
                "Langsam zurück."],
         cues=["Bild zeigt Kurzhantel-Variante, Bewegung identisch."]),
    dict(id="N28", name="Beinbeugen mit Band im Sitzen", group="Beine & Hüfte", equip="Band", status="vorsicht",
         start="8 Wdh. je Seite", img="Seated_Band_Hamstring_Curl",
         steps=["Band vorne befestigt, um die Ferse.", "Ferse unter den Stuhl ziehen.", "Langsam zurück."],
         cues=["Nur ohne Knieschmerz.", "Leichter Widerstand."]),
    dict(id="N29", name="Katze-Kuh im Vierfüßler", group="Mobilität", equip="Boden", status="vorsicht",
         start="6 langsame Wdh.", img="Cat_Stretch",
         steps=["Vierfüßlerstand, Hände unter den Schultern.", "Rücken sanft rund machen.", "Dann sanft lang machen."],
         cues=["Kleiner Bewegungsumfang, Kopf bleibt neutral (HWS).", "Bei Knieschmerz Decke unterlegen oder auslassen."]),
    dict(id="N30", name="Brust- und Schulterdehnung", group="Mobilität", equip="Türrahmen", status="plan",
         start="2 × 20 Sek.", img="Chest_And_Front_Of_Shoulder_Stretch",
         steps=["Unterarm an den Türrahmen, Ellbogen auf Schulterhöhe.", "Sanft nach vorne lehnen.", "Halten."],
         cues=["Nur angenehme Dehnung."]),
    dict(id="N31", name="Hüftbeuger-Dehnung im Stehen", group="Mobilität", equip="Arbeitsplatte", status="plan",
         start="2 × 20 Sek. je Seite", img="Standing_Hip_Flexors",
         steps=["Kleine Schrittstellung an der Arbeitsplatte.", "Becken leicht nach vorne kippen, Gesäß anspannen.",
                "Halten."],
         cues=["Kein Ausfallschritt, keine tiefe Position.", "Hinterer Fuß ganz entspannt (Achilles)."]),
    dict(id="N32", name="Becken kippen im Stehen", group="Mobilität", equip="Wand", status="plan",
         start="10 Wdh.", img="Standing_Pelvic_Tilt",
         steps=["Rücken an der Wand, Knie locker.", "Becken sanft nach hinten kippen (unterer Rücken zur Wand).",
                "Lösen."], cues=["Gut für die LWS, ruhig atmen."]),
    dict(id="N33", name="Arm- und Schulterkreisen", group="Aufwärmen", equip="–", status="plan",
         start="je 10 vor/zurück", img="Arm_Circles",
         steps=["Arme locker kreisen, klein anfangen.", "Danach nur die Schultern kreisen."],
         cues=["Nacken entspannt lassen."]),
    dict(id="N34", name="Fußkreisen im Sitzen", group="Aufwärmen", equip="Stuhl", status="plan",
         start="je 8 pro Richtung", img="Ankle_Circles",
         steps=["Sitzen, Fuß leicht anheben.", "Langsam kreisen."],
         cues=["Nur angenehmer Umfang (operierte Knöchel)."]),
    dict(id="N35", name="Bauernlauf (leicht)", group="Rumpf", equip="Kurzhantel", status="spaeter",
         start="2 × 30 Sek.", img="Farmers_Walk",
         steps=["Je eine leichte Hantel in jeder Hand.", "Aufrecht, langsam gehen.", "Ablegen ohne Rundrücken."],
         cues=["Erst nach Physio-Okay (LWS/Achilles)."]),
    dict(id="N36", name="Kniebeuge zum Stuhl mit Hantel", group="Beine & Hüfte", equip="Kurzhantel", status="spaeter",
         start="6 Wdh.", img="Dumbbell_Squat_To_A_Bench",
         steps=["Hantel vor der Brust.", "Langsam auf den Stuhl setzen, wieder aufstehen."],
         cues=["Steigerung von K07 – erst wenn Knie und Achilles ruhig sind."]),
]

NO = [  # Muster -> Grund
    (r"jump|hop|bound|sprint|skip|plyo|burpee|climber|skating|butt_kick|star|scissors_jump|leap|box|depth",
     "Sprung/explosiv – Achilles & Knie"),
    (r"lunge|split|step[-_]?up|pistol|single-leg_high|worlds_greatest", "Ausfallschritt/Stufe – Knie & Achilles"),
    (r"calf|soleus|gastrocnemius|achilles", "Waden/Achilles – erst nach Physio"),
    (r"crunch|sit-?up|v-up|jackknife|toe_touch|heel_touch|leg_raise|leg_lift|leg_pull|flutter|scissor|tuck|"
     r"air_bike|elbow_to_knee|cocoon|bottoms_up|butt-ups|frog|janda|wipers|knee_hip_raise", "Bauchpresse – HWS/Bauch"),
    (r"neck|chin_to_chest|looking_at_ceiling|shrug", "Nacken – HWS"),
    (r"russian|twist|windmill|wood|around_the_world|spell_caster|torso_rotation|side_bend", "Drehung/Seitneigung – LWS"),
    (r"deadlift|good_morning|hyperext|superman|locust|lower_back_curl|glute-ham|glute_ham|pull_through", "Rückenstrecker unter Last – LWS"),
    (r"pull-?up|pullup|chin-up|dips|dip$|muscle|body-up|inverted_row|scapular", "Eigengewicht zu hoch"),
    (r"overhead|shoulder_press|dumbbell_press|arnold|cuban|upright_row|military|above_head|see-saw|"
     r"standing_palms-in|alternating_dumbbell_press|scaption|pullover|^standing_dumbbell_triceps|"
     r"^standing_one-arm_dumbbell_triceps|^seated_triceps_press|^dumbbell_one-arm_triceps|tate_press|upward_stretch", "Über Kopf – HWS/Schulter"),
    (r"clean|swing|sledge|wind_sprints|running", "Schwung/Laufen"),
    (r"squat|plie|power_partials", "Kniebeuge – erst nach Knie-Freigabe"),
    (r"push-?up|pushup|plank|side_bridge|bridge|spider|inchworm", "Bodenstütz – später"),
]
SPAETER_RX = re.compile(r"squat|plie|push-?up|pushup|plank|side_bridge|bench|flyes|floor_press|decline|incline|"
                        r"lying|bridge|monster|hip_lift|adduction|dead_bug|childs|quad|groin|straddle|hamstring")
FREI_RX = re.compile(r"(?<!bent_over_two-dumbbell_)row(?!_with_palms)|curl|kickback|lateral_raise|side_laterals|external_rotation|internal_rotation|pull_apart|"
                     r"back_flyes|reverse_flyes|rear_delt|circles|chest_stretch|triceps_stretch|tricep_side|biceps_stretch|"
                     r"cat_stretch|pelvic|hip_flexors|wrist|front_dumbbell_raise|cross_over|elbows_back|"
                     r"shoulder_stretch|upper_back|middle_back|chair_|towel")
GROUP = [
    (r"stretch|circles|pelvic|flexor|childs|straddle|smr", "Mobilität"),
    (r"curl|tricep|kickback|wrist|zottman|skull|tate", "Arme"),
    (r"squat|lunge|leg|hip|glute|calf|step|abduct|adduct|monster|hamstring|butt", "Beine & Hüfte"),
    (r"crunch|sit-up|plank|bridge|twist|abs|dead_bug|vacuum|tuck|bug|v-up|side_bend", "Rumpf"),
    (r"row|pull|fly|flye|press|push|raise|delt|shoulder|chest|rotation|shrug", "Oberkörper"),
]
EQUIP = {"body only": "Körpergewicht", "bands": "Band", "dumbbell": "Kurzhantel", None: "Körpergewicht",
         "other": "Sonstiges", "exercise ball": "Gymnastikball", "foam roll": "Faszienrolle"}


def classify(x):
    key = x["id"].lower()
    for rx, why in NO:
        if re.search(rx, key):
            if why.startswith(("Kniebeuge", "Bodenstütz")):
                return "spaeter", why
            return "nein", why
    if FREI_RX.search(key):
        return "frei", ""
    if SPAETER_RX.search(key):
        return "spaeter", "Bank/Boden/Last – nach Freigabe"
    return "vorsicht", "Leicht testen, nur beschwerdefrei"


def group_of(x):
    key = x["id"].lower()
    for rx, g in GROUP:
        if re.search(rx, key):
            return g
    return "Oberkörper"


def fetch(path):
    dst = IMG / path
    if dst.exists() and dst.stat().st_size:
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(RAW + urllib.request.quote(path), timeout=30) as r:
        dst.write_bytes(r.read())


def main(src):
    db = {x["id"]: x for x in json.load(open(src, encoding="utf8"))}
    out = []
    for e in OWN:
        img = e.pop("img")
        if img and img not in db:
            print("Bild fehlt:", img)
            img = None
        e["images"] = db[img]["images"] if img else []
        e["img_note"] = "Bild zeigt eine ähnliche Übung" if img and e["id"].startswith("K") else ""
        e["source"] = "Eigene Karte (Wissensbasis)" if e["id"].startswith("K") else "Zusatzkarte Coach"
        e["warn"] = ""
        out.append(e)
    used = {e["id"] for e in out}
    wanted_equip = {"body only", "bands", "dumbbell", None}
    for x in db.values():
        if x["equipment"] not in wanted_equip or x["level"] == "expert" or x["category"] in ("plyometrics", "cardio"):
            continue
        status, why = classify(x)
        out.append(dict(id=x["id"], name=x["name"], group=group_of(x), equip=EQUIP.get(x["equipment"], "–"),
                        status=status, warn=why, start="", steps=x["instructions"], cues=[], images=x["images"],
                        img_note="", lang="en", source="free-exercise-db (Public Domain)",
                        muscles=x["primaryMuscles"]))
    for e in out:
        for p in e["images"]:
            fetch(p)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf8")
    from collections import Counter
    print(len(out), Counter(e["status"] for e in out))


if __name__ == "__main__":
    main(sys.argv[1])
