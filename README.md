# JobMatch AI

Streamlit-App, die Profile mit passenden Jobs verbindet. Backend: Supabase (Auth + Datenbank).

## Lokal starten

```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Werte in secrets.toml mit deinem Supabase-Projekt ausfuellen
streamlit run app.py
```

## Deployment

Auf [share.streamlit.io](https://share.streamlit.io) das Repo verbinden und in den
App-Settings unter "Secrets" denselben Inhalt wie in `secrets.toml.example` einfuegen.
