# Fitness & Diet

Private Coach-App: Tagesplan (Training, Essen, Supplements), Übungsbibliothek mit Bildern,
Rezepte aus Mealie, Verlauf. FastAPI + SQLite, läuft neben dem Trainingsplaner auf debian2.

- URL: `http://192.168.178.66:8091` (unterwegs per VPN)
- Daten: `/docker/fitness-app/data/fitness.db` (Logs, Einstellungen, Yazio-Import)
- Deploy: Ordner nach `/docker/fitness-app` kopieren, dort `docker compose up -d --build`

## Inhalte

| Datei | Inhalt |
|---|---|
| `app/plan.py` | Regeln für Wochen/Tage: Phasen, Einheiten A/B/C, Gehminuten, Essens-Rotation, Aufgaben |
| `app/data/exercises.json` | erzeugt von `tools/build_exercises.py` (eigene Karten K01–K20, Zusatzkarten N21+, free-exercise-db) |
| `app/data/mealie_recipes.json` | 62 ausgewählte Rezepte aus Mealie (Bilder kommen live von Mealie) |
| `app/data/supplements.json` | Supplement-Einordnung, Arztfragen, Quellen |

## API (für Coach / lokales LLM)

- `GET /api/day/YYYY-MM-DD`, `GET /api/week/YYYY-MM-DD`
- `PUT /api/log/YYYY-MM-DD` – `{done, ex, pain:{Achilles,Knie,Nacken,Bauch}, weight, waist, energy, drinks, note, swap}`
- `PUT /api/settings` – `{strength_days: 2|3|4, minutes: 20|30|45, level: "auto"|"1"|"2"|"3", kcal_target, protein_target, doctor_ok}`
- `POST /api/nutrition` – `{date, kcal, protein, carbs, fat, weight}` (iOS-Kurzbefehl aus Apple Health/Yazio). Ohne kcal: keine Änderung, Antwort ok:false; fehlende Makros überschreiben vorhandene nicht. Kurzbefehle: 21:30 heute, 7:00 letzte 3 Tage (Anleitung in den Einstellungen)
- `GET /api/stats`, `GET /api/export`
- `GET /api/homepage` – Kurzwerte für die Homelab-Startseite (Woche/Phase, heute erledigt, als Nächstes, Ernährung, Serie, Gewicht)

Schmerz-Bremse: Ein Wert ≥ 5/10 in den letzten 7 Tagen setzt die Phase eine Stufe zurück.
