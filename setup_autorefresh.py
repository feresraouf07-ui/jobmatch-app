"""
jobr – Cron-Setup für täglichen Job-Refresh
============================================
Einmalig ausführen, dann läuft der Refresh jeden Tag automatisch:

    python3 setup_autorefresh.py

Was dieses Skript tut:
  1. Findet den Pfad zu Python3 und zu refresh_jobs.py
  2. Erstellt einen Cron-Job: täglich um 07:00 Uhr
  3. Schreibt Logs nach jobmatch-app/logs/refresh_jobs.log

Cron entfernen:
    crontab -e   →  Zeile mit refresh_jobs.py löschen

Aktuellen Cron anzeigen:
    crontab -l
"""

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
REFRESH_SCRIPT = SCRIPT_DIR / "refresh_jobs.py"

# ── Python-Pfad ermitteln ─────────────────────────────────────────────────────
python_path = sys.executable  # Derselbe Python, der dieses Skript ausführt


def get_current_crontab() -> str:
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        return result.stdout if result.returncode == 0 else ""
    except Exception:
        return ""


def main():
    print("\n🔧 jobr – Auto-Refresh Setup")
    print("=" * 45)
    print(f"  Python     : {python_path}")
    print(f"  Skript     : {REFRESH_SCRIPT}")
    print()

    if not REFRESH_SCRIPT.exists():
        print("❌  refresh_jobs.py nicht gefunden.")
        print(f"   Erwartet unter: {REFRESH_SCRIPT}")
        sys.exit(1)

    # Cron-Zeile: täglich 07:00 Uhr, mit --deactivate-old einmal pro Woche (Montags)
    daily_line = (
        f"0 7 * * * {python_path} {REFRESH_SCRIPT} "
        f">> {SCRIPT_DIR}/logs/cron.log 2>&1"
    )
    weekly_deactivate = (
        f"0 7 * * 1 {python_path} {REFRESH_SCRIPT} --deactivate-old "
        f">> {SCRIPT_DIR}/logs/cron.log 2>&1"
    )

    current = get_current_crontab()

    # Schon vorhanden?
    if str(REFRESH_SCRIPT) in current:
        print("ℹ️  Cron-Job bereits eingerichtet. Kein Update nötig.")
        print("\nAktueller Crontab:")
        print(current)
        return

    new_crontab = current.rstrip("\n") + "\n"
    new_crontab += f"# jobr – Täglicher Job-Refresh (täglich 07:00)\n"
    new_crontab += daily_line + "\n"
    new_crontab += f"# jobr – Alte Jobs deaktivieren (montags 07:00)\n"
    new_crontab += weekly_deactivate + "\n"

    # Neuen Crontab schreiben
    proc = subprocess.run(
        ["crontab", "-"],
        input=new_crontab,
        text=True,
        capture_output=True,
    )

    if proc.returncode == 0:
        print("✅  Cron-Job erfolgreich eingerichtet!\n")
        print("  Refresh läuft jetzt täglich um 07:00 Uhr.")
        print("  Alte Jobs werden jeden Montag deaktiviert.")
        print(f"\n  Logs:  {SCRIPT_DIR}/logs/refresh_jobs.log")
        print(f"         {SCRIPT_DIR}/logs/cron.log")
        print("\nCrontab prüfen:  crontab -l")
        print("Crontab bearbeiten:  crontab -e")
    else:
        print(f"❌  Fehler beim Einrichten: {proc.stderr}")
        print("\nAlternativ: Crontab manuell öffnen mit 'crontab -e' und eintragen:")
        print(f"\n{daily_line}\n{weekly_deactivate}\n")


if __name__ == "__main__":
    main()
