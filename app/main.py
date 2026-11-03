"""Fitness & Diet – Backend (FastAPI + SQLite)."""
import base64
import json
import os
import secrets
import sqlite3
import time
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from . import plan

DATA = Path(os.environ.get("DATA_DIR", "/data"))
DATA.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA / "fitness.db"
PASSWORD = os.environ.get("APP_PASSWORD", "").strip()
TRAINER_URL = os.environ.get("TRAINER_EVENTS_URL", "").strip()
MEALIE_URL = os.environ.get("MEALIE_URL", "http://192.168.178.195:9925").rstrip("/")
HERE = Path(__file__).parent
STATIC = HERE / "static"


def load(name):
    return json.loads((HERE / "data" / name).read_text(encoding="utf8"))


EXERCISES = load("exercises.json")
EX_BY_ID = {e["id"]: e for e in EXERCISES}
RECIPES = load("mealie_recipes.json")
RCP_BY_SLUG = {r["slug"]: r for r in RECIPES}
SUPPS = load("supplements.json")

SCHEMA = """
CREATE TABLE IF NOT EXISTS logs(day TEXT PRIMARY KEY, data TEXT NOT NULL DEFAULT '{}', updated TEXT);
CREATE TABLE IF NOT EXISTS settings(k TEXT PRIMARY KEY, v TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS nutrition(day TEXT PRIMARY KEY, kcal REAL, protein REAL, carbs REAL, fat REAL,
  source TEXT, updated TEXT);
"""
DEFAULT_SETTINGS = {"strength_days": 2, "minutes": 20, "level": "auto", "kcal_target": 2200,
                    "protein_target": 140, "doctor_ok": False, "locations": None}


def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


with db() as _c:
    _c.executescript(SCHEMA)


def now():
    return datetime.now().isoformat(timespec="seconds")


def get_settings():
    s = dict(DEFAULT_SETTINGS)
    with db() as c:
        for r in c.execute("SELECT k, v FROM settings"):
            s[r["k"]] = json.loads(r["v"])
    return s


def get_log(c, day):
    r = c.execute("SELECT data FROM logs WHERE day=?", (day,)).fetchone()
    return json.loads(r["data"]) if r else {}


_events = {"t": 0, "data": []}


def events():
    """Handball-Termine aus dem Trainingsplaner (gecacht, 30 Min.)."""
    if not TRAINER_URL:
        return []
    if time.time() - _events["t"] > 1800:
        try:
            with urllib.request.urlopen(TRAINER_URL, timeout=5) as r:
                _events["data"] = json.load(r).get("events", [])
        except Exception:
            pass
        _events["t"] = time.time()
    return _events["data"]


def pain_hold(c, d: date):
    """Bremse: Schmerz >= 5/10 in den letzten 7 Tagen -> eine Stufe zurück."""
    since = (d - timedelta(days=7)).isoformat()
    for r in c.execute("SELECT day, data FROM logs WHERE day>=? AND day<?", (since, d.isoformat())):
        pain = json.loads(r["data"]).get("pain", {})
        if any((v or 0) >= 5 for v in pain.values() if isinstance(v, (int, float))):
            return True
    return False


def day_payload(d: date, settings, c):
    p = plan.build_day(d, settings, events(), hold=pain_hold(c, d))
    p["log"] = get_log(c, d.isoformat())
    n = c.execute("SELECT * FROM nutrition WHERE day=?", (d.isoformat(),)).fetchone()
    p["nutrition"] = dict(n) if n else None
    # Tausch-Wünsche (anderes Rezept) aus dem Log anwenden
    for b in p["blocks"]:
        sw = p["log"].get("swap", {}).get(b["id"])
        if sw:
            b["recipe"] = sw
    total = [b["id"] for b in p["blocks"] if b["kind"] in ("workout", "walk", "meal", "supp", "move") and not b.get("optional")]
    done = p["log"].get("done", {})
    p["score"] = {"done": sum(1 for i in total if done.get(i)), "total": len(total)}
    return p


app = FastAPI(title="Fitness & Diet")


@app.middleware("http")
async def basic_auth(request: Request, call_next):
    if PASSWORD and request.url.path != "/api/health":
        ok = False
        h = request.headers.get("authorization", "")
        if h.startswith("Basic "):
            try:
                _, _, pw = base64.b64decode(h[6:]).decode().partition(":")
                ok = secrets.compare_digest(pw, PASSWORD)
            except Exception:
                ok = False
        if not ok:
            return Response(status_code=401, headers={"WWW-Authenticate": 'Basic realm="Fitness"'})
    resp = await call_next(request)
    if not request.url.path.startswith("/img/"):
        resp.headers["Cache-Control"] = "no-cache"
    return resp


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/config")
def config():
    return {"mealie": MEALIE_URL, "start": plan.START.isoformat(), "weeks": plan.WEEKS, "phases": plan.PHASES,
            "settings": get_settings(), "strength_options": list(plan.STRENGTH_DAYS)}


