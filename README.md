# JobMatch AI

Streamlit-Webapp, die junge Leute mit passenden Jobs verbindet.
Backend: Supabase (Auth + Datenbank).

Live: `https://<deine-app>.streamlit.app`

---

## So aenderst du was an der App

### Aenderung machen + veroeffentlichen

```bash
cd ~/JobMatchAI/job_app/jobmatch-app
# Datei aendern (z. B. app.py oder .streamlit/config.toml)
streamlit run app.py        # lokal testen
git add .
git commit -m "Was geaendert wurde, in einem Satz"
git push
```

Sobald der Push durch ist, deployt Streamlit Cloud **automatisch** in ~1 Min. neu.
Du musst nichts klicken.

### Aussehen aendern (Farben, Schrift)

In `.streamlit/config.toml` die Werte unter `[theme]` anpassen.
Auch lokal sofort sichtbar nach Reload.

### Geheime Werte aendern (Keys, URLs)

Lokal: `.streamlit/secrets.toml`
Live: Streamlit Cloud Dashboard -> App -> Settings -> Secrets

Beide muessen denselben Inhalt haben.

---

## Lokal starten (erstes Mal)

```bash
cd ~/JobMatchAI/job_app/jobmatch-app
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# secrets.toml mit echten Supabase-Werten ausfuellen
streamlit run app.py
```

---

## Hilfreiche Commands

| Was | Command |
|---|---|
| App lokal starten | `streamlit run app.py` |
| Was hat sich geaendert? | `git status` |
| Aenderungen rueckgaengig (vor Commit) | `git restore <datei>` |
| Letzten Commit ansehen | `git show HEAD` |
| Logs auf Streamlit Cloud | Dashboard -> App -> Manage app |
