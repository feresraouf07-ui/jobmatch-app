"""
jobr – Täglicher Job-Refresh
=============================
Dieses Skript läuft täglich automatisch (via Cron oder launchd).
Es holt neue Jobs von der Bundesagentur für Arbeit und deaktiviert
Jobs, die älter als 30 Tage sind.

Einmaliger Setup:
    chmod +x /Users/feres/JobMatchAI/job_app/jobmatch-app/refresh_jobs.py
    python3 setup_autorefresh.py   # richtet den Cron-Job ein

Manuell ausführen:
    python3 refresh_jobs.py
    python3 refresh_jobs.py --deactivate-old   # zusätzlich alte Jobs deaktivieren
"""

import sys
import json
import time
import logging
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path
from supabase import create_client

# ── Logging ──────────────────────────────────────────────────────────────────
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "refresh_jobs.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("jobr-refresh")

# ── Supabase ─────────────────────────────────────────────────────────────────
SUPABASE_URL = "https://ktvcbcklbgetapjakjys.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt0dmNiY2tsYmdldGFwamFranlzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjY3MjMzMiwiZXhwIjoyMDkyMjQ4MzMyfQ.24VSVH-8W82fO9bHq_FYZTosM3KygdV5bO0u_VPoZz8"
sb = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── Konfiguration ─────────────────────────────────────────────────────────────
SUCHBEGRIFFE = [
    "Marketing", "Sales", "Vertrieb", "IT", "Softwareentwickler",
    "Logistik", "Kundenservice", "HR", "Finance", "Controlling",
    "Data Analyst", "UX Designer", "Werkstudent", "Ausbildung",
]
STAEDTE = ["Düsseldorf", "Köln", "Hamburg", "Berlin", "München", "Frankfurt"]
MAX_JOBS_PRO_KOMBINATION = 5
DEACTIVATE_AFTER_DAYS = 30

JOBART_MAP = {
    "01": "Vollzeit", "02": "Teilzeit", "04": "Minijob",
    "05": "Praktikum", "06": "Ausbildung",
}


# ── BA-API-Fetch ──────────────────────────────────────────────────────────────
def fetch_from_ba_api() -> int:
    """Holt Jobs von der BA-API und trägt neue in Supabase ein.
    Gibt die Anzahl der neu eingetragenen Jobs zurück."""
    headers = {"X-API-Key": "jobboerse-jobsuche-ui"}
    inserted = 0
    api_errors = 0

    log.info("=== BA-API Refresh gestartet ===")
    log.info(f"Städte: {STAEDTE}")
    log.info(f"Suchbegriffe: {SUCHBEGRIFFE}")

    for stadt in STAEDTE:
        for begriff in SUCHBEGRIFFE:
            url = (
                "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs"
                f"?was={requests.utils.quote(begriff)}"
                f"&wo={requests.utils.quote(stadt)}"
                f"&umkreis=25&size={MAX_JOBS_PRO_KOMBINATION}&angebotsart=1"
            )
            try:
                resp = requests.get(url, headers=headers, timeout=15)
                resp.raise_for_status()
                stellenangebote = resp.json().get("stellenangebote") or []

                for s in stellenangebote:
                    count = _upsert_ba_job(s, stadt, begriff)
                    inserted += count
                    time.sleep(0.1)

            except requests.RequestException as e:
                log.warning(f"  API-Fehler ({stadt}/{begriff}): {e}")
                api_errors += 1
            time.sleep(0.4)  # Rate-Limit der BA-API respektieren

    log.info(f"=== Fetch abgeschlossen: {inserted} neue Jobs, {api_errors} API-Fehler ===")
    return inserted


def _upsert_ba_job(s: dict, fallback_stadt: str, suchbegriff: str) -> int:
    """Trägt einen BA-API-Job in Supabase ein (überspringt Duplikate)."""
    title = s.get("titel", "").strip()
    company = s.get("arbeitgeber", "Unbekannt").strip()
    if not title or not company:
        return 0

    # Duplikat-Check
    existing = sb.table("jobs").select("id") \
        .eq("title", title).eq("company", company).execute()
    if existing.data:
        return 0

    city = s.get("arbeitsort", {}).get("ort", fallback_stadt)
    job_type = JOBART_MAP.get(str(s.get("angebotsart", "01")), "Vollzeit")
    ref_nr = s.get("refnr", "")
    apply_url = (
        f"https://jobboerse.arbeitsagentur.de/vamJB/startseite.html?kuerzel={ref_nr}"
        if ref_nr else ""
    )

    # Stichworte aus Titel extrahieren
    keywords = [w.lower() for w in title.split() if len(w) > 3][:6]
    if suchbegriff.lower() not in keywords:
        keywords.append(suchbegriff.lower())

    job_data = {
        "title": title,
        "company": company,
        "city": city,
        "country": "Deutschland",
        "job_type": job_type,
        "work_model": "Vor Ort",
        "salary_min": 0,
        "salary_unit": "€/Monat",
        "languages": ["Deutsch"],
        "experience": "Berufseinsteiger",
        "skills": [],
        "keywords": keywords[:8],
        "description": s.get("stellenbeschreibung", f"{title} bei {company} in {city}."),
        "requirements_text": "",
        "benefits": [],
        "urgency": 7,
        "recency": 10,
        "entry_friendly": True,
        "is_active": True,
        "featured": False,
        "puls": "Neu eingestellt",
        "apply_url": apply_url,
    }

    try:
        sb.table("jobs").insert(job_data).execute()
        log.info(f"  ✅  {title} @ {company} ({city})")
        return 1
    except Exception as e:
        log.warning(f"  ❌  Insert-Fehler für '{title}': {e}")
        return 0


# ── Alte Jobs deaktivieren ────────────────────────────────────────────────────
def deactivate_old_jobs() -> int:
    """Setzt is_active=False für Jobs, die älter als DEACTIVATE_AFTER_DAYS Tage sind.
    Gibt Anzahl der deaktivierten Jobs zurück."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=DEACTIVATE_AFTER_DAYS)).isoformat()
    log.info(f"=== Deaktiviere Jobs älter als {DEACTIVATE_AFTER_DAYS} Tage (vor {cutoff[:10]}) ===")

    try:
        result = sb.table("jobs") \
            .update({"is_active": False}) \
            .eq("is_active", True) \
            .lt("created_at", cutoff) \
            .execute()
        count = len(result.data) if result.data else 0
        log.info(f"  {count} Jobs deaktiviert.")
        return count
    except Exception as e:
        log.error(f"  Fehler beim Deaktivieren: {e}")
        return 0


# ── Haupt-Routine ─────────────────────────────────────────────────────────────
def main():
    start = datetime.now()
    log.info(f"{'═'*55}")
    log.info(f"jobr Job-Refresh  –  {start.strftime('%d.%m.%Y %H:%M')}")
    log.info(f"{'═'*55}")

    try:
        new_jobs = fetch_from_ba_api()
    except Exception as e:
        log.error(f"Kritischer Fehler beim Fetch: {e}")
        new_jobs = 0

    deactivated = 0
    if "--deactivate-old" in sys.argv:
        try:
            deactivated = deactivate_old_jobs()
        except Exception as e:
            log.error(f"Fehler beim Deaktivieren: {e}")

    duration = (datetime.now() - start).total_seconds()
    log.info(f"{'─'*55}")
    log.info(f"  Neue Jobs       : {new_jobs}")
    log.info(f"  Deaktiviert     : {deactivated}")
    log.info(f"  Dauer           : {duration:.1f}s")
    log.info(f"{'─'*55}\n")


if __name__ == "__main__":
    main()