@app.get("/api/day/{day}")
def get_day(day: str):
    d = date.fromisoformat(day)
    with db() as c:
        return day_payload(d, get_settings(), c)


@app.get("/api/week/{day}")
def get_week(day: str):
    d = date.fromisoformat(day)
    mon = d - timedelta(days=d.weekday())
    s = get_settings()
    with db() as c:
        days = [day_payload(mon + timedelta(days=i), s, c) for i in range(7)]
    return {"monday": mon.isoformat(), "week": plan.week_no(mon), "days": days,
            "tasks": plan.WEEK_TASKS.get(plan.week_no(mon), [])}


@app.put("/api/log/{day}")
async def put_log(day: str, request: Request):
    date.fromisoformat(day)
    body = await request.json()
    with db() as c:
        cur = get_log(c, day)
        cur.update(body)
        c.execute("INSERT INTO logs(day, data, updated) VALUES(?,?,?) ON CONFLICT(day) DO UPDATE SET data=excluded.data,"
                  " updated=excluded.updated", (day, json.dumps(cur, ensure_ascii=False), now()))
    return cur


@app.put("/api/settings")
async def put_settings(request: Request):
    body = await request.json()
    with db() as c:
        for k, v in body.items():
            if k not in DEFAULT_SETTINGS:
                raise HTTPException(400, f"unbekannte Einstellung {k}")
            c.execute("INSERT INTO settings(k, v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v", (k, json.dumps(v)))
    return get_settings()


@app.get("/api/exercises")
def exercises():
    return EXERCISES


@app.get("/api/recipes")
def recipes():
    return RECIPES


@app.get("/api/supplements")
def supplements():
    return SUPPS


@app.post("/api/nutrition")
async def post_nutrition(request: Request):
    """Import aus Apple Health (iOS-Kurzbefehl, Werte von Yazio).
    Body: {"date": "YYYY-MM-DD", "kcal": .., "protein": .., "carbs": .., "fat": .., "weight": ..}
    Zahlen dürfen auch als Text mit Komma kommen."""
    b = await request.json()

    def num(v):
        if v in (None, ""):
            return None
        t = str(v).split()[0]
        if "," in t:  # deutsches Format aus dem Kurzbefehl: 2.150,5
            t = t.replace(".", "").replace(",", ".")
        try:
            return round(float(t), 1)
        except ValueError:
            return None

    day = str(b.get("date") or date.today().isoformat())[:10]
    date.fromisoformat(day)
    vals = {k: num(b.get(k)) for k in ("kcal", "protein", "carbs", "fat")}
    with db() as c:
        c.execute("INSERT INTO nutrition(day,kcal,protein,carbs,fat,source,updated) VALUES(?,?,?,?,?,?,?) "
                  "ON CONFLICT(day) DO UPDATE SET kcal=excluded.kcal, protein=excluded.protein, carbs=excluded.carbs,"
                  " fat=excluded.fat, source=excluded.source, updated=excluded.updated",
                  (day, vals["kcal"], vals["protein"], vals["carbs"], vals["fat"], b.get("source", "health"), now()))
        w = num(b.get("weight"))
        if w:
            cur = get_log(c, day)
            cur.setdefault("weight", w)
            c.execute("INSERT INTO logs(day, data, updated) VALUES(?,?,?) ON CONFLICT(day) DO UPDATE SET "
                      "data=excluded.data, updated=excluded.updated", (day, json.dumps(cur), now()))
    return {"ok": True, "day": day, **vals}


@app.get("/api/stats")
def stats():
    with db() as c:
        logs = {r["day"]: json.loads(r["data"]) for r in c.execute("SELECT day, data FROM logs ORDER BY day")}
        nut = {r["day"]: dict(r) for r in c.execute("SELECT * FROM nutrition ORDER BY day")}
        s = get_settings()
        # Serie: Tage in Folge mit >= 60 % erledigt (ab gestern rückwärts, heute zählt, wenn schon erreicht)
        streak, d = 0, date.today()
        first = True
        while d >= plan.START:
            p = day_payload(d, s, c)
            ok = p["score"]["total"] and p["score"]["done"] / p["score"]["total"] >= 0.6
            if ok:
                streak += 1
            elif not first:
                break
            first = False
            d -= timedelta(days=1)
    series = [{"day": k, "weight": v.get("weight"), "waist": v.get("waist"), "pain": v.get("pain", {}),
               "energy": v.get("energy")} for k, v in logs.items()]
    return {"series": series, "nutrition": list(nut.values()), "streak": streak}


@app.get("/api/export")
def export():
    """Alles für den Coach (Claude) bzw. ein lokales LLM."""
    with db() as c:
        logs = {r["day"]: json.loads(r["data"]) for r in c.execute("SELECT day, data FROM logs ORDER BY day")}
        nut = [dict(r) for r in c.execute("SELECT * FROM nutrition ORDER BY day")]
    return {"settings": get_settings(), "logs": logs, "nutrition": nut}


app.mount("/img", StaticFiles(directory=STATIC / "img"), name="img")
app.mount("/", StaticFiles(directory=STATIC, html=True), name="static")
