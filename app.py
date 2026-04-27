import streamlit as st
from datetime import date, timedelta

st.set_page_config(page_title="JobMatch AI", page_icon="briefcase", layout="centered")

#  Supabase 
SUPABASE_URL = "https://ktvcbcklbgetapjakjys.supabase.co"
SUPABASE_KEY = "sb_publishable_SqfU3Nk3VQpLbw0FaGfu9w_ejrMddr8"

@st.cache_resource
def get_sb():
    try:
        from supabase import create_client
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        return None

def sb_available():
    return get_sb() is not None

# Auth
def sb_register(email, password):
    sb = get_sb()
    if not sb: return None, "Supabase nicht verfügbar"
    try:
        res = sb.auth.sign_up({"email": email, "password": password})
        if res.user: return res.user, None
        return None, "Registrierung fehlgeschlagen."
    except Exception as e:
        msg = str(e)
        if "already" in msg.lower(): return None, "Diese E-Mail ist bereits registriert."
        return None, msg

def sb_login(email, password):
    sb = get_sb()
    if not sb: return None, "Supabase nicht verfügbar"
    try:
        res = sb.auth.sign_in_with_password({"email": email, "password": password})
        if res.user: return res.user, None
        return None, "Login fehlgeschlagen."
    except Exception as e:
        msg = str(e)
        if "Invalid" in msg: return None, "E-Mail oder Passwort falsch."
        return None, msg

# Profil
def sb_save_profile(user_id, profile, xp=0, streak=0, badges=[], ref_code=""):
    sb = get_sb()
    if not sb: return
    try:
        data = {
            "user_id": user_id,
            "vorname": profile.get("vorname",""),
            "nachname": profile.get("nachname",""),
            "geburtsdatum": profile["geburtsdatum"].isoformat() if profile.get("geburtsdatum") else None,
            "stadt": profile.get("stadt",""),
            "umkreis": profile.get("umkreis", 30),
            "jobtitel": profile.get("jobtitel",""),
            "jobart": profile.get("jobart","Vollzeit"),
            "arbeitsmodell": profile.get("arbeitsmodell","Hybrid"),
            "erfahrung": profile.get("erfahrung","Berufseinsteiger"),
            "gehalt_min": profile.get("gehalt_min", 2500),
            "sprachen": profile.get("sprachen",[]),
            "skills": profile.get("skills",[]),
            "extra_skills_text": profile.get("extra_skills_text",""),
            "xp": xp,
            "streak_count": streak,
            "badges": badges,
            "referral_code": ref_code,
        }
        sb.table("profiles").upsert(data, on_conflict="user_id").execute()
    except Exception as e:
        pass  # Stille Fehler — App läuft weiter

def sb_load_profile(user_id):
    sb = get_sb()
    if not sb: return None
    try:
        res = sb.table("profiles").select("*").eq("user_id", user_id).single().execute()
        d = res.data
        if not d: return None
        return {
            "vorname": d.get("vorname",""),
            "nachname": d.get("nachname",""),
            "geburtsdatum": date.fromisoformat(d["geburtsdatum"]) if d.get("geburtsdatum") else date(2000,1,1),
            "stadt": d.get("stadt",""),
            "umkreis": d.get("umkreis", 30),
            "jobtitel": d.get("jobtitel",""),
            "jobart": d.get("jobart","Vollzeit"),
            "arbeitsmodell": d.get("arbeitsmodell","Hybrid"),
            "erfahrung": d.get("erfahrung","Berufseinsteiger"),
            "gehalt_min": d.get("gehalt_min", 2500),
            "sprachen": d.get("sprachen") or [],
            "skills": d.get("skills") or [],
            "extra_skills_text": d.get("extra_skills_text",""),
            "lebenslauf_name": "",
            "zeugnisse_namen": [],
            "startdatum": date.today(),
            "_xp": d.get("xp", 0),
            "_streak": d.get("streak_count", 0),
            "_badges": d.get("badges") or [],
            "_ref_code": d.get("referral_code",""),
        }
    except:
        return None

# Bewerbungen
def sb_save_application(user_id, app):
    sb = get_sb()
    if not sb: return
    try:
        sb.table("applications").insert({
            "user_id": user_id,
            "job_title": app.get("title",""),
            "job_city": app.get("city",""),
            "job_country": app.get("country","Deutschland"),
            "job_type": app.get("job_type",""),
            "work_model": app.get("work_model",""),
            "salary_min": app.get("salary_min", 0),
            "salary_unit": app.get("salary_unit","€/Monat"),
            "score": app.get("score", 0),
            "status": app.get("status","Beworben"),
            "description": app.get("description",""),
            "requirements_text": app.get("requirements_text",""),
            "skills": app.get("skills",[]),
            "experience": app.get("experience",""),
        }).execute()
    except: pass

def sb_load_applications(user_id):
    sb = get_sb()
    if not sb: return []
    try:
        res = sb.table("applications").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        result = []
        for d in (res.data or []):
            result.append({
                "title": d.get("job_title",""),
                "city": d.get("job_city",""),
                "country": d.get("job_country","Deutschland"),
                "job_type": d.get("job_type",""),
                "work_model": d.get("work_model",""),
                "salary_min": d.get("salary_min", 0),
                "salary_unit": d.get("salary_unit","€/Monat"),
                "score": d.get("score", 0),
                "status": d.get("status","Beworben"),
                "description": d.get("description",""),
                "requirements_text": d.get("requirements_text",""),
                "skills": d.get("skills") or [],
                "experience": d.get("experience",""),
                "_db_id": d.get("id"),
            })
        return result
    except: return []

def sb_update_app_status(db_id, new_status):
    sb = get_sb()
    if not sb or not db_id: return
    try:
        sb.table("applications").update({"status": new_status}).eq("id", db_id).execute()
    except: pass

# Nachrichten
def sb_save_message(user_id, app_key, sender, text):
    sb = get_sb()
    if not sb: return
    try:
        sb.table("messages").insert({
            "user_id": user_id, "app_key": app_key,
            "sender": sender, "text": text,
        }).execute()
    except: pass

def sb_load_messages(user_id):
    sb = get_sb()
    if not sb: return {}
    try:
        res = sb.table("messages").select("*").eq("user_id", user_id).order("created_at").execute()
        msgs = {}
        for d in (res.data or []):
            k = d.get("app_key","")
            if k not in msgs: msgs[k] = []
            msgs[k].append({"sender": d.get("sender",""), "text": d.get("text",""),
                            "time": (d.get("created_at","") or "")[:10]})
        return msgs
    except: return {}

# Social Feed
def sb_add_feed(user_id, username, text, xp):
    sb = get_sb()
    if not sb: return
    try:
        sb.table("social_feed").insert({"user_id": user_id, "username": username, "text": text, "xp": xp}).execute()
    except: pass

def sb_load_feed():
    sb = get_sb()
    if not sb: return []
    try:
        res = sb.table("social_feed").select("*").order("created_at", desc=True).limit(20).execute()
        return [{"user": d.get("username","Anonym"), "text": d.get("text",""), "xp": d.get("xp",0),
                 "date": (d.get("created_at","") or "")[:10]} for d in (res.data or [])]
    except: return []

TOTAL_STEPS_SEEKER = 11
TOTAL_STEPS_EMPLOYER = 7
MINDESTALTER = 14

JOBARTEN = ["Vollzeit","Teilzeit","Minijob","Werkstudent","Praktikum","Schülerpraktikum","Ausbildung","Ferienjob","Work and Travel"]
ARBEITSMODELLE = ["Vor Ort","Hybrid","Remote","Egal"]
ERFAHRUNGSLEVEL = ["Berufseinsteiger","1-2 Jahre","3-5 Jahre","5+ Jahre"]
APPLICATION_STATUSES = ["Gemerkt","Beworben","In Prüfung","Interview","Angebot","Angenommen","Abgelehnt"]
SKILL_OPTIONEN = ["Kommunikation","Organisation","Teamarbeit","Kundenkontakt","Verkauf","Marketing","Projektmanagement","Excel","Präsentation","Zeitmanagement","Social Media","Kreativität","Verlässlichkeit","Handwerkliches Geschick","Pflege","Gastronomie","Logistik","Verwaltung","Buchhaltung","Beratung","Design","Python","SQL"]
SPRACH_OPTIONEN = ["Deutsch","Englisch","Französisch","Spanisch","Arabisch","Türkisch","Italienisch","Polnisch"]
BENEFIT_OPTIONEN = ["Deutschlandticket","Homeoffice","Remote","Weiterbildung","Bonus","Flexible Zeiten","Mentoring","Equipment","Mitarbeiterrabatt","Verpflegung","Betriebliche Altersvorsorge"]

DISTANCE_MATRIX = {
    "düsseldorf":{"Düsseldorf":0,"Neuss":8,"Köln":42,"Dortmund":70,"Berlin":565,"München":613,"Hamburg":410,"Frankfurt":228},
    "münchen":{"München":0,"Augsburg":64,"Nürnberg":170,"Berlin":585,"Hamburg":775,"Köln":575,"Düsseldorf":613,"Frankfurt":394},
    "berlin":{"Berlin":0,"Potsdam":27,"Leipzig":190,"Hamburg":289,"München":585,"Düsseldorf":565,"Frankfurt":545,"Köln":575},
    "köln":{"Köln":0,"Bonn":29,"Düsseldorf":42,"Dortmund":95,"Frankfurt":190,"Berlin":575,"München":575,"Hamburg":420},
    "hamburg":{"Hamburg":0,"Bremen":122,"Berlin":289,"Hannover":150,"Köln":420,"Düsseldorf":410,"Frankfurt":493,"München":775},
    "frankfurt":{"Frankfurt":0,"Wiesbaden":38,"Mainz":43,"Köln":190,"Düsseldorf":228,"Berlin":545,"Hamburg":493,"München":394},
}

INTERVIEW_FRAGEN = {
    "Vollzeit": [
        "Warum bewirbst du dich genau bei uns und nicht bei einem Mitbewerber?",
        "Beschreibe eine Situation, in der du unter Druck erfolgreich gearbeitet hast.",
        "Wo siehst du dich in 3 Jahren?",
        "Was sind deine größten Stärken — und eine ehrliche Schwäche?",
        "Wie gehst du mit Feedback um, das du nicht erwartet hast?",
    ],
    "Werkstudent": [
        "Wie planst du Studium und Arbeit zeitlich zu vereinbaren?",
        "Was erhoffst du dir von dieser Werkstudentenstelle für deine Karriere?",
        "Welche Kurse aus deinem Studium sind direkt für diesen Job relevant?",
        "Beschreibe ein Uni-Projekt, in dem du Verantwortung übernommen hast.",
        "Wie viele Stunden pro Woche kannst du realistisch arbeiten?",
    ],
    "Praktikum": [
        "Was möchtest du in diesem Praktikum konkret lernen?",
        "Welche Erwartungen hast du an deine Betreuung?",
        "Beschreibe ein Schulprojekt, das dich auf diese Stelle vorbereitet hat.",
        "Warum interessiert dich diese Branche?",
        "Was machst du, wenn du eine Aufgabe nicht verstehst?",
    ],
    "Teilzeit": [
        "Warum suchst du gezielt eine Teilzeitstelle?",
        "Wie organisierst du deine Zeit, wenn mehrere Aufgaben gleichzeitig anfallen?",
        "Was sind deine festen Verfügbarkeiten pro Woche?",
        "Wie schnell kannst du dich in neue Aufgabenbereiche einarbeiten?",
        "Was motiviert dich bei der Arbeit am meisten?",
    ],
    "Minijob": [
        "Wann kannst du anfangen und welche Tage bist du verfügbar?",
        "Hast du Erfahrung in ähnlichen Jobs gesammelt?",
        "Wie gehst du mit schwierigen Kunden oder stressigen Situationen um?",
        "Was weißt du bereits über unser Unternehmen?",
        "Wie lange planst du, in dieser Position zu bleiben?",
    ],
    "Ausbildung": [
        "Warum hast du dich für genau diesen Ausbildungsberuf entschieden?",
        "Was weißt du über den Ablauf einer dualen Ausbildung?",
        "Wie lernst du am effektivsten — eher durch Theorie oder Praxis?",
        "Was erwartest du von deinen Ausbildern?",
        "Wo möchtest du nach der Ausbildung stehen?",
    ],
    "Ferienjob": [
        "In welchem Zeitraum bist du verfügbar?",
        "Hast du körperlich anspruchsvolle Arbeit schon gemacht?",
        "Wie gehst du mit Schichtarbeit um?",
        "Kannst du auch kurzfristig einspringen?",
        "Was motiviert dich, diesen Job zu machen?",
    ],
    "Schülerpraktikum": [
        "Warum hast du dich für unser Unternehmen entschieden?",
        "Was interessiert dich an diesem Berufsfeld?",
        "Was erhoffst du dir von diesem Praktikum mitzunehmen?",
        "Bist du eher selbstständig oder arbeitest du lieber im Team?",
        "Was machst du in deiner Freizeit — gibt es Hobbys die zu uns passen?",
    ],
    "Work and Travel": [
        "Wie lange planst du im Ausland zu bleiben?",
        "Hast du Erfahrung mit selbstständigem Reisen und Organisieren?",
        "Welche Sprachen sprichst du und auf welchem Niveau?",
        "Wie gehst du mit unbekannten Situationen und kulturellen Unterschieden um?",
        "Was erhoffst du dir von dieser Erfahrung für dein Leben danach?",
    ],
}

GEHALTS_TIPPS = {
    "€/Stunde": "Bei Stundenjobs: Nenne immer zuerst das obere Ende deiner Vorstellung. Sage konkret: 'Ich stelle mir {max} €/h vor' — nicht eine Spanne. Belege es mit deiner Verlässlichkeit und Flexibilität.",
    "€/Monat": "Bei Monatsgehältern: Recherchiere vorher die Marktüblichkeit. Fordere 10-15% mehr als dein Ziel — so hast du Verhandlungsspielraum. Nenne nie zuerst eine Zahl, wenn der Arbeitgeber noch nicht gefragt hat.",
    "€/Jahr": "Bei Jahresgehältern: Denk in Brutto-Zahlen. Berücksichtige Boni, Urlaubsgeld und Benefits als Teil des Gesamtpakets. Sage: 'Ich suche ein Gesamtpaket von X — wo sehen Sie uns?'",
}

def default_account():
    return {"email":"","password":"","registered":False,"logged_in":False}

def default_profile():
    return {"vorname":"","nachname":"","geburtsdatum":date(2000,1,1),"stadt":"","umkreis":15,"arbeitsmodell":"Vor Ort","startdatum":date.today(),"jobtitel":"","jobart":"Vollzeit","skills":[],"extra_skills_text":"","sprachen":[],"erfahrung":"Berufseinsteiger","gehalt_min":2500,"lebenslauf_name":"","zeugnisse_namen":[]}

def default_job_post():
    return {"title":"","company":"","city":"","country":"Deutschland","job_type":"Vollzeit","work_model":"Vor Ort","salary_min":2500,"salary_unit":"€/Monat","languages":[],"experience":"Berufseinsteiger","skills":[],"extra_skills_text":"","keywords_text":"","description":"","requirements_text":"","benefits":[],"extra_benefits_text":"","urgency":5,"recency":10,"entry_friendly":False,"created_by_user":True}

def base_jobs():
    return [
        # Vollzeit Düsseldorf / Hybrid
        {"title":"Junior Marketing Manager","city":"Düsseldorf","country":"Deutschland","job_type":"Vollzeit","work_model":"Hybrid","salary_min":2800,"salary_unit":"€/Monat","languages":["Deutsch","Englisch"],"experience":"Berufseinsteiger","skills":["Marketing","Kommunikation","Social Media","Kreativität"],"keywords":["marketing","content","kampagne","brand"],"description":"Plane und setze Marketingkampagnen um, erstelle Content und analysiere Performance-Daten.","requirements_text":"Affinität zu Marketing & Kommunikation, strukturiertes Arbeiten, erste Erfahrungen erwünscht.","benefits":["Homeoffice","Weiterbildung","Bonus","Flexible Zeiten"],"urgency":8,"recency":10,"entry_friendly":True,"created_by_user":False,"puls":"Neu eingestellt"},
        {"title":"Sales Manager","city":"Düsseldorf","country":"Deutschland","job_type":"Vollzeit","work_model":"Vor Ort","salary_min":3000,"salary_unit":"€/Monat","languages":["Deutsch","Englisch"],"experience":"Berufseinsteiger","skills":["Verkauf","Kommunikation","Kundenkontakt","Präsentation"],"keywords":["sales","vertrieb","verkauf","account"],"description":"Akquiriere Neukunden, pflege Bestandskunden und präsentiere unser Produktportfolio überzeugend.","requirements_text":"Kommunikationsstärke, Abschlussorientierung und Spaß an Vertrieb.","benefits":["Bonus","Deutschlandticket","Equipment","Mentoring"],"urgency":9,"recency":9,"entry_friendly":True,"created_by_user":False,"puls":"Sehr gesucht"},
        {"title":"Content Creator & Social Media","city":"Düsseldorf","country":"Deutschland","job_type":"Vollzeit","work_model":"Hybrid","salary_min":2600,"salary_unit":"€/Monat","languages":["Deutsch","Englisch"],"experience":"Berufseinsteiger","skills":["Social Media","Kreativität","Marketing","Kommunikation"],"keywords":["content","social media","creator","instagram","tiktok"],"description":"Erstelle kreativen Content für Instagram, TikTok und LinkedIn, plane Redaktionskalender und analysiere Reichweiten.","requirements_text":"Gespür für Trends, erste Erfahrung mit Social Media Plattformen, kreatives Mindset.","benefits":["Flexible Zeiten","Homeoffice","Equipment","Mitarbeiterrabatt"],"urgency":7,"recency":10,"entry_friendly":True,"created_by_user":False,"puls":"Neu eingestellt"},
        {"title":"Projektkoordinator Operations","city":"Düsseldorf","country":"Deutschland","job_type":"Vollzeit","work_model":"Hybrid","salary_min":3200,"salary_unit":"€/Monat","languages":["Deutsch","Englisch"],"experience":"Berufseinsteiger","skills":["Projektmanagement","Organisation","Kommunikation","Excel"],"keywords":["projekt","operations","koordinator","planung"],"description":"Koordiniere Projekte zwischen Teams, erstelle Reports und optimiere interne Abläufe.","requirements_text":"Strukturierte Arbeitsweise, Organisationstalent, erste Projekterfahrung.","benefits":["Weiterbildung","Bonus","Homeoffice","Betriebliche Altersvorsorge"],"urgency":6,"recency":8,"entry_friendly":True,"created_by_user":False,"puls":""},
        {"title":"Account Manager Kundenbetreuung","city":"Düsseldorf","country":"Deutschland","job_type":"Vollzeit","work_model":"Hybrid","salary_min":2900,"salary_unit":"€/Monat","languages":["Deutsch","Englisch"],"experience":"Berufseinsteiger","skills":["Kommunikation","Kundenkontakt","Organisation","Präsentation"],"keywords":["account","kundenbetreuung","client","beratung"],"description":"Betreue einen festen Kundenstamm, löse Anfragen und entwickle langfristige Kundenbeziehungen.","requirements_text":"Serviceorientierung, freundliches Auftreten, strukturiertes Arbeiten.","benefits":["Deutschlandticket","Flexible Zeiten","Weiterbildung","Bonus"],"urgency":7,"recency":9,"entry_friendly":True,"created_by_user":False,"puls":"Sehr gesucht"},
        {"title":"HR & Recruiting Coordinator","city":"Düsseldorf","country":"Deutschland","job_type":"Vollzeit","work_model":"Hybrid","salary_min":2800,"salary_unit":"€/Monat","languages":["Deutsch","Englisch"],"experience":"Berufseinsteiger","skills":["Kommunikation","Organisation","Beratung","Präsentation"],"keywords":["hr","recruiting","personal","hiring"],"description":"Koordiniere Bewerbungsprozesse, führe erste Interviews und unterstütze das HR-Team.","requirements_text":"Interesse an Menschen und HR, Organisationstalent, Diskretion.","benefits":["Homeoffice","Weiterbildung","Mentoring","Flexible Zeiten"],"urgency":6,"recency":8,"entry_friendly":True,"created_by_user":False,"puls":""},
        {"title":"E-Commerce Manager","city":"Düsseldorf","country":"Deutschland","job_type":"Vollzeit","work_model":"Hybrid","salary_min":3000,"salary_unit":"€/Monat","languages":["Deutsch","Englisch"],"experience":"Berufseinsteiger","skills":["Marketing","Excel","Kommunikation","Zeitmanagement"],"keywords":["ecommerce","online shop","digital","amazon"],"description":"Manage unsere Online-Shop-Präsenz, optimiere Produktlistings und analysiere Verkaufsdaten.","requirements_text":"Digitalaffinität, analytisches Denken, erste E-Commerce Kenntnisse von Vorteil.","benefits":["Homeoffice","Bonus","Weiterbildung","Equipment"],"urgency":8,"recency":10,"entry_friendly":True,"created_by_user":False,"puls":"Neu eingestellt"},
        {"title":"Office Manager & Assistenz","city":"Düsseldorf","country":"Deutschland","job_type":"Vollzeit","work_model":"Vor Ort","salary_min":2700,"salary_unit":"€/Monat","languages":["Deutsch"],"experience":"Berufseinsteiger","skills":["Organisation","Kommunikation","Excel","Zeitmanagement"],"keywords":["office","assistenz","management","verwaltung"],"description":"Halte den Büroalltag am Laufen: Terminverwaltung, Korrespondenz, Bestellungen und Empfang.","requirements_text":"Zuverlässigkeit, gepflegtes Auftreten, sehr gute Deutschkenntnisse.","benefits":["Verpflegung","Betriebliche Altersvorsorge","Deutschlandticket"],"urgency":5,"recency":7,"entry_friendly":True,"created_by_user":False,"puls":""},
        # Remote Vollzeit
        {"title":"Junior Data Analyst Remote","city":"Düsseldorf","country":"Deutschland","job_type":"Vollzeit","work_model":"Remote","salary_min":3000,"salary_unit":"€/Monat","languages":["Deutsch","Englisch"],"experience":"Berufseinsteiger","skills":["Excel","Kommunikation","Organisation","Präsentation"],"keywords":["data","analyst","excel","reporting","auswertung"],"description":"Erstelle Reports, analysiere Kundendaten und präsentiere Ergebnisse dem Management.","requirements_text":"Affinität zu Zahlen, Excel-Kenntnisse, strukturiertes Denken.","benefits":["Remote","Weiterbildung","Equipment","Bonus"],"urgency":7,"recency":9,"entry_friendly":True,"created_by_user":False,"puls":""},
        {"title":"Customer Success Manager Remote","city":"Düsseldorf","country":"Deutschland","job_type":"Vollzeit","work_model":"Remote","salary_min":2800,"salary_unit":"€/Monat","languages":["Deutsch","Englisch"],"experience":"Berufseinsteiger","skills":["Kommunikation","Kundenkontakt","Organisation","Beratung"],"keywords":["customer success","support","client","betreuung","remote"],"description":"Begleite Kunden nach dem Kauf, führe Onboardings durch und maximiere Kundenzufriedenheit.","requirements_text":"Empathie, Kommunikationsstärke, selbstständiges Arbeiten im Homeoffice.","benefits":["Remote","Equipment","Flexible Zeiten","Weiterbildung"],"urgency":8,"recency":10,"entry_friendly":True,"created_by_user":False,"puls":"Sehr gesucht"},
        # Test-Job mit hohem Match für Tester
        {"title":"Marketing & Communications Manager","city":"Düsseldorf","country":"Deutschland","job_type":"Vollzeit","work_model":"Hybrid","salary_min":2500,"salary_unit":"€/Monat","languages":["Deutsch","Englisch"],"experience":"Berufseinsteiger","skills":["Marketing","Kommunikation","Social Media","Kreativität","Präsentation","Zeitmanagement"],"keywords":["marketing","communications","manager","brand","pr"],"description":"Entwickle Kommunikationsstrategien, manage Social Media Kanäle und koordiniere externe Agenturen.","requirements_text":"Interesse an Marken und Kommunikation, kreatives Denken, gutes Sprachgefühl.","benefits":["Homeoffice","Weiterbildung","Bonus","Flexible Zeiten","Deutschlandticket"],"urgency":9,"recency":10,"entry_friendly":True,"created_by_user":False,"puls":"Neu · Sehr gesucht"},
    ]

#  State 
DEFAULTS = {
    "step":0,"app_mode":"","auth_mode":"",
    "account":None,"profile":None,"job_post_form":None,
    "posted_jobs":[],"matches":[],"current_match_index":0,
    "liked_jobs":[],"disliked_jobs":[],"applications":[],
    "sort_mode":"Passendste",
    "swipe_stats":{"likes":0,"dislikes":0},
    "consecutive_dislikes":0,
    "anschreiben_job":None,"show_anschreiben":False,
    "streak_last_login":None,"streak_count":0,
    "traumjob_analyse":None,
    "nachrichten":{},"slide_idx":0,
    "active_chat":None,
    "xp":0,"level_name":"Newcomer","level_color":"#6b7280","badges":[],
    "referral_code":"","referred_friends":[],
    "countdown_jobs":{},"social_feed":[],
}
for k,v in DEFAULTS.items():
    if k not in st.session_state:
        if k=="account": st.session_state[k]=default_account()
        elif k=="profile": st.session_state[k]=default_profile()
        elif k=="job_post_form": st.session_state[k]=default_job_post()
        else: st.session_state[k]=v

# Streak
today_str = str(date.today())
last = st.session_state.streak_last_login
if last != today_str:
    if last == str(date.today()-timedelta(days=1)): st.session_state.streak_count += 1
    elif last is None: st.session_state.streak_count = 1
    else: st.session_state.streak_count = 1
    st.session_state.streak_last_login = today_str

# Test-Bewerbung vorinstallieren (Interview-Status zum Testen)
TEST_APP = {"title":"Marketing & Communications Manager","city":"Düsseldorf","country":"Deutschland","job_type":"Vollzeit","work_model":"Hybrid","score":95,"status":"Interview","description":"Entwickle Kommunikationsstrategien, manage Social Media Kanäle und koordiniere externe Agenturen.","requirements_text":"Interesse an Marken und Kommunikation, kreatives Denken, gutes Sprachgefühl.","skills":["Marketing","Kommunikation","Social Media"],"experience":"Berufseinsteiger","salary_unit":"€/Monat"}
if not any(a["title"]==TEST_APP["title"] for a in st.session_state.applications):
    st.session_state.applications.append(TEST_APP)

#  Helpers 
def next_step(): st.session_state.step+=1; st.rerun()
def prev_step():
    if st.session_state.step>0: st.session_state.step-=1; st.rerun()
def reset_all():
    for k in list(st.session_state.keys()): del st.session_state[k]
    st.rerun()
def reset_employer_flow_only():
    st.session_state.job_post_form=default_job_post(); st.session_state.step=100; st.rerun()

def city_distance(search_city, job_city):
    s=search_city.strip().lower()
    if s in DISTANCE_MATRIX: return DISTANCE_MATRIX[s].get(job_city,9999)
    return 0 if s==job_city.strip().lower() else 9999

def is_work_model_compatible(user_model, job_model):
    if user_model=="Egal": return True
    if user_model=="Remote": return job_model=="Remote"
    if user_model=="Hybrid": return job_model in ["Hybrid","Remote"]
    if user_model=="Vor Ort": return job_model in ["Vor Ort","Hybrid"]
    return False

def combined_skills(profile):
    extra=[s.strip() for s in profile["extra_skills_text"].split(",") if s.strip()]
    return list(dict.fromkeys(profile["skills"]+extra))

def combined_job_post_skills(jp):
    extra=[s.strip() for s in jp["extra_skills_text"].split(",") if s.strip()]
    return list(dict.fromkeys(jp["skills"]+extra))

def combined_job_post_benefits(jp):
    extra=[b.strip() for b in jp["extra_benefits_text"].split(",") if b.strip()]
    return list(dict.fromkeys(jp["benefits"]+extra))

def parse_keywords(text): return [k.strip().lower() for k in text.split(",") if k.strip()]
def get_all_jobs(): return base_jobs()+st.session_state.posted_jobs

def get_application_counts():
    counts={s:0 for s in APPLICATION_STATUSES}
    for app in st.session_state.applications:
        s=app.get("status","Gemerkt")
        if s in counts: counts[s]+=1
    return counts

def job_exists_in_applications(job):
    return any(a["title"]==job["title"] and a["city"]==job["city"] and a["job_type"]==job["job_type"] for a in st.session_state.applications)

def add_job_to_applications(job, status="Gemerkt"):
    if not job_exists_in_applications(job):
        st.session_state.applications.append({
            "title":job["title"],"city":job["city"],"country":job["country"],
            "job_type":job["job_type"],"work_model":job["work_model"],
            "score":job["score"],"status":status,
            "description":job["description"],
            "requirements_text":job.get("requirements_text",""),
            "skills":job.get("skills",[]),
            "experience":job.get("experience",""),
            "salary_unit":job.get("salary_unit","€/Monat"),
        })

def update_application_status(index, new_status):
    if 0<=index<len(st.session_state.applications):
        st.session_state.applications[index]["status"]=new_status

def calculate_age(birthdate):
    today=date.today(); years=today.year-birthdate.year
    if (today.month,today.day)<(birthdate.month,birthdate.day): years-=1
    return years

def validate_profile_identity(vorname, nachname, geburtsdatum):
    if not vorname.strip(): return False,"Bitte gib deinen Vornamen ein."
    if not nachname.strip(): return False,"Bitte gib deinen Nachnamen ein."
    if calculate_age(geburtsdatum)<MINDESTALTER: return False,f"Das Mindestalter beträgt {MINDESTALTER} Jahre."
    return True,""

def validate_job_post(jp):
    if not jp["title"].strip(): return False,"Bitte gib einen Jobtitel ein."
    if not jp["city"].strip(): return False,"Bitte gib einen Ort ein."
    if not jp["description"].strip(): return False,"Bitte gib eine Beschreibung ein."
    return True,""

def profil_staerke(profile):
    checks=[(bool(profile["vorname"]),10),(bool(profile["stadt"]),15),(bool(profile["jobtitel"]),15),(bool(profile["skills"]),20),(bool(profile["sprachen"]),10),(bool(profile["lebenslauf_name"]),20),(bool(profile["extra_skills_text"]),10)]
    return sum(pts for cond,pts in checks if cond)

def calculate_matches(profile):
    jobs=get_all_jobs()
    user_city=profile["stadt"].strip()
    radius=profile["umkreis"]
    user_work_model=profile["arbeitsmodell"]
    user_job_title=profile["jobtitel"].strip().lower()
    user_job_type=profile["jobart"]
    user_skills=set(combined_skills(profile))
    user_languages=set(profile["sprachen"])
    user_experience=profile["erfahrung"]
    user_salary_min=profile["gehalt_min"]
    filtered=[]
    for job in jobs:
        distance=city_distance(user_city,job["city"])
        within_radius=distance<=radius
        remote_ok=job["work_model"]=="Remote" and user_work_model in ["Remote","Hybrid","Egal"]
        if not (within_radius or remote_ok): continue
        if not is_work_model_compatible(user_work_model,job["work_model"]): continue
        if job["job_type"]!=user_job_type: continue
        if job["salary_min"]<user_salary_min: continue
        score=40; reason_parts=[]
        if user_job_title:
            if any(k in user_job_title for k in job["keywords"]) or any(w in job["title"].lower() for w in user_job_title.split()):
                score+=20; reason_parts.append(("title","Jobtitel passt zu deiner Suche"))
        matching_skills=[s for s in job["skills"] if s in user_skills]
        if matching_skills:
            score+=min(len(matching_skills)*8,24)
            reason_parts.append(("skills",f"{len(matching_skills)} Skills passen: {', '.join(matching_skills)}"))
        matching_languages=[l for l in job["languages"] if l in user_languages]
        if matching_languages:
            score+=min(len(matching_languages)*5,10)
            reason_parts.append(("lang",f"Sprachen passen: {', '.join(matching_languages)}"))
        if job["experience"]==user_experience:
            score+=8; reason_parts.append(("exp","Erfahrungslevel passt genau"))
        if job["work_model"]==user_work_model:
            score+=8; reason_parts.append(("model",f"Du willst {user_work_model} — dieser Job auch"))
        if distance==0:
            score+=12; reason_parts.append(("dist",f"Direkt in {job['city']} — keine Pendelzeit"))
        elif distance<=radius and job["work_model"]!="Remote":
            score+=8; reason_parts.append(("dist",f"Nur {distance} km von dir entfernt"))
        elif job["work_model"]=="Remote":
            score+=10; reason_parts.append(("dist","Komplett remote — egal wo du bist"))
        if user_experience=="Berufseinsteiger" and job["entry_friendly"]:
            score+=10; reason_parts.append(("entry","Offen für Berufseinsteiger"))
        score=min(score,100)
        missing=[]
        missing_skills=[s for s in job["skills"] if s not in user_skills]
        if missing_skills: missing.append(f"Skills fehlen: {', '.join(missing_skills[:2])}")
        if job["experience"]!=user_experience: missing.append(f"Erfahrung: Job sucht {job['experience']}")
        # Gehalts-Tipp
        salary_unit=job.get("salary_unit","€/Monat")
        max_salary=job["salary_min"]+round(job["salary_min"]*0.15)
        gehalts_tipp=GEHALTS_TIPPS.get(salary_unit,"").replace("{max}",str(max_salary))
        filtered.append({**job,"distance":distance if distance!=9999 else None,"score":score,"reason_parts":reason_parts,"missing":missing,"gehalts_tipp":gehalts_tipp})
    mode=st.session_state.sort_mode
    if mode=="Passendste": filtered.sort(key=lambda x:x["score"],reverse=True)
    elif mode=="Neueste": filtered.sort(key=lambda x:x["recency"],reverse=True)
    elif mode=="Dringend": filtered.sort(key=lambda x:x["urgency"],reverse=True)
    return filtered

def find_similar_jobs(job, all_matches, n=2):
    result=[]
    for m in all_matches:
        if m["title"]==job["title"]: continue
        shared=len(set(m.get("skills",[]))&set(job.get("skills",[])))
        if shared>=1: result.append((shared,m))
    result.sort(key=lambda x:x[0],reverse=True)
    return [m for _,m in result[:n]]

def analyse_ablehnung(app, profile):
    user_skills=set(combined_skills(profile))
    job_skills=set(app.get("skills",[]))
    fehlende=list(job_skills-user_skills)
    lines=[]
    if fehlende: lines.append(f"Dir fehlten diese Skills: {', '.join(fehlende)}")
    if app.get("experience") and app["experience"]!=profile["erfahrung"]:
        lines.append(f"Erfahrung: Job wollte {app['experience']}, du hast {profile['erfahrung']}")
    if not lines: lines.append("Das Profil passte nicht optimal. Versuche ähnliche Jobs mit leicht anderen Filtern.")
    return lines

def get_interview_fragen(job_type, job_skills, profile_skills):
    basis=INTERVIEW_FRAGEN.get(job_type, INTERVIEW_FRAGEN["Vollzeit"])
    matching=[s for s in job_skills if s in set(profile_skills)]
    extra=[]
    if "Marketing" in matching or "Social Media" in matching:
        extra.append("Welche Marketingkampagne hat dich zuletzt wirklich beeindruckt — und warum?")
    if "Python" in matching or "SQL" in matching or "Excel" in matching:
        extra.append("Beschreibe ein konkretes Projekt, bei dem du Daten analysiert oder visualisiert hast.")
    if "Kommunikation" in matching or "Präsentation" in matching:
        extra.append("Halte eine kurze 2-Minuten-Präsentation zu dir selbst — wie würdest du starten?")
    if "Kundenkontakt" in matching or "Verkauf" in matching:
        extra.append("Wie würdest du einem neuen Kunden unser Produkt in 30 Sekunden erklären?")
    if "Projektmanagement" in matching or "Organisation" in matching:
        extra.append("Welche Tools nutzt du für Projektplanung — und wie priorisierst du bei vielen Aufgaben?")
    combined=basis+extra
    return combined[:6]

def sim_arbeitgeber_antwort(app_title):
    """Simuliert eine Arbeitgeber-Antwort (in echtem System: vom Arbeitgeber gesetzt)."""
    import random
    antworten=[
        "Vielen Dank für Ihre Bewerbung! Wir haben sie erhalten und prüfen sie sorgfältig.",
        "Ihre Unterlagen sehen vielversprechend aus. Wir melden uns in den nächsten Tagen.",
        "Danke für Ihr Interesse! Wir prüfen alle Bewerbungen und melden uns bald.",
    ]
    return random.choice(antworten)

def send_nachricht(app_key, text, sender="Bewerber"):
    if app_key not in st.session_state.nachrichten:
        st.session_state.nachrichten[app_key]=[]
    st.session_state.nachrichten[app_key].append({"sender":sender,"text":text,"time":str(date.today())})

def save_job_post():
    form=st.session_state.job_post_form
    valid,message=validate_job_post(form)
    if not valid: st.warning(message); return
    new_job={"title":form["title"].strip(),"city":form["city"].strip(),"country":form["country"].strip() or "Deutschland","job_type":form["job_type"],"work_model":form["work_model"],"salary_min":form["salary_min"],"salary_unit":form["salary_unit"],"languages":form["languages"],"experience":form["experience"],"skills":combined_job_post_skills(form),"keywords":parse_keywords(form["keywords_text"]) if form["keywords_text"].strip() else [form["title"].strip().lower()],"description":form["description"].strip(),"requirements_text":form["requirements_text"].strip(),"benefits":combined_job_post_benefits(form),"urgency":form["urgency"],"recency":10,"entry_friendly":form["entry_friendly"],"created_by_user":True,"puls":""}
    st.session_state.posted_jobs.append(new_job)
    st.session_state.job_post_form=default_job_post()
    st.session_state.step=107; st.rerun()

def like_current_job():
    idx=st.session_state.current_match_index
    if idx<len(st.session_state.matches):
        job=st.session_state.matches[idx]
        st.session_state.liked_jobs.append(job)
        add_job_to_applications(job,"Gemerkt")
        st.session_state.swipe_stats["likes"]+=1
        st.session_state.consecutive_dislikes=0
        st.session_state.current_match_index+=1
        st.session_state.anschreiben_job=job
        st.session_state.show_anschreiben=True
        add_xp("job_gemerkt", st.session_state.profile.get('vorname','Du') + " hat einen Job gemerkt")
        st.rerun()

def apply_current_job(job):
    # Speichere Job-Referenz sicher bevor Index erhöht wird
    saved_job = dict(job)
    already=job_exists_in_applications(saved_job)
    if not already: add_job_to_applications(saved_job,"Beworben")
    else:
        for i,a in enumerate(st.session_state.applications):
            if a["title"]==saved_job["title"] and a["city"]==saved_job["city"]:
                update_application_status(i,"Beworben"); break
    # Auto-Nachricht vom "Arbeitgeber"
    app_key = f"{saved_job['title']}_{saved_job['city']}"
    if app_key not in st.session_state.nachrichten:
        st.session_state.nachrichten[app_key] = []
    st.session_state.nachrichten[app_key].append({
        "sender": "Arbeitgeber",
        "text": f"Vielen Dank für Ihre Bewerbung als {saved_job['title']}! Wir haben Ihre Unterlagen erhalten und prüfen diese sorgfältig. Wir melden uns in Kürze.",
        "time": str(date.today())
    })
    st.session_state.consecutive_dislikes=0
    st.session_state.current_match_index += 1
    st.session_state.anschreiben_job=saved_job
    st.session_state.show_anschreiben=False
    add_xp("beworben", st.session_state.profile.get('vorname','Du') + " hat sich bei " + saved_job['title'] + " beworben")
    # In Supabase speichern
    uid = st.session_state.account.get("sb_user_id")
    if uid:
        sb_save_application(uid, {**saved_job, "status": "Beworben"})
        sb_save_message(uid, app_key, "Arbeitgeber",
            f"Vielen Dank für Ihre Bewerbung als {saved_job['title']}! Wir melden uns in Kürze.")
        sb_add_feed(uid, st.session_state.profile.get("vorname","Anonym"),
            st.session_state.profile.get("vorname","Jemand") + " hat sich bei " + saved_job['title'] + " beworben", 30)
    st.session_state.step=17; st.rerun()

def dislike_current_job():
    idx=st.session_state.current_match_index
    if idx<len(st.session_state.matches):
        st.session_state.disliked_jobs.append(st.session_state.matches[idx])
        st.session_state.swipe_stats["dislikes"]+=1
        st.session_state.consecutive_dislikes+=1
        st.session_state.current_match_index+=1
        st.rerun()

def generate_anschreiben(job, profile):
    vorname=profile.get("vorname",""); nachname=profile.get("nachname","")
    matching=[s for s in job["skills"] if s in set(combined_skills(profile))]
    skills_text=", ".join(matching) if matching else "meine Kenntnisse"
    erfahrung=profile.get("erfahrung","Berufseinsteiger")
    einstieg="Als Berufseinsteiger bringe ich frische Perspektiven und hohe Lernbereitschaft mit." if erfahrung=="Berufseinsteiger" else f"Mit {erfahrung} Berufserfahrung bringe ich relevantes Praxiswissen mit."
    return f"""Sehr geehrte Damen und Herren,

mit großem Interesse habe ich Ihre Stellenausschreibung als {job['title']} in {job['city']} gelesen und möchte mich hiermit bewerben.

{einstieg} Besonders meine Kenntnisse in {skills_text} passen meiner Einschätzung nach gut zu den Anforderungen dieser Stelle.

{job.get('requirements_text','')} — auf genau diese Anforderungen bin ich gut vorbereitet und freue mich darauf, mein Wissen in Ihrem Team einzubringen.

Ich bin motiviert, schnell Verantwortung zu übernehmen und aktiv zum Erfolg Ihres Teams beizutragen.

Über eine Einladung zum Gespräch freue ich mich sehr.

Mit freundlichen Grüßen,
{vorname} {nachname}"""


#  Gamification 
XP_EVENTS = {"job_gemerkt":10,"beworben":30,"interview":75,"anschreiben":20,"profil_komplett":50,"referral":80}
LEVELS = [(0,"Newcomer","#6b7280"),(100,"Jobsucher","#22d3ee"),(300,"Bewerber","#a78bfa"),(600,"Pro","#f59e0b"),(1000,"Top-Talent","#f472b6"),(2000,"Legende","#6366f1")]
BADGE_DATA = {
    "erste_bewerbung": ("","Erster Move","Erste Bewerbung"),
    "streak_3":        ("","On Fire","3 Tage Streak"),
    "streak_7":        ("","Unstoppable","7 Tage Streak"),
    "profil_100":      ("","Vollprofil","100% ausgefüllt"),
    "5_bewerbungen":   ("","Zielstrebig","5 Bewerbungen"),
    "referral_1":      ("","Netzwerker","Freund eingeladen"),
    "interview":       ("","Interview-Ready","Interview erhalten"),
}
DEMO_FRIENDS = [
    {"name":"Lena M.","level":"Pro","xp":640,"apps":8,"streak":12},
    {"name":"Jonas K.","level":"Bewerber","xp":390,"apps":4,"streak":5},
    {"name":"Sara T.","level":"Jobsucher","xp":190,"apps":2,"streak":3},
]

def get_level(xp):
    cur = LEVELS[0]
    for lvl in LEVELS:
        if xp >= lvl[0]: cur = lvl
    idx = LEVELS.index(cur)
    nxt = LEVELS[idx+1] if idx+1 < len(LEVELS) else None
    return cur, nxt

def add_xp(key, feed_text=""):
    pts = XP_EVENTS.get(key, 0)
    if not pts: return
    st.session_state.xp = st.session_state.get("xp",0) + pts
    cur, _ = get_level(st.session_state.xp)
    st.session_state.level_name = cur[1]
    st.session_state.level_color = cur[2]
    badges = st.session_state.get("badges",[])
    apps = [a for a in st.session_state.applications if a.get("status") in ["Beworben","In Prüfung","Interview","Angebot","Angenommen"]]
    if len(apps)>=1 and "erste_bewerbung" not in badges: badges.append("erste_bewerbung")
    if len(apps)>=5 and "5_bewerbungen" not in badges: badges.append("5_bewerbungen")
    if st.session_state.get("streak_count",0)>=3 and "streak_3" not in badges: badges.append("streak_3")
    if st.session_state.get("streak_count",0)>=7 and "streak_7" not in badges: badges.append("streak_7")
    if any(a.get("status")=="Interview" for a in st.session_state.applications) and "interview" not in badges: badges.append("interview")
    if len(st.session_state.get("referred_friends",[]))>=1 and "referral_1" not in badges: badges.append("referral_1")
    st.session_state.badges = badges
    if feed_text:
        feed = st.session_state.get("social_feed",[])
        feed.insert(0,{"user":st.session_state.profile.get("vorname","Du"),"text":feed_text,"xp":pts,"date":str(date.today())})
        st.session_state.social_feed = feed[:20]

def get_match_persona(profile):
    jt = profile.get("jobart","Vollzeit")
    skills = profile.get("skills",[])
    if jt in ["Ferienjob","Schülerpraktikum"]: return "Starter","Du weißt was du willst: Erfahrung sammeln, Geld verdienen, Gas geben. Nichts hält dich auf."
    if jt == "Werkstudent": return "Multitasker","Studium, Job, Leben — du managst alles gleichzeitig. Absoluter Respekt."
    if jt == "Ausbildung": return "Macher","Während andere noch überlegen, bist du schon mittendrin. Hands-on ist dein Ding."
    if jt == "Minijob": return "Flexmaster","Dein Leben, dein Tempo. Du verdienst Geld wann es dir passt. Smart."
    if any(s in skills for s in ["Marketing","Social Media","Kreativität"]): return "Creative","Du denkst in Kampagnen und Stories. Dein Job muss genauso kreativ sein wie du."
    if any(s in skills for s in ["Python","SQL","Programmierung"]): return "Techie","Code ist deine Sprache. Du löst Probleme die andere nicht mal verstehen."
    return "Allrounder","Flexibel, motiviert, lernbereit. Du passt überall rein — und das ist echte Stärke."

def gen_referral(vorname):
    import hashlib
    return "JM-" + hashlib.md5(f"{vorname}{date.today().year}".encode()).hexdigest()[:6].upper()

#  UI-Helpers 
def H(text):
    st.markdown(f"<p style='font-size:22px;font-weight:700;color:#fff;margin:4px 0 2px 0;font-family:Inter,sans-serif;'>{text}</p>",unsafe_allow_html=True)
def hint(text):
    st.markdown(f"<p style='font-size:13px;color:#777;margin-bottom:18px;font-family:Inter,sans-serif;'>{text}</p>",unsafe_allow_html=True)
def lbl(text):
    st.markdown(f"<p style='font-size:11px;color:#666;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:3px;margin-top:10px;font-family:Inter,sans-serif;'>{text}</p>",unsafe_allow_html=True)
def val(text, size=14, color="#e0e0e0"):
    st.markdown(f"<p style='font-size:{size}px;color:{color};font-family:Inter,sans-serif;margin:0 0 4px 0;line-height:1.55;'>{text}</p>",unsafe_allow_html=True)

#  CSS 
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html,body,[data-testid="stAppViewContainer"],[data-testid="stApp"]{background:#000!important;color:#fff!important;font-family:'Inter',sans-serif!important;}
[data-testid="stHeader"]{background:transparent!important;}
[data-testid="stToolbar"]{display:none!important;}
.block-container{padding-top:2rem!important;max-width:640px!important;}
.stTextInput>div>div>input,.stTextArea>div>textarea{background:#111!important;border:1px solid #333!important;border-radius:8px!important;color:#ffffff!important;font-family:'Inter',sans-serif!important;font-size:15px!important;font-weight:500!important;}
.stTextInput>div>div>input::placeholder,.stTextArea>div>textarea::placeholder{color:#555!important;}
.stTextInput>div>div>input:focus,.stTextArea>div>textarea:focus{border-color:#fff!important;box-shadow:none!important;}
.stTextInput label,.stTextArea label,.stSelectbox label,.stMultiSelect label,.stDateInput label,.stSlider label{color:#888!important;font-size:13px!important;font-family:'Inter',sans-serif!important;}
.stSelectbox>div>div{background:#111!important;border:1px solid #333!important;border-radius:8px!important;color:#ffffff!important;font-weight:500!important;}
.stMultiSelect>div>div{background:#111!important;border:1px solid #333!important;border-radius:8px!important;color:#ffffff!important;}
[data-testid="stMultiSelect"] span[data-baseweb="tag"]{background:#222!important;border:1px solid #444!important;border-radius:4px!important;color:#fff!important;}
.stRadio label{color:#ddd!important;font-size:15px!important;}
.stCheckbox label{color:#ddd!important;font-size:15px!important;}
.stProgress>div>div{background:#1a1a1a!important;border-radius:4px!important;}
.stProgress>div>div>div{background:#fff!important;border-radius:4px!important;}
.stButton>button{background:#fff!important;color:#000!important;border:none!important;border-radius:8px!important;padding:0.6rem 1.2rem!important;font-family:'Inter',sans-serif!important;font-weight:600!important;font-size:14px!important;width:100%!important;min-height:44px!important;transition:opacity 0.15s!important;}
.stButton>button:hover{opacity:0.82!important;}
.stDateInput>div>div>input{background:#111!important;border:1px solid #333!important;color:#fff!important;border-radius:8px!important;font-weight:500!important;}
[data-testid="stMetricValue"]{color:#fff!important;font-family:'Inter',sans-serif!important;font-weight:700!important;}
[data-testid="stMetricLabel"]{color:#666!important;font-family:'Inter',sans-serif!important;}
.stCaption,.stCaption p{color:#666!important;font-family:'Inter',sans-serif!important;}
hr{border-color:#1e1e1e!important;}
[data-testid="stFileUploader"]{background:#111!important;border:1px dashed #333!important;border-radius:8px!important;}
[data-testid="stVerticalBlockBorderWrapper"]{border:1px solid #2a2a2a!important;border-radius:12px!important;background:#0d0d0d!important;box-shadow:0 0 0 1px #222,0 4px 24px rgba(0,0,0,0.6)!important;}
p,div,span{font-family:'Inter',sans-serif!important;}
</style>
""",unsafe_allow_html=True)

#  Header (nur auf Nicht-Startseite) 
if st.session_state.step != 0:
    st.markdown("<div style='text-align:center;padding:4px 0 24px 0;'><span style='font-size:30px;font-weight:700;color:#fff;letter-spacing:-0.03em;font-family:Inter,sans-serif;'>JobMatch AI</span><br><span style='font-size:12px;color:#555;letter-spacing:0.08em;text-transform:uppercase;font-family:Inter,sans-serif;'>Find jobs that fit your life</span></div>",unsafe_allow_html=True)

if 2<=st.session_state.step<=12 and st.session_state.app_mode=="suche":
    cs=st.session_state.step-1
    st.progress(cs/TOTAL_STEPS_SEEKER)
    st.caption(f"Schritt {cs} von {TOTAL_STEPS_SEEKER}")

if 100<=st.session_state.step<=106 and st.session_state.app_mode=="biete":
    cs=st.session_state.step-99
    st.progress(cs/TOTAL_STEPS_EMPLOYER)
    st.caption(f"Schritt {cs} von {TOTAL_STEPS_EMPLOYER}")

# 
# STEP 0 — Animierte Startseite
# 
if st.session_state.step==0:
    st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
@keyframes glow{0%,100%{opacity:.2}50%{opacity:.7}}
@keyframes fadeUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
.hero{background:linear-gradient(150deg,#06060e,#0c0b1e,#040408);border-radius:22px;padding:52px 24px 44px;text-align:center;position:relative;overflow:hidden;border:1px solid #1a1830;margin-bottom:14px;}
.hero-g1{position:absolute;top:-70px;left:-70px;width:260px;height:260px;background:radial-gradient(circle,rgba(99,102,241,.22) 0%,transparent 65%);border-radius:50%;animation:glow 5s ease-in-out infinite;pointer-events:none;}
.hero-g2{position:absolute;bottom:-50px;right:-50px;width:200px;height:200px;background:radial-gradient(circle,rgba(139,92,246,.16) 0%,transparent 65%);border-radius:50%;animation:glow 7s ease-in-out infinite reverse;pointer-events:none;}
.hero-logo{font-size:52px;font-weight:900;letter-spacing:-.05em;background:linear-gradient(135deg,#fff 0%,#c7d2fe 40%,#a5b4fc 65%,#818cf8 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1;animation:fadeUp .5s both;}
.hero-sub{font-size:13px;color:#3d4c6b;letter-spacing:.15em;text-transform:uppercase;margin-top:6px;animation:fadeUp .5s .1s both;}
.hero-tag{font-size:16px;color:#7080a0;margin-top:16px;line-height:1.6;animation:fadeUp .6s .15s both;}
.hero-stats{display:flex;gap:10px;margin-top:28px;animation:fadeUp .7s .2s both;}
.hero-stat{flex:1;background:rgba(255,255,255,.03);border:1px solid #1e1e35;border-radius:14px;padding:18px 8px;}
.hero-stat-n{font-size:30px;font-weight:900;background:linear-gradient(135deg,#fff,#a5b4fc);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1;}
.hero-stat-l{font-size:10px;color:#475569;text-transform:uppercase;letter-spacing:.08em;margin-top:6px;}
.hero-quote{margin-top:22px;font-size:11px;color:#1e2535;font-style:italic;animation:fadeUp .8s .3s both;}
.chips{display:flex;gap:8px;margin-bottom:14px;}
.chip{flex:1;background:#08080e;border:1px solid #1a1a2e;border-radius:12px;padding:11px 6px;text-align:center;}
.chip-t{font-size:11px;font-weight:700;color:#c7d2fe;margin-bottom:2px;}
.chip-s{font-size:10px;color:#3d4c6b;}
</style>""", unsafe_allow_html=True)

    st.markdown('''
<div class="hero">
  <div class="hero-g1"></div><div class="hero-g2"></div>
  <div style="position:relative;z-index:1;">
    <div class="hero-logo">JobMatch AI</div>
    <div class="hero-sub">Find your next job</div>
    <div class="hero-tag">Swipe. Match. Bewerb dich.<br><span style="color:#94a3b8;">Der Traumjob wartet — wirklich.</span></div>
    <div class="hero-stats">
      <div class="hero-stat"><div class="hero-stat-n">10+</div><div class="hero-stat-l">Jobs heute</div></div>
      <div class="hero-stat"><div class="hero-stat-n">88%</div><div class="hero-stat-l">Avg. Match</div></div>
      <div class="hero-stat"><div class="hero-stat-n">3 Min</div><div class="hero-stat-l">Bis Bewerbung</div></div>
    </div>
    <div class="hero-quote">Ich hab in 10 Minuten meinen Traumjob gefunden. - Max, 24</div>
  </div>
</div>
<div class="chips">
  <div class="chip"><div class="chip-t">Dein Match</div><div class="chip-s">Nur Jobs für dich</div></div>
  <div class="chip"><div class="chip-t">Kein Stress</div><div class="chip-s">Einfach swipen</div></div>
  <div class="chip"><div class="chip-t">Sofort</div><div class="chip-s">Bewerbung raus</div></div>
  <div class="chip"><div class="chip-t">Direkt</div><div class="chip-s">Chat mit Firma</div></div>
</div>
''', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Registrieren / Einloggen", use_container_width=True):
            st.session_state.app_mode="suche"; st.session_state.step=1; st.rerun()
    with col2:
        if st.button("Job einstellen", use_container_width=True):
            st.session_state.app_mode="biete"; st.session_state.step=100; st.rerun()

    st.write("")
    _code_input = st.text_input("Freunde-Code", placeholder="z.B. JM-A3F9B2", label_visibility="visible")
    if _code_input:
        _code = _code_input.strip().upper()
        if _code.startswith("JM-") and len(_code) == 9:
            if _code not in st.session_state.get("referred_friends", []):
                rfs = st.session_state.get("referred_friends", [])
                rfs.append(_code)
                st.session_state.referred_friends = rfs
                st.session_state.pending_referral_bonus = True
                st.success("Code gespeichert — dein Bonus wartet nach der Registrierung.")
            else:
                st.info("Dieser Code wurde bereits eingelöst.")
        elif len(_code_input.strip()) > 3:
            st.warning("Ungültiger Code. Format: JM-XXXXXX")

# 
# STEP 1
# 
elif st.session_state.step==1 and st.session_state.app_mode=="suche":
    H("Willkommen"); hint("Starte mit Login oder Registrierung.")
    col1,col2=st.columns(2)
    with col1:
        if st.button("Einloggen",use_container_width=True): st.session_state.auth_mode="login"; st.rerun()
    with col2:
        if st.button("Registrieren",use_container_width=True): st.session_state.auth_mode="register"; st.rerun()

    if st.session_state.auth_mode=="register":
        st.divider()
        email=st.text_input("E-Mail",placeholder="deinname@email.com")
        password=st.text_input("Passwort",type="password",placeholder="Passwort wählen (mind. 6 Zeichen)")
        if st.button("Konto erstellen",use_container_width=True):
            if email.strip() and password.strip():
                if sb_available():
                    user, err = sb_register(email.strip(), password)
                    if err:
                        st.error(err)
                    else:
                        st.session_state.account.update({"email":email.strip(),"sb_user_id":user.id,"registered":True,"logged_in":True})
                        if st.session_state.get("pending_referral_bonus"):
                            add_xp("referral","Einladungscode eingelöst")
                            st.session_state.pending_referral_bonus = False
                        st.session_state.step=20; st.rerun()
                else:
                    # Fallback ohne Supabase
                    st.session_state.account.update({"email":email.strip(),"registered":True,"logged_in":True})
                    if st.session_state.get("pending_referral_bonus"):
                        add_xp("referral","Einladungscode eingelöst")
                        st.session_state.pending_referral_bonus = False
                    st.session_state.step=20; st.rerun()
            else: st.warning("Bitte E-Mail und Passwort eingeben.")

    elif st.session_state.auth_mode=="login":
        st.divider()
        email=st.text_input("E-Mail",placeholder="deinname@email.com")
        password=st.text_input("Passwort",type="password",placeholder="Passwort eingeben")
        if st.button("Einloggen",key="login_btn",use_container_width=True):
            if email.strip() and password.strip():
                if sb_available():
                    user, err = sb_login(email.strip(), password)
                    if err:
                        st.error(err)
                    else:
                        st.session_state.account.update({"email":email.strip(),"sb_user_id":user.id,"logged_in":True})
                        # Lade gespeichertes Profil aus Datenbank
                        saved = sb_load_profile(user.id)
                        if saved:
                            xp_saved = saved.pop("_xp", 0)
                            streak_saved = saved.pop("_streak", 0)
                            badges_saved = saved.pop("_badges", [])
                            ref_saved = saved.pop("_ref_code", "")
                            st.session_state.profile.update(saved)
                            st.session_state.xp = xp_saved
                            st.session_state.streak_count = streak_saved
                            st.session_state.badges = badges_saved
                            st.session_state.referral_code = ref_saved
                            # Lade Bewerbungen
                            apps = sb_load_applications(user.id)
                            if apps: st.session_state.applications = apps
                            # Lade Nachrichten
                            msgs = sb_load_messages(user.id)
                            if msgs: st.session_state.nachrichten = msgs
                            # Bekannter Nutzer → direkt zu Jobs
                            st.session_state.matches = calculate_matches(st.session_state.profile)
                            st.session_state.current_match_index = 0
                            st.session_state.step = 13; st.rerun()
                        else:
                            # Neues Profil anlegen
                            st.session_state.step=20; st.rerun()
                else:
                    st.session_state.account.update({"email":email.strip(),"logged_in":True})
                    st.session_state.step=20; st.rerun()
            else: st.warning("Bitte E-Mail und Passwort eingeben.")
    st.divider()
    if st.button("Zurück zur Auswahl",use_container_width=True): reset_all()


# 
# STEP 20 — Persona: Wer bist du?
# 
elif st.session_state.step==20 and st.session_state.app_mode=="suche":
    st.markdown("""<style>
@keyframes fadeUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
.pcard{border-radius:16px;padding:20px 18px;margin-bottom:10px;cursor:pointer;position:relative;overflow:hidden;border:1px solid transparent;transition:all .2s;animation:fadeUp .5s both;}
.pcard:hover{transform:translateY(-2px);}
.pcard-emoji{font-size:32px;margin-bottom:8px;}
.pcard-title{font-size:17px;font-weight:800;color:#fff;margin-bottom:4px;font-family:Inter,sans-serif;}
.pcard-desc{font-size:12px;color:#6b7280;line-height:1.5;}
.pcard-tag{display:inline-block;font-size:10px;font-weight:600;padding:3px 10px;border-radius:999px;margin-top:8px;}
</style>""", unsafe_allow_html=True)

    st.markdown("<div style='text-align:center;margin-bottom:6px;'><span style='font-size:28px;font-weight:900;color:#fff;font-family:Inter,sans-serif;letter-spacing:-.02em;'>Wer bist du?</span></div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;font-size:13px;color:#475569;margin-bottom:24px;'>Ein Klick — wir erledigen den Rest.</div>", unsafe_allow_html=True)

    PERSONAS = [
        {
            "emoji": "",
            "label": "Schüler", "sublabel": "ab 15 Jahre",
            "desc": "Ferienjob, Schülerpraktikum oder erster Minijob. Kein Stress, kein Lebenslauf.",
            "tag": "Ferienjob · Praktikum · Minijob",
            "tag_color": "#22d3ee", "bg": "linear-gradient(135deg,#0c1a2e,#0a1520)",
            "border": "#1e3a5a",
            "jobart": "Ferienjob", "arbeitsmodell": "Vor Ort",
            "erfahrung": "Berufseinsteiger", "gehalt_min": 12, "jobtitel": "Ferienjob",
        },
        {
            "emoji": "",
            "label": "Student", "sublabel": "Werkstudent gesucht",
            "desc": "Du studierst und willst Geld verdienen. Flexibel, oft remote, gutes Stundengehalt.",
            "tag": "Werkstudent · Teilzeit · Hybrid",
            "tag_color": "#a78bfa", "bg": "linear-gradient(135deg,#0f0c1e,#0a0816)",
            "border": "#2a1e50",
            "jobart": "Werkstudent", "arbeitsmodell": "Hybrid",
            "erfahrung": "Berufseinsteiger", "gehalt_min": 14, "jobtitel": "Werkstudent",
        },
        {
            "emoji": "",
            "label": "Azubi", "sublabel": "Ausbildung starten oder laufend",
            "desc": "Du suchst einen Ausbildungsplatz oder bist mittendrin. Wir finden die richtigen Betriebe.",
            "tag": "Ausbildung · Berufseinsteiger",
            "tag_color": "#34d399", "bg": "linear-gradient(135deg,#061a12,#041410)",
            "border": "#0d3a22",
            "jobart": "Ausbildung", "arbeitsmodell": "Vor Ort",
            "erfahrung": "Berufseinsteiger", "gehalt_min": 800, "jobtitel": "Ausbildung",
        },
        {
            "emoji": "",
            "label": "Berufseinsteiger", "sublabel": "Erster richtiger Job",
            "desc": "Schule oder Studium abgeschlossen. Zeit für den ersten echten Schritt.",
            "tag": "Vollzeit · Einstieg · Hybrid",
            "tag_color": "#f59e0b", "bg": "linear-gradient(135deg,#1a0f00,#150c00)",
            "border": "#3a2200",
            "jobart": "Vollzeit", "arbeitsmodell": "Hybrid",
            "erfahrung": "Berufseinsteiger", "gehalt_min": 2500, "jobtitel": "",
        },
        {
            "emoji": "",
            "label": "Erfahren", "sublabel": "Nächster Karriereschritt",
            "desc": "Du hast Erfahrung und willst mehr. Mehr Gehalt, mehr Verantwortung, mehr Sinn.",
            "tag": "Vollzeit · Senior · Remote-Option",
            "tag_color": "#6366f1", "bg": "linear-gradient(135deg,#0a0814,#080610)",
            "border": "#1e1a35",
            "jobart": "Vollzeit", "arbeitsmodell": "Hybrid",
            "erfahrung": "1-2 Jahre", "gehalt_min": 3000, "jobtitel": "",
        },
        {
            "emoji": "",
            "label": "Nebenjob", "sublabel": "Dazuverdienen",
            "desc": "Schnell Geld verdienen, flexible Zeiten, kein Stress. Minijob oder Aushilfe — easy.",
            "tag": "Minijob · Aushilfe · Flexibel",
            "tag_color": "#f472b6", "bg": "linear-gradient(135deg,#1a0814,#140610)",
            "border": "#3a1230",
            "jobart": "Minijob", "arbeitsmodell": "Vor Ort",
            "erfahrung": "Berufseinsteiger", "gehalt_min": 13, "jobtitel": "Minijob",
        },
    ]

    def render_pcard(p):
        return (
            f'<div class="pcard" style="background:{p["bg"]};border-color:{p["border"]};'
            f'min-height:180px;display:flex;flex-direction:column;justify-content:space-between;">'
            f'<div>'
            f'<div class="pcard-emoji">{p["emoji"]}</div>'
            f'<div class="pcard-title">{p["label"]}</div>'
            f'<div style="font-size:10px;color:{p["tag_color"]};font-weight:600;margin-bottom:6px;'
            f'text-transform:uppercase;letter-spacing:.06em;">{p["sublabel"]}</div>'
            f'<div class="pcard-desc">{p["desc"]}</div>'
            f'</div>'
            f'<div class="pcard-tag" style="background:{p["tag_color"]}18;color:{p["tag_color"]};'
            f'border:1px solid {p["tag_color"]}30;margin-top:10px;">{p["tag"]}</div>'
            f'</div>'
        )

    col_a, col_b = st.columns(2)
    for i in range(0, len(PERSONAS), 2):
        p_left  = PERSONAS[i]
        p_right = PERSONAS[i+1] if i+1 < len(PERSONAS) else None
        with col_a:
            st.markdown(render_pcard(p_left), unsafe_allow_html=True)
            if st.button(f'Das bin ich {p_left["emoji"]}', key=f'p_{i}', use_container_width=True):
                for k in ["jobart","arbeitsmodell","erfahrung","gehalt_min"]:
                    st.session_state.profile[k] = p_left[k]
                if p_left["jobtitel"]: st.session_state.profile["jobtitel"] = p_left["jobtitel"]
                st.session_state.step = 21; st.rerun()
        with col_b:
            if p_right:
                st.markdown(render_pcard(p_right), unsafe_allow_html=True)
                if st.button(f'Das bin ich {p_right["emoji"]}', key=f'p_{i+1}', use_container_width=True):
                    for k in ["jobart","arbeitsmodell","erfahrung","gehalt_min"]:
                        st.session_state.profile[k] = p_right[k]
                    if p_right["jobtitel"]: st.session_state.profile["jobtitel"] = p_right["jobtitel"]
                    st.session_state.step = 21; st.rerun()

    st.write("")
    if st.button("Zurück", use_container_width=True): reset_all()

# 
# STEP 21 — Match-Typ Reveal
# 
elif st.session_state.step==21 and st.session_state.app_mode=="suche":
    if not st.session_state.get("referral_code"):
        st.session_state.referral_code = gen_referral(st.session_state.profile.get("vorname","User"))
    _title21, _desc21 = get_match_persona(st.session_state.profile)
    _ref21 = st.session_state.referral_code
    _em_map = {"Starter":"","Multitasker":"","Macher":"","Flexmaster":"","Creative":"","Techie":"","Allrounder":""}
    _em21 = _em_map.get(_title21, "")
    st.markdown("""<style>
@keyframes popIn{0%{opacity:0;transform:scale(.6)}70%{transform:scale(1.08)}100%{opacity:1;transform:scale(1)}}
@keyframes fadeUp{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
</style>""", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align:center;padding:28px 0 16px;'>"
        "<div style='font-size:80px;animation:popIn .7s cubic-bezier(.34,1.5,.64,1) both;'>" + _em21 + "</div>"
        "<div style='font-size:13px;color:#475569;letter-spacing:.12em;text-transform:uppercase;margin-top:14px;'>Dein Job-Typ</div>"
        "<div style='font-size:34px;font-weight:900;color:#fff;letter-spacing:-.03em;margin-top:6px;'>Der " + _title21 + "</div>"
        "<div style='font-size:14px;color:#94a3b8;margin-top:12px;line-height:1.65;max-width:310px;margin-left:auto;margin-right:auto;'>" + _desc21 + "</div>"
        "</div>"
        "<div style='background:linear-gradient(135deg,#0f0c1e,#0a0816);border:1px solid #2a1e50;border-radius:16px;padding:18px 20px;margin:8px 0 16px;text-align:center;'>"
        "<div style='font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:.08em;'>Freunde einladen = XP kassieren</div>"
        "<div style='font-size:22px;font-weight:900;color:#a78bfa;margin:8px 0 4px;letter-spacing:.08em;'>" + _ref21 + "</div>"
        "<div style='font-size:12px;color:#374151;'>Pro Freund der sich registriert: +80 XP</div>"
        "</div>",
        unsafe_allow_html=True
    )
    if st.button("Los — Profil ausfüllen", use_container_width=True):
        st.session_state.step = 2; st.rerun()

# 
# STEP 30 — Social Feed / Strava-Style Community
# 
elif st.session_state.step==30 and st.session_state.app_mode=="suche":
    H("Community")
    _xp30 = st.session_state.get("xp",0)
    _streak30 = st.session_state.get("streak_count",0)
    _badges30 = st.session_state.get("badges",[])
    _apps30 = [a for a in st.session_state.applications if a.get("status") in ["Beworben","In Prüfung","Interview","Angebot","Angenommen"]]
    (_,_lvl30,_lcol30), _nxt30 = get_level(_xp30)

    # Eigene Stats
    _cur_min30 = [l[0] for l in LEVELS if _xp30 >= l[0]][-1]
    _prog30 = (_xp30 - _cur_min30) / (_nxt30[0] - _cur_min30) if _nxt30 else 1.0
    _vn30 = st.session_state.profile.get("vorname","Du")
    st.markdown(
        "<div style='background:linear-gradient(135deg,#0f0c1e,#0a0816);border:1px solid #2a1e50;border-radius:16px;padding:18px 20px;margin-bottom:14px;'>"
        "<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;'>"
        "<div><div style='font-size:17px;font-weight:800;color:#fff;'>" + _vn30 + " (Du)</div>"
        "<div style='font-size:12px;margin-top:2px;'><span style='color:" + _lcol30 + ";font-weight:700;'>" + _lvl30 + "</span></div></div>"
        "<div style='text-align:right;'><div style='font-size:24px;font-weight:900;color:#f97316;'> " + str(_streak30) + "</div>"
        "<div style='font-size:10px;color:#374151;'>Tage Streak</div></div></div>"
        "<div style='display:flex;'>"
        "<div style='flex:1;text-align:center;'><div style='font-size:22px;font-weight:900;color:#fff;'>" + str(_xp30) + "</div><div style='font-size:10px;color:#475569;text-transform:uppercase;'>XP</div></div>"
        "<div style='flex:1;text-align:center;border-left:1px solid #1e1e35;'><div style='font-size:22px;font-weight:900;color:#fff;'>" + str(len(_apps30)) + "</div><div style='font-size:10px;color:#475569;text-transform:uppercase;'>Bewerbungen</div></div>"
        "<div style='flex:1;text-align:center;border-left:1px solid #1e1e35;'><div style='font-size:22px;font-weight:900;color:#fff;'>" + str(len(_badges30)) + "</div><div style='font-size:10px;color:#475569;text-transform:uppercase;'>Badges</div></div>"
        "</div></div>",
        unsafe_allow_html=True
    )
    # XP Progress Bar
    if _nxt30:
        st.markdown(
            "<div style='margin-bottom:14px;'>"
            "<div style='display:flex;justify-content:space-between;font-size:11px;color:#475569;margin-bottom:4px;'><span>" + _lvl30 + "</span><span>" + _nxt30[1] + "</span></div>"
            "<div style='height:6px;background:#111;border-radius:999px;overflow:hidden;'>"
            "<div style='height:100%;width:" + str(int(_prog30*100)) + "%;background:linear-gradient(90deg," + _lcol30 + "," + _lcol30 + "99);border-radius:999px;'></div>"
            "</div></div>",
            unsafe_allow_html=True
        )
    # Badges
    st.markdown("<p style='font-size:14px;font-weight:700;color:#fff;margin-bottom:8px;'>Deine Badges</p>", unsafe_allow_html=True)
    if _badges30:
        _bcols30 = st.columns(min(len(_badges30),4))
        for _bi30, _bk30 in enumerate(_badges30[:4]):
            _bem30, _bn30, _bd30 = BADGE_DATA.get(_bk30, ("?",_bk30,""))
            with _bcols30[_bi30]:
                st.markdown("<div style='text-align:center;background:#0a0a16;border:1px solid #1e1e35;border-radius:12px;padding:10px 4px;'><div style='font-size:26px;'>" + _bem30 + "</div><div style='font-size:10px;color:#a78bfa;font-weight:700;margin-top:4px;'>" + _bn30 + "</div><div style='font-size:9px;color:#374151;'>" + _bd30 + "</div></div>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='font-size:12px;color:#374151;'>Noch keine Badges — bewirb dich für deinen ersten!</p>", unsafe_allow_html=True)
    st.divider()
    # Rangliste
    st.markdown("<p style='font-size:14px;font-weight:700;color:#fff;margin-bottom:10px;'> Rangliste</p>", unsafe_allow_html=True)
    _me30 = {"name": _vn30 + " (Du)", "level": _lvl30, "xp": _xp30, "apps": len(_apps30), "streak": _streak30}
    _all30 = sorted([_me30] + DEMO_FRIENDS, key=lambda x: x["xp"], reverse=True)
    _medals30 = ["","",""]
    for _ri30, _fr30 in enumerate(_all30):
        _is_me30 = "(Du)" in _fr30["name"]
        _bg30 = "#0f0c1e" if _is_me30 else "#0a0a0f"
        _brd30 = "#2a1e50" if _is_me30 else "#1e1e2e"
        _med30 = _medals30[_ri30] if _ri30 < 3 else "#" + str(_ri30+1)
        _fw30 = "800" if _is_me30 else "600"
        st.markdown(
            "<div style='background:" + _bg30 + ";border:1px solid " + _brd30 + ";border-radius:12px;padding:12px 16px;margin-bottom:8px;display:flex;align-items:center;justify-content:space-between;'>"
            "<div style='display:flex;align-items:center;gap:12px;'>"
            "<div style='font-size:20px;min-width:28px;text-align:center;'>" + str(_med30) + "</div>"
            "<div><div style='font-size:14px;font-weight:" + _fw30 + ";color:#fff;'>" + _fr30["name"] + "</div>"
            "<div style='font-size:11px;color:#475569;'>" + _fr30["level"] + " ·  " + str(_fr30["streak"]) + " Tage</div></div></div>"
            "<div style='text-align:right;'><div style='font-size:15px;font-weight:800;color:#a78bfa;'>" + str(_fr30["xp"]) + " XP</div>"
            "<div style='font-size:11px;color:#374151;'>" + str(_fr30["apps"]) + " Bewerbungen</div></div>"
            "</div>",
            unsafe_allow_html=True
        )
    st.divider()
    # Activity Feed — aus Supabase laden wenn verfügbar, sonst lokal
    _feed30 = sb_load_feed() if sb_available() else st.session_state.get("social_feed",[])
    st.markdown("<p style='font-size:14px;font-weight:700;color:#fff;margin-bottom:8px;'>Aktivitäten</p>", unsafe_allow_html=True)
    if _feed30:
        for _fe30 in _feed30[:5]:
            st.markdown("<div style='padding:8px 0;border-bottom:1px solid #111;font-size:13px;color:#94a3b8;'><span style='color:#6366f1;font-weight:700;'>+" + str(_fe30["xp"]) + " XP</span> · " + _fe30["text"] + " <span style='color:#374151;font-size:11px;'>(" + _fe30["date"] + ")</span></div>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='font-size:12px;color:#374151;'>Noch keine Aktivitäten — leg los und verdiene XP!</p>", unsafe_allow_html=True)
    st.divider()
    # Referral
    _ref30 = st.session_state.get("referral_code","JM-??????")
    with st.container(border=True):
        st.markdown("<p style='font-size:14px;font-weight:700;color:#fff;margin:0 0 4px 0;'> Freunde einladen</p>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:12px;color:#666;margin:0 0 8px 0;'>+80 XP wenn dein Freund sich registriert</p>", unsafe_allow_html=True)
        st.code(_ref30, language=None)
        _ri_input = st.text_input("Referral-Code eingeben", placeholder="JM-XXXXXX")
        if st.button("Code einlösen", use_container_width=True):
            if _ri_input.strip().upper().startswith("JM-") and _ri_input.strip().upper() not in st.session_state.get("referred_friends",[]):
                _rfs = st.session_state.get("referred_friends",[])
                _rfs.append(_ri_input.strip().upper())
                st.session_state.referred_friends = _rfs
                add_xp("referral", st.session_state.profile.get("vorname","Du") + " hat einen Freund eingeladen")
                st.success("+80 XP! Badge freigeschaltet ")
                st.rerun()
            else:
                st.warning("Ungültiger oder bereits verwendeter Code.")
    st.write("")
    if st.button("Zurück zu Jobs", use_container_width=True): st.session_state.step=13; st.rerun()

# 
# STEPS 2–12
# 
elif st.session_state.step==2 and st.session_state.app_mode=="suche":
    staerke=profil_staerke(st.session_state.profile)
    st.progress(staerke/100); st.caption(f"Profilstärke: {staerke}% — je vollständiger, desto besser deine Matches"); st.write("")
    H("Deine Basisdaten"); hint("Vorname, Nachname und Geburtsdatum.")
    vorname=st.text_input("Vorname",value=st.session_state.profile["vorname"],placeholder="Dein Vorname")
    nachname=st.text_input("Nachname",value=st.session_state.profile["nachname"],placeholder="Dein Nachname")
    max_bd=date.today().replace(year=date.today().year-MINDESTALTER)
    geburtsdatum=st.date_input("Geburtsdatum",value=st.session_state.profile["geburtsdatum"],min_value=date(1950,1,1),max_value=max_bd)
    col1,col2=st.columns(2)
    with col1:
        if st.button("Zurück",key="b2",use_container_width=True): prev_step()
    with col2:
        if st.button("Weiter",key="n2",use_container_width=True):
            valid,msg=validate_profile_identity(vorname,nachname,geburtsdatum)
            if valid: st.session_state.profile.update({"vorname":vorname.strip(),"nachname":nachname.strip(),"geburtsdatum":geburtsdatum}); next_step()
            else: st.warning(msg)

elif st.session_state.step==3 and st.session_state.app_mode=="suche":
    _ps=profil_staerke(st.session_state.profile); st.progress(_ps/100); st.caption(f'Profilstärke: {_ps}%')
    H("Wo suchst du?"); hint("Deine Stadt für die Umkreissuche.")
    stadt=st.text_input("Stadt",value=st.session_state.profile["stadt"],placeholder="z.B. Düsseldorf",label_visibility="collapsed")
    col1,col2=st.columns(2)
    with col1:
        if st.button("Zurück",key="b3",use_container_width=True): prev_step()
    with col2:
        if st.button("Weiter",key="n3",use_container_width=True):
            if stadt.strip(): st.session_state.profile["stadt"]=stadt.strip(); next_step()
            else: st.warning("Bitte gib eine Stadt ein.")

elif st.session_state.step==4 and st.session_state.app_mode=="suche":
    _ps=profil_staerke(st.session_state.profile); st.progress(_ps/100); st.caption(f'Profilstärke: {_ps}%')
    H("Wie weit darf es sein?"); hint("Maximale Entfernung zum Job.")
    umkreis=st.select_slider("Umkreis",options=[5,10,15,20,30,50,75,100],value=st.session_state.profile["umkreis"],format_func=lambda x:f"{x} km")
    col1,col2=st.columns(2)
    with col1:
        if st.button("Zurück",key="b4",use_container_width=True): prev_step()
    with col2:
        if st.button("Weiter",key="n4",use_container_width=True): st.session_state.profile["umkreis"]=umkreis; next_step()

elif st.session_state.step==5 and st.session_state.app_mode=="suche":
    _ps=profil_staerke(st.session_state.profile); st.progress(_ps/100); st.caption(f'Profilstärke: {_ps}%')
    H("Wie möchtest du arbeiten?"); hint("Wähle dein Arbeitsmodell.")
    arbeitsmodell=st.radio("Arbeitsmodell",ARBEITSMODELLE,index=ARBEITSMODELLE.index(st.session_state.profile["arbeitsmodell"]),horizontal=True,label_visibility="collapsed")
    col1,col2=st.columns(2)
    with col1:
        if st.button("Zurück",key="b5",use_container_width=True): prev_step()
    with col2:
        if st.button("Weiter",key="n5",use_container_width=True): st.session_state.profile["arbeitsmodell"]=arbeitsmodell; next_step()

elif st.session_state.step==6 and st.session_state.app_mode=="suche":
    _ps=profil_staerke(st.session_state.profile); st.progress(_ps/100); st.caption(f'Profilstärke: {_ps}%')
    H("Welchen Job suchst du?"); hint("Ein Titel reicht — z.B. Marketing Manager.")
    jobtitel=st.text_input("Jobtitel",value=st.session_state.profile["jobtitel"],placeholder="z.B. Marketing Manager, Sales, Projektkoordinator",label_visibility="collapsed")
    col1,col2=st.columns(2)
    with col1:
        if st.button("Zurück",key="b6",use_container_width=True): prev_step()
    with col2:
        if st.button("Weiter",key="n6",use_container_width=True):
            if jobtitel.strip(): st.session_state.profile["jobtitel"]=jobtitel.strip(); next_step()
            else: st.warning("Bitte gib einen Jobtitel ein.")

elif st.session_state.step==7 and st.session_state.app_mode=="suche":
    _ps=profil_staerke(st.session_state.profile); st.progress(_ps/100); st.caption(f'Profilstärke: {_ps}%')
    H("Welche Jobart?"); hint("Wähle die Art der Stelle aus.")
    jobart=st.selectbox("Jobart",JOBARTEN,index=JOBARTEN.index(st.session_state.profile["jobart"]),label_visibility="collapsed")
    col1,col2=st.columns(2)
    with col1:
        if st.button("Zurück",key="b7",use_container_width=True): prev_step()
    with col2:
        if st.button("Weiter",key="n7",use_container_width=True): st.session_state.profile["jobart"]=jobart; next_step()

elif st.session_state.step==8 and st.session_state.app_mode=="suche":
    _ps=profil_staerke(st.session_state.profile); st.progress(_ps/100); st.caption(f'Profilstärke: {_ps}%')
    H("Was kannst du gut?"); hint("Wähle passende Skills und ergänze eigene.")
    skills=st.multiselect("Skills",SKILL_OPTIONEN,default=st.session_state.profile["skills"],label_visibility="collapsed")
    extra_skills=st.text_input("Eigene Skills (mit Komma trennen)",value=st.session_state.profile["extra_skills_text"],placeholder="z.B. Figma, SAP, Barista")
    col1,col2=st.columns(2)
    with col1:
        if st.button("Zurück",key="b8",use_container_width=True): prev_step()
    with col2:
        if st.button("Weiter",key="n8",use_container_width=True):
            st.session_state.profile["skills"]=skills; st.session_state.profile["extra_skills_text"]=extra_skills; next_step()

elif st.session_state.step==9 and st.session_state.app_mode=="suche":
    _ps=profil_staerke(st.session_state.profile); st.progress(_ps/100); st.caption(f'Profilstärke: {_ps}%')
    H("Welche Sprachen sprichst du?"); hint("Damit passen die Stellen auch sprachlich.")
    sprachen=st.multiselect("Sprachen",SPRACH_OPTIONEN,default=st.session_state.profile["sprachen"],label_visibility="collapsed")
    col1,col2=st.columns(2)
    with col1:
        if st.button("Zurück",key="b9",use_container_width=True): prev_step()
    with col2:
        if st.button("Weiter",key="n9",use_container_width=True): st.session_state.profile["sprachen"]=sprachen; next_step()

elif st.session_state.step==10 and st.session_state.app_mode=="suche":
    _ps=profil_staerke(st.session_state.profile); st.progress(_ps/100); st.caption(f'Profilstärke: {_ps}%')
    H("Wie viel Erfahrung hast du?"); hint("Das verbessert die Match-Qualität.")
    erfahrung=st.radio("Erfahrung",ERFAHRUNGSLEVEL,index=ERFAHRUNGSLEVEL.index(st.session_state.profile["erfahrung"]),label_visibility="collapsed")
    col1,col2=st.columns(2)
    with col1:
        if st.button("Zurück",key="b10",use_container_width=True): prev_step()
    with col2:
        if st.button("Weiter",key="n10",use_container_width=True): st.session_state.profile["erfahrung"]=erfahrung; next_step()

elif st.session_state.step==11 and st.session_state.app_mode=="suche":
    _ps=profil_staerke(st.session_state.profile); st.progress(_ps/100); st.caption(f'Profilstärke: {_ps}%')
    H("Dein Mindestgehalt"); hint("Nur Jobs ab diesem Betrag werden angezeigt.")
    if st.session_state.profile["jobart"] in ["Minijob","Werkstudent","Ferienjob"]:
        opts=[12,13,14,15,16,18,20,25]
        dv=st.session_state.profile["gehalt_min"] if st.session_state.profile["gehalt_min"] in opts else 14
        gehalt_min=st.select_slider("Gehalt",options=opts,value=dv,format_func=lambda x:f"{x} €/Stunde")
    else:
        monthly=[1200,1800,2500,3000,3500,4000,5000,6000,42000]
        dv=st.session_state.profile["gehalt_min"] if st.session_state.profile["gehalt_min"] in monthly else 2500
        gehalt_min=st.select_slider("Gehalt",options=monthly,value=dv,format_func=lambda x:"42.000 €/Jahr" if x==42000 else f"{x} €/Monat")
    startdatum=st.date_input("Frühestes Startdatum",value=st.session_state.profile["startdatum"],min_value=date.today())
    col1,col2=st.columns(2)
    with col1:
        if st.button("Zurück",key="b11",use_container_width=True): prev_step()
    with col2:
        if st.button("Weiter",key="n11",use_container_width=True):
            st.session_state.profile["gehalt_min"]=gehalt_min; st.session_state.profile["startdatum"]=startdatum; next_step()

elif st.session_state.step==12 and st.session_state.app_mode=="suche":
    staerke=profil_staerke(st.session_state.profile)
    st.progress(staerke/100)
    if not st.session_state.profile["lebenslauf_name"]: st.caption(f"Profilstärke: {staerke}% — Mit Lebenslauf: +20% und mehr Matches")
    else: st.caption(f"Profilstärke: {staerke}% — Vollständig!")
    st.write("")
    H("Unterlagen hochladen"); hint("Optional — aber hilfreich für spätere Bewerbungen.")
    lebenslauf=st.file_uploader("Lebenslauf (PDF, Word)",type=["pdf","doc","docx"],accept_multiple_files=False)
    zeugnisse=st.file_uploader("Weitere Unterlagen",type=["pdf","png","jpg","jpeg","doc","docx"],accept_multiple_files=True)
    if lebenslauf: st.session_state.profile["lebenslauf_name"]=lebenslauf.name
    if zeugnisse: st.session_state.profile["zeugnisse_namen"]=[z.name for z in zeugnisse]
    col1,col2=st.columns(2)
    with col1:
        if st.button("Zurück",key="b12",use_container_width=True): prev_step()
    with col2:
        if st.button("Jobs finden",key="n12",use_container_width=True):
            st.session_state.matches=calculate_matches(st.session_state.profile)
            st.session_state.current_match_index=0
            add_xp("profil_komplett", st.session_state.profile.get("vorname","Du") + " hat das Profil abgeschlossen")
            # Profil in Supabase speichern
            uid = st.session_state.account.get("sb_user_id")
            if uid:
                sb_save_profile(uid, st.session_state.profile,
                    xp=st.session_state.get("xp",0),
                    streak=st.session_state.get("streak_count",0),
                    badges=st.session_state.get("badges",[]),
                    ref_code=st.session_state.get("referral_code",""))
                # Social Feed Eintrag
                sb_add_feed(uid, st.session_state.profile.get("vorname","Anonym"),
                    st.session_state.profile.get("vorname","Jemand") + " hat sein Profil abgeschlossen", 50)
            st.session_state.step=13; st.rerun()

# 
# STEP 13 — Swipe
# 
elif st.session_state.step==13 and st.session_state.app_mode=="suche":
    if st.session_state.streak_count>=2:
        st.markdown(f"<div style='background:#111;border:1px solid #2a2a2a;border-radius:8px;padding:10px 14px;margin-bottom:14px;font-size:13px;color:#aaa;'>{st.session_state.streak_count} Tage in Folge aktiv — bleib dran!</div>",unsafe_allow_html=True)

    if st.session_state.show_anschreiben and st.session_state.anschreiben_job:
        job=st.session_state.anschreiben_job
        with st.container(border=True):
            st.markdown(f"<p style='font-size:15px;font-weight:700;color:#fff;margin:0 0 2px 0;'>Anschreiben generieren?</p>",unsafe_allow_html=True)
            st.markdown(f"<p style='font-size:13px;color:#666;margin:0 0 12px 0;'>Für: {job['title']} in {job['city']}</p>",unsafe_allow_html=True)
            col1,col2=st.columns(2)
            with col1:
                if st.button("Ja, generieren",key="gen_yes",use_container_width=True):
                    st.session_state.show_anschreiben=False
                    st.session_state[f"anschreiben_{job['title']}"]=generate_anschreiben(job,st.session_state.profile)
                    st.session_state.step=16; st.rerun()
            with col2:
                if st.button("Nein, danke",key="gen_no",use_container_width=True):
                    st.session_state.show_anschreiben=False; st.rerun()
        st.write("")

    counts=get_application_counts()
    total_seen=st.session_state.swipe_stats["likes"]+st.session_state.swipe_stats["dislikes"]
    liked=st.session_state.swipe_stats["likes"]
    col_s1,col_s2,col_s3=st.columns(3)
    with col_s1: st.metric("Gemerkt",counts["Gemerkt"])
    with col_s2: st.metric("Beworben",counts["Beworben"])
    with col_s3: st.metric("Im Prozess",counts["In Prüfung"]+counts["Interview"]+counts["Angebot"])

    if total_seen>0 and total_seen%5==0 and liked>0:
        st.success(f"Du hast heute {total_seen} Jobs gesehen und {liked} gemerkt. Weiter so!")
    elif total_seen>=3 and liked==0:
        st.info("Noch nichts Passendes? Tipp: Umkreis erweitern oder Jobart anpassen.")

    st.divider()

    col_a,col_b,col_c,col_d=st.columns(4)
    with col_a:
        if st.button("Filter",use_container_width=True): st.session_state.step=3; st.rerun()
    with col_b:
        if st.button("Favoriten",use_container_width=True): st.session_state.step=14; st.rerun()
    with col_c:
        if st.button("Bewerbungen",use_container_width=True): st.session_state.step=15; st.rerun()
    with col_d:
        if st.button(" Feed",use_container_width=True): st.session_state.step=30; st.rerun()
    sel=st.selectbox("Sortierung",["Passendste","Neueste","Dringend"],index=["Passendste","Neueste","Dringend"].index(st.session_state.sort_mode))
    if sel!=st.session_state.sort_mode:
        st.session_state.sort_mode=sel; st.session_state.matches=calculate_matches(st.session_state.profile); st.session_state.current_match_index=0; st.rerun()

    _xp = st.session_state.get("xp",0)
    _streak = st.session_state.get("streak_count",0)
    (_,_lvl,_lcol),_nxt = get_level(_xp)
    _nxt_txt = " · noch " + str(_nxt[0]-_xp) + " XP bis " + _nxt[1] if _nxt else " · Max Level!"
    _sc2 = "#f97316" if _streak>=3 else "#6366f1"
    _si2 = "" if _streak>=3 else ""
    _vn = st.session_state.profile.get('vorname','')
    _bs = " ".join([BADGE_DATA[b][0] for b in st.session_state.get("badges",[])[:4]])
    st.markdown(
        "<div style='background:linear-gradient(135deg,#0f0c1e,#0a0816);border:1px solid #2a1e50;border-radius:14px;"
        "padding:12px 16px;margin-bottom:14px;display:flex;align-items:center;justify-content:space-between;'>"
        "<div><div style='font-size:16px;font-weight:800;color:#fff;'>Hallo, " + _vn + " " + _bs + "</div>"
        "<div style='font-size:11px;color:#475569;margin-top:2px;'>"
        "<span style='color:" + _lcol + ";font-weight:700;'>" + _lvl + "</span> · " + str(_xp) + " XP" + _nxt_txt + "</div></div>"
        "<div style='text-align:right;'><div style='font-size:22px;font-weight:900;color:" + _sc2 + ";'>" + _si2 + " " + str(_streak) + "</div>"
        "<div style='font-size:10px;color:#374151;text-transform:uppercase;letter-spacing:.06em;'>Tage Streak</div></div>"
        "</div>",
        unsafe_allow_html=True
    )

    if st.session_state.consecutive_dislikes>=3:
        st.warning(f"Du hast {st.session_state.consecutive_dislikes} Jobs übersprungen. Filter anpassen?")
        if st.button("Filter anpassen",key="momentum_filter",use_container_width=True):
            st.session_state.consecutive_dislikes=0; st.session_state.step=3; st.rerun()

    if not st.session_state.matches:
        st.warning("Keine Jobs gefunden. Passe deine Filter an.")
        col1,col2=st.columns(2)
        with col1:
            if st.button("Filter anpassen",use_container_width=True): st.session_state.step=3; st.rerun()
        with col2:
            if st.button("Neu starten",use_container_width=True): reset_all()
    else:
        idx=st.session_state.current_match_index
        matches=st.session_state.matches
        if idx<len(matches):
            job=matches[idx]
            sc=job["score"]
            st.caption(f"Job {idx+1} von {len(matches)} — noch {len(matches)-idx-1} weitere")

            # Instagram Story-Style Job Card
            _sc_col = "#10b981" if sc>=80 else "#6366f1" if sc>=60 else "#f59e0b"
            _target = job.get("job_type","")
            _tc_map = {"Werkstudent":"#a78bfa","Minijob":"#f472b6","Ferienjob":"#22d3ee","Ausbildung":"#34d399","Vollzeit":"#f59e0b","Teilzeit":"#fb923c","Praktikum":"#60a5fa"}
            _tc = _tc_map.get(_target,"#6b7280")
            _co = " · " + job["company"] if job.get("company") else ""
            _cd_key = job["title"] + "_" + job["city"]
            _cd = st.session_state.get("countdown_jobs",{}).get(_cd_key)
            _cd_html = ""
            if _cd:
                _days = (_cd - date.today()).days
                if _days <= 2: _cd_html = "<span style='background:#ef444422;color:#ef4444;border:1px solid #ef444444;border-radius:999px;padding:3px 10px;font-size:11px;font-weight:700;'> Noch " + str(_days) + " Tag(e)!</span>"
                elif _days <= 7: _cd_html = "<span style='background:#f59e0b22;color:#f59e0b;border:1px solid #f59e0b44;border-radius:999px;padding:3px 10px;font-size:11px;'> Noch " + str(_days) + " Tage</span>"
            _skills_html = "".join(["<span style='display:inline-block;background:#6366f114;border:1px solid #6366f130;border-radius:999px;padding:3px 9px;font-size:11px;color:#a5b4fc;margin:2px;'>" + s + "</span>" for s in job.get("skills",[])])
            _ben_html = "".join(["<span style='display:inline-block;background:#ffffff08;border:1px solid #222;border-radius:999px;padding:3px 9px;font-size:11px;color:#666;margin:2px;'>" + b + "</span>" for b in job.get("benefits",[])])
            _match_line = "".join(["<span style='font-size:11px;color:#4b5563;display:block;margin:2px 0;'>— " + r + "</span>" for _,r in job.get("reason_parts",[])])
            _card = (
                "<div style='background:linear-gradient(145deg,#0a0a16,#08080f);border:1px solid #1e1e35;border-radius:20px;overflow:hidden;margin-bottom:8px;'>"
                "<div style='padding:14px 18px 10px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #111;'>"
                "<div><div style='font-size:15px;font-weight:800;color:#fff;'>" + job["title"] + "</div>"
                "<div style='font-size:11px;color:#555;margin-top:2px;'>" + job["city"] + ", " + job["country"] + _co + "</div></div>"
                "<span style='background:" + _tc + "22;color:" + _tc + ";border:1px solid " + _tc + "44;border-radius:999px;padding:4px 12px;font-size:11px;font-weight:700;'>" + _target + "</span>"
                "</div>"
                "<div style='padding:10px 18px;border-bottom:1px solid #111;'>"
                "<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;'>"
                "<span style='font-size:11px;color:#555;text-transform:uppercase;letter-spacing:.06em;'>Match</span>"
                "<span style='font-size:20px;font-weight:900;color:" + _sc_col + ";'>" + str(sc) + "%</span></div>"
                "<div style='height:4px;background:#111;border-radius:999px;overflow:hidden;'>"
                "<div style='height:100%;width:" + str(sc) + "%;background:linear-gradient(90deg," + _sc_col + "," + _sc_col + "99);border-radius:999px;'></div></div>"
                "<div style='margin-top:4px;'>" + _match_line + "</div>"
                "</div>"
                "<div style='padding:10px 18px;display:flex;border-bottom:1px solid #111;'>"
                "<div style='flex:1;text-align:center;border-right:1px solid #111;padding:6px 0;'><div style='font-size:16px;font-weight:900;color:#fff;'>ab " + str(job["salary_min"]) + "</div><div style='font-size:9px;color:#555;text-transform:uppercase;'>" + job["salary_unit"] + "</div></div>"
                "<div style='flex:1;text-align:center;border-right:1px solid #111;padding:6px 0;'><div style='font-size:13px;font-weight:700;color:#fff;'>" + job["work_model"] + "</div><div style='font-size:9px;color:#555;text-transform:uppercase;'>Modell</div></div>"
                "<div style='flex:1;text-align:center;padding:6px 0;'><div style='font-size:12px;font-weight:700;color:#fff;'>" + job["experience"] + "</div><div style='font-size:9px;color:#555;text-transform:uppercase;'>Level</div></div>"
                "</div>"
                "<div style='padding:10px 18px;border-bottom:1px solid #111;'><div style='font-size:13px;color:#94a3b8;line-height:1.5;'>" + job["description"][:180] + ("..." if len(job["description"])>180 else "") + "</div></div>"
                "<div style='padding:10px 18px;border-bottom:1px solid #111;'>"
                "<div style='font-size:10px;color:#374151;text-transform:uppercase;letter-spacing:.07em;margin-bottom:5px;'>Skills</div>"
                + (_skills_html if _skills_html else "<span style='color:#2d3748;font-size:12px;'>Keine angegeben</span>") +
                "</div>"
                "<div style='padding:10px 18px 12px;'>"
                "<div style='font-size:10px;color:#374151;text-transform:uppercase;letter-spacing:.07em;margin-bottom:5px;'>Benefits</div>"
                + (_ben_html if _ben_html else "<span style='color:#2d3748;font-size:12px;'>Keine angegeben</span>")
                + ("<div style='margin-top:8px;'>" + _cd_html + "</div>" if _cd_html else "")
                + "</div></div>"
            )
            st.markdown(_card, unsafe_allow_html=True)
            with st.expander(" Bewerbungsfrist setzen"):
                _new_cd = st.date_input("Frist", min_value=date.today(), key="cd_" + str(idx))
                if st.button("Frist speichern", key="cdsave_" + str(idx), use_container_width=True):
                    if "countdown_jobs" not in st.session_state: st.session_state.countdown_jobs = {}
                    st.session_state.countdown_jobs[_cd_key] = _new_cd; st.rerun()

            col1,col2,col3=st.columns(3)
            col1,col2,col3=st.columns(3)
            with col1:
                if st.button("Weiter",key="dislike_btn",use_container_width=True): dislike_current_job()
            with col2:
                if st.button("Merken",key="like_btn",use_container_width=True): like_current_job()
            with col3:
                if st.button("Jetzt bewerben",key="apply_btn",use_container_width=True): apply_current_job(job)

            # Ähnliche Jobs
            similar=find_similar_jobs(job,matches)
            if similar:
                st.markdown("<p style='font-size:12px;color:#3a3a3a;margin-top:14px;margin-bottom:4px;'>Ähnliche Jobs:</p>",unsafe_allow_html=True)
                for sj in similar:
                    st.markdown(f"<p style='font-size:12px;color:#444;margin:2px 0;'>— {sj['title']} ({sj['score']}% Match)</p>",unsafe_allow_html=True)

        else:
            st.success("Du hast alle passenden Jobs gesehen.")
            if liked>0: st.markdown(f"<p style='font-size:14px;color:#888;margin:4px 0 16px 0;'>Heute {total_seen} Jobs gesehen, {liked} gemerkt.</p>",unsafe_allow_html=True)
            if st.session_state.liked_jobs:
                st.markdown(f"<p style='font-size:16px;font-weight:600;color:#fff;margin:0 0 8px 0;'>Gemerkte Jobs ({len(st.session_state.liked_jobs)})</p>",unsafe_allow_html=True)
                for job in st.session_state.liked_jobs:
                    with st.container(border=True):
                        st.markdown(f"<p style='font-weight:600;color:#fff;margin:0;'>{job['title']}</p>",unsafe_allow_html=True)
                        st.caption(f"{job['city']} · {job['job_type']} · {job['score']}% Match")
            else: st.info("Noch keine Jobs gemerkt.")
            col1,col2=st.columns(2)
            with col1:
                if st.button("Nochmal swipen",use_container_width=True):
                    st.session_state.current_match_index=0; st.session_state.liked_jobs=[]; st.session_state.disliked_jobs=[]
                    st.session_state.consecutive_dislikes=0; st.session_state.matches=calculate_matches(st.session_state.profile); st.rerun()
            with col2:
                if st.button("Neu starten",use_container_width=True): reset_all()

# 
# STEP 14 — Favoriten
# 
elif st.session_state.step==14 and st.session_state.app_mode=="suche":
    H("Deine Favoriten"); st.write("")
    if st.session_state.liked_jobs:
        for job in st.session_state.liked_jobs:
            with st.container(border=True):
                st.markdown(f"<p style='font-weight:600;color:#fff;margin:0 0 2px 0;'>{job['title']}</p>",unsafe_allow_html=True)
                st.caption(f"{job['city']} · {job['job_type']} · {job['work_model']}")
                st.progress(job["score"]/100); st.caption(f"{job['score']}% Match")
                if job["benefits"]: st.caption("Benefits: "+", ".join(job["benefits"]))
                if st.button(f"Anschreiben erstellen",key=f"anschr_{job['title']}",use_container_width=True):
                    st.session_state.anschreiben_job=job
                    st.session_state[f"anschreiben_{job['title']}"]=generate_anschreiben(job,st.session_state.profile)
                    st.session_state.step=16; st.rerun()
    else: st.info("Noch keine Jobs gemerkt.")
    st.write("")
    col1,col2=st.columns(2)
    with col1:
        if st.button("Zurück zu Jobs",use_container_width=True): st.session_state.step=13; st.rerun()
    with col2:
        if st.button("Zu Bewerbungen",use_container_width=True): st.session_state.step=15; st.rerun()

# 
# STEP 15 — Bewerbungs-Tracker
# 
elif st.session_state.step==15 and st.session_state.app_mode=="suche":
    H("Meine Bewerbungen")
    counts=get_application_counts()
    col1,col2,col3=st.columns(3)
    with col1: st.metric("Beworben",counts["Beworben"])
    with col2: st.metric("Im Prozess",counts["In Prüfung"]+counts["Interview"]+counts["Angebot"])
    with col3: st.metric("Angenommen",counts["Angenommen"])
    st.divider()

    # Filter-Tabs nach Status-Gruppe
    tab_alle, tab_prozess, tab_offen = st.tabs(["Alle", "Im Prozess", "Offen / Beworben"])

    def render_app_card(i, app, tab_prefix=""):
        with st.container(border=True):
            # Status-Badge oben
            STATUS_COLORS = {
                "Gemerkt":"#444","Beworben":"#555","In Prüfung":"#666",
                "Interview":"#888","Angebot":"#aaa","Angenommen":"#fff","Abgelehnt":"#444"
            }
            sc=STATUS_COLORS.get(app["status"],"#555")
            st.markdown(f"<span style='font-size:11px;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:999px;padding:3px 10px;color:{sc};'>{app['status']}</span>",unsafe_allow_html=True)
            st.write("")
            st.markdown(f"<p style='font-weight:600;color:#fff;margin:0 0 2px 0;font-size:16px;'>{app['title']}</p>",unsafe_allow_html=True)
            st.caption(f"{app['city']} · {app['job_type']} · {app['score']}% Match")
            st.markdown(f"<p style='font-size:13px;color:#666;margin:4px 0 10px 0;'>{app['description'][:90]}...</p>",unsafe_allow_html=True)

            # Chat-Button
            app_key=f"{app['title']}_{app['city']}"
            nachrichten=st.session_state.nachrichten.get(app_key,[])
            unread = len([n for n in nachrichten if n["sender"]=="Arbeitgeber"])
            chat_label = f"Nachricht vom Arbeitgeber ({unread})" if unread > 0 else "Chat mit Arbeitgeber"
            if st.button(chat_label, key=f"chat_{tab_prefix}_{i}", use_container_width=True):
                st.session_state.active_chat = i
                st.session_state.step = 19; st.rerun()

            # Interview-Vorbereitung
            if app["status"] in ["Interview","Angebot"]:
                st.divider()
                st.markdown("<p style='font-size:13px;font-weight:600;color:#fff;margin:0 0 6px 0;'>Interview-Vorbereitung</p>",unsafe_allow_html=True)
                st.markdown("<p style='font-size:12px;color:#666;margin:0 0 8px 0;'>Diese Fragen werden dir wahrscheinlich gestellt:</p>",unsafe_allow_html=True)
                fragen=get_interview_fragen(app["job_type"],app.get("skills",[]),combined_skills(st.session_state.profile))
                for fi,frage in enumerate(fragen,1):
                    st.markdown(f"<p style='font-size:13px;color:#ccc;margin:4px 0;padding:8px 12px;background:#111;border-radius:6px;border-left:2px solid #333;'>{fi}. {frage}</p>",unsafe_allow_html=True)
                salary_unit=app.get("salary_unit","€/Monat")
                gehalts_tipp=GEHALTS_TIPPS.get(salary_unit,"")
                if gehalts_tipp:
                    st.markdown("<p style='font-size:12px;color:#555;margin-top:10px;font-weight:600;'>Gehalts-Verhandlung:</p>",unsafe_allow_html=True)
                    st.markdown(f"<p style='font-size:12px;color:#555;line-height:1.5;'>{gehalts_tipp}</p>",unsafe_allow_html=True)

            # Ablehnung-Analyse
            if app["status"]=="Abgelehnt":
                st.divider()
                st.markdown("<p style='font-size:12px;color:#555;font-weight:600;'>Warum wurde ich abgelehnt?</p>",unsafe_allow_html=True)
                gruende=analyse_ablehnung(app,st.session_state.profile)
                for g in gruende:
                    st.markdown(f"<p style='font-size:12px;color:#555;margin:2px 0;'>— {g}</p>",unsafe_allow_html=True)
                if st.session_state.matches:
                    besser=[m for m in st.session_state.matches if m["score"]>app["score"] and m["title"]!=app["title"]][:2]
                    if besser:
                        st.markdown("<p style='font-size:12px;color:#444;margin-top:6px;'>Diese Jobs passen besser:</p>",unsafe_allow_html=True)
                        for b in besser:
                            st.markdown(f"<p style='font-size:12px;color:#555;margin:2px 0;'>— {b['title']} ({b['score']}% Match)</p>",unsafe_allow_html=True)

    with tab_alle:
        if st.session_state.applications:
            for i,app in enumerate(st.session_state.applications):
                render_app_card(i, app, "alle")
        else:
            st.info("Noch keine Bewerbungen. Merke Jobs beim Swipen.")

    with tab_prozess:
        prozess_apps=[(i,a) for i,a in enumerate(st.session_state.applications) if a["status"] in ["In Prüfung","Interview","Angebot"]]
        if prozess_apps:
            for i,app in prozess_apps:
                render_app_card(i, app, "prozess")
        else:
            st.info("Noch keine Bewerbungen im Prozess.")

    with tab_offen:
        offen_apps=[(i,a) for i,a in enumerate(st.session_state.applications) if a["status"] in ["Gemerkt","Beworben"]]
        if offen_apps:
            for i,app in offen_apps:
                render_app_card(i, app, "offen")
        else:
            st.info("Keine offenen Bewerbungen.")

    st.write("")
    col_a,col_b,col_c=st.columns(3)
    with col_a:
        if st.button("Zurück zu Jobs",use_container_width=True): st.session_state.step=13; st.rerun()
    with col_b:
        if st.button("Favoriten",use_container_width=True): st.session_state.step=14; st.rerun()
    with col_c:
        if st.button("Neu starten",use_container_width=True): reset_all()

# 
# STEP 16 — Anschreiben
# 
elif st.session_state.step==16 and st.session_state.app_mode=="suche":
    job=st.session_state.anschreiben_job
    H("Dein Anschreiben"); hint(f"Generiert für: {job['title']} in {job['city']}")
    key=f"anschreiben_{job['title']}"
    text=st.session_state.get(key,"")
    edited=st.text_area("Anschreiben",value=text,height=380,label_visibility="collapsed")
    st.session_state[key]=edited
    st.caption("Du kannst den Text direkt bearbeiten und dann kopieren.")
    st.write("")
    with st.container(border=True):
        st.markdown("<p style='font-size:15px;font-weight:700;color:#fff;margin:0 0 3px 0;'>Bereit?</p>",unsafe_allow_html=True)
        st.markdown("<p style='font-size:13px;color:#666;margin:0 0 12px 0;'>Sende jetzt deine Bewerbung ab — wird im Tracker gespeichert.</p>",unsafe_allow_html=True)
        if st.button("Jetzt bewerben",key="apply_from_anschr",use_container_width=True):
            already=job_exists_in_applications(job)
            if not already: add_job_to_applications(job,"Beworben")
            else:
                for i,a in enumerate(st.session_state.applications):
                    if a["title"]==job["title"] and a["city"]==job["city"]:
                        update_application_status(i,"Beworben"); break
            st.session_state.step=17; st.rerun()
    st.write("")
    col1,col2=st.columns(2)
    with col1:
        if st.button("Zurück zu Jobs",use_container_width=True): st.session_state.step=13; st.rerun()
    with col2:
        if st.button("Zu Bewerbungen",use_container_width=True): st.session_state.step=15; st.rerun()

# 
# STEP 17 — Bewerbung bestätigt
# 
elif st.session_state.step==17 and st.session_state.app_mode=="suche":
    job=st.session_state.anschreiben_job
    st.write("")
    with st.container(border=True):
        st.markdown("<p style='font-size:22px;font-weight:700;color:#fff;text-align:center;margin:12px 0 6px 0;'>Bewerbung abgeschickt</p>",unsafe_allow_html=True)
        st.markdown(f"<p style='font-size:14px;color:#888;text-align:center;margin-bottom:16px;'>{job['title']} · {job['city']}</p>",unsafe_allow_html=True)
        st.markdown("<p style='font-size:14px;color:#ccc;text-align:center;line-height:1.6;'>Deine Bewerbung ist jetzt im Tracker sichtbar. Sobald du ein Interview bekommst, generiert die App deine Interviewfragen.</p>",unsafe_allow_html=True)
        st.divider()
        st.markdown("<p style='font-size:13px;color:#555;text-align:center;margin:4px 0 10px 0;'>Was als nächstes?</p>",unsafe_allow_html=True)
    st.write("")
    key=f"anschreiben_{job['title']}"
    has_anschreiben=key in st.session_state and st.session_state[key]
    if not has_anschreiben:
        with st.container(border=True):
            st.markdown("<p style='font-size:15px;font-weight:600;color:#fff;margin:0 0 4px 0;'>Anschreiben erstellen</p>",unsafe_allow_html=True)
            st.markdown("<p style='font-size:13px;color:#666;margin:0 0 10px 0;'>Heb dich von anderen Bewerbern ab.</p>",unsafe_allow_html=True)
            if st.button("Anschreiben generieren",key="apply_anschr",use_container_width=True):
                st.session_state[key]=generate_anschreiben(job,st.session_state.profile)
                st.session_state.step=16; st.rerun()
    else:
        with st.container(border=True):
            st.markdown("<p style='font-size:15px;font-weight:600;color:#fff;margin:0 0 4px 0;'>Anschreiben vorhanden</p>",unsafe_allow_html=True)
            if st.button("Anschreiben ansehen",key="apply_anschr_edit",use_container_width=True):
                st.session_state.step=16; st.rerun()
    st.write("")
    col1,col2=st.columns(2)
    with col1:
        if st.button("Weitere Jobs sehen",use_container_width=True):
            st.session_state.show_anschreiben=False; st.session_state.step=13; st.rerun()
    with col2:
        if st.button("Zum Bewerbungs-Tracker",use_container_width=True): st.session_state.step=15; st.rerun()

# 
# STEP 18 — Traumjob-Analyse
# 
elif st.session_state.step==18 and st.session_state.app_mode=="suche":
    H("Traumjob-Analyse"); hint("Finde heraus, was dir noch fehlt.")
    traumjob=st.text_input("Dein Traumjob-Titel",placeholder="z.B. Product Manager, UX Designer, Marketing Director",label_visibility="collapsed")
    if st.button("Analysieren",use_container_width=True) and traumjob.strip():
        user_skills=set(combined_skills(st.session_state.profile))
        jobs=get_all_jobs()
        relevant=[j for j in jobs if any(k in traumjob.lower() for k in j["keywords"]) or any(w in j["title"].lower() for w in traumjob.lower().split())]
        if relevant:
            needed_skills=set()
            for j in relevant: needed_skills.update(j["skills"])
            fehlende=list(needed_skills-user_skills)
            vorhandene=list(needed_skills&user_skills)
            st.session_state.traumjob_analyse={"traumjob":traumjob,"fehlende":fehlende,"vorhandene":vorhandene}
        else:
            st.session_state.traumjob_analyse={"traumjob":traumjob,"fehlende":[],"vorhandene":[]}

    if st.session_state.traumjob_analyse:
        a=st.session_state.traumjob_analyse
        st.write("")
        with st.container(border=True):
            st.markdown(f"<p style='font-size:16px;font-weight:600;color:#fff;margin:0 0 8px 0;'>Analyse: {a['traumjob']}</p>",unsafe_allow_html=True)
            if a["vorhandene"]:
                st.markdown("<p style='font-size:12px;color:#666;margin-bottom:4px;'>Diese Skills hast du bereits:</p>",unsafe_allow_html=True)
                for s in a["vorhandene"]:
                    st.markdown(f"<p style='font-size:13px;color:#888;margin:2px 0;'>+ {s}</p>",unsafe_allow_html=True)
            if a["fehlende"]:
                st.write("")
                st.markdown("<p style='font-size:12px;color:#666;margin-bottom:4px;'>Diese Skills fehlen dir noch:</p>",unsafe_allow_html=True)
                for s in a["fehlende"]:
                    st.markdown(f"<p style='font-size:13px;color:#555;margin:2px 0;'>— {s}</p>",unsafe_allow_html=True)
            if not a["fehlende"] and not a["vorhandene"]:
                st.markdown("<p style='font-size:13px;color:#666;'>Kein passender Job in der Datenbank gefunden. Versuche einen anderen Titel.</p>",unsafe_allow_html=True)
    st.write("")
    if st.button("Zurück zu Jobs",use_container_width=True): st.session_state.step=13; st.rerun()

# 
# STEP 19 — Chat mit Arbeitgeber
# 
elif st.session_state.step==19 and st.session_state.app_mode=="suche":
    idx = st.session_state.active_chat
    if idx is None or idx >= len(st.session_state.applications):
        st.session_state.step=15; st.rerun()
    app = st.session_state.applications[idx]
    app_key = f"{app['title']}_{app['city']}"

    H(f"Chat — {app['title']}")
    hint(f"{app['city']} · {app['status']}")

    # Nachrichten anzeigen
    nachrichten = st.session_state.nachrichten.get(app_key, [])
    if nachrichten:
        for msg in nachrichten:
            is_me = msg["sender"] == "Bewerber"
            align = "right" if is_me else "left"
            bg = "#1a1a1a" if is_me else "#111"
            border = "#333" if is_me else "#2a2a2a"
            name_color = "#888" if is_me else "#666"
            st.markdown(
                f"<div style='text-align:{align};margin-bottom:10px;'>"
                f"<span style='font-size:11px;color:{name_color};'>{msg['sender']} · {msg['time']}</span><br>"
                f"<span style='display:inline-block;background:{bg};border:1px solid {border};border-radius:10px;padding:8px 14px;font-size:14px;color:#ddd;max-width:85%;text-align:left;'>{msg['text']}</span>"
                f"</div>",
                unsafe_allow_html=True
            )
    else:
        st.markdown("<p style='font-size:14px;color:#444;text-align:center;margin:24px 0;'>Noch keine Nachrichten. Schreibe dem Arbeitgeber.</p>", unsafe_allow_html=True)

    st.divider()

    # Neue Nachricht senden
    neue_nachricht = st.text_input("Nachricht schreiben", placeholder="z.B. Ich wollte kurz nachfragen...", label_visibility="collapsed")
    col1, col2 = st.columns([3,1])
    with col1:
        pass
    with col2:
        if st.button("Senden", use_container_width=True):
            if neue_nachricht.strip():
                if app_key not in st.session_state.nachrichten:
                    st.session_state.nachrichten[app_key] = []
                st.session_state.nachrichten[app_key].append({
                    "sender": "Bewerber",
                    "text": neue_nachricht.strip(),
                    "time": str(date.today())
                })
                # Simuliere Arbeitgeber-Antwort auf Follow-up
                import random
                antworten = [
                    "Danke für Ihre Nachricht! Wir melden uns bald mit weiteren Informationen.",
                    "Vielen Dank! Wir befinden uns gerade im Auswahlprozess und werden uns zeitnah bei Ihnen melden.",
                    "Ihre Nachricht ist bei uns eingegangen. Unser Team prüft Ihre Bewerbung — bitte haben Sie noch etwas Geduld.",
                ]
                st.session_state.nachrichten[app_key].append({
                    "sender": "Arbeitgeber",
                    "text": random.choice(antworten),
                    "time": str(date.today())
                })
                st.rerun()

    st.write("")
    if st.button("Zurück zu Bewerbungen", use_container_width=True):
        st.session_state.step=15; st.rerun()

# 
# ARBEITGEBER 100–107
# 
elif st.session_state.step==100 and st.session_state.app_mode=="biete":
    H("Job einstellen"); hint("Grunddaten der Stelle — so erscheint sie auf der Jobkarte.")
    title=st.text_input("Jobtitel",value=st.session_state.job_post_form["title"],placeholder="z.B. Junior Marketing Manager")
    company=st.text_input("Unternehmensname",value=st.session_state.job_post_form.get("company",""),placeholder="z.B. Mustermann GmbH")
    city=st.text_input("Ort",value=st.session_state.job_post_form["city"],placeholder="z.B. Düsseldorf")
    country=st.text_input("Land",value=st.session_state.job_post_form["country"],placeholder="Deutschland")
    col1,col2=st.columns(2)
    with col1:
        if st.button("Zurück",key="eb100",use_container_width=True): reset_all()
    with col2:
        if st.button("Weiter",key="en100",use_container_width=True):
            if title.strip() and city.strip():
                st.session_state.job_post_form.update({"title":title.strip(),"company":company.strip(),"city":city.strip(),"country":country.strip() or "Deutschland"}); next_step()
            else: st.warning("Bitte Jobtitel und Ort eingeben.")

elif st.session_state.step==101 and st.session_state.app_mode=="biete":
    H("Jobart, Modell & Erfahrung"); hint("Diese Felder erscheinen direkt auf der Jobkarte.")
    job_type=st.selectbox("Jobart — wird auf der Karte angezeigt",JOBARTEN,index=JOBARTEN.index(st.session_state.job_post_form["job_type"]))
    work_model=st.radio("Arbeitsmodell — wird auf der Karte angezeigt",["Vor Ort","Hybrid","Remote"],index=["Vor Ort","Hybrid","Remote"].index(st.session_state.job_post_form["work_model"]) if st.session_state.job_post_form["work_model"] in ["Vor Ort","Hybrid","Remote"] else 0,horizontal=True)
    experience=st.radio("Erfahrungslevel — wird auf der Karte angezeigt",ERFAHRUNGSLEVEL,index=ERFAHRUNGSLEVEL.index(st.session_state.job_post_form["experience"]),horizontal=True)
    entry_friendly=st.checkbox("Für Berufseinsteiger geeignet (verbessert Matching für Einsteiger)",value=st.session_state.job_post_form["entry_friendly"])
    col1,col2=st.columns(2)
    with col1:
        if st.button("Zurück",key="eb101",use_container_width=True): prev_step()
    with col2:
        if st.button("Weiter",key="en101",use_container_width=True):
            st.session_state.job_post_form.update({"job_type":job_type,"work_model":work_model,"experience":experience,"entry_friendly":entry_friendly}); next_step()

elif st.session_state.step==102 and st.session_state.app_mode=="biete":
    H("Gehalt"); hint("Wird für den Gehaltsfilter verwendet.")
    if st.session_state.job_post_form["job_type"] in ["Minijob","Werkstudent","Ferienjob"]:
        salary_unit="€/Stunde"
        opts=[12,13,14,15,16,18,20,25]
        salary_min=st.select_slider("Gehalt",options=opts,value=st.session_state.job_post_form["salary_min"] if st.session_state.job_post_form["salary_min"] in opts else 14,format_func=lambda x:f"{x} €/Stunde")
    else:
        salary_unit=st.radio("Einheit",["€/Monat","€/Jahr"],horizontal=True,index=["€/Monat","€/Jahr"].index(st.session_state.job_post_form["salary_unit"]) if st.session_state.job_post_form["salary_unit"] in ["€/Monat","€/Jahr"] else 0)
        if salary_unit=="€/Monat":
            opts=[1200,1800,2500,3000,3500,4000,5000,6000]
            salary_min=st.select_slider("Gehalt",options=opts,value=st.session_state.job_post_form["salary_min"] if st.session_state.job_post_form["salary_min"] in opts else 3000,format_func=lambda x:f"{x} €/Monat")
        else:
            opts=[30000,36000,42000,50000,60000,70000,80000]
            salary_min=st.select_slider("Gehalt",options=opts,value=st.session_state.job_post_form["salary_min"] if st.session_state.job_post_form["salary_min"] in opts else 42000,format_func=lambda x:f"{x} €/Jahr")
    col1,col2=st.columns(2)
    with col1:
        if st.button("Zurück",key="eb102",use_container_width=True): prev_step()
    with col2:
        if st.button("Weiter",key="en102",use_container_width=True):
            st.session_state.job_post_form.update({"salary_min":salary_min,"salary_unit":salary_unit}); next_step()

elif st.session_state.step==103 and st.session_state.app_mode=="biete":
    H("Sprachen")
    hint("Welche Sprachen benoetigt die Stelle? — erscheint auf der Jobkarte unter 'Sprachen'")
    languages=st.multiselect("Benoet. Sprachen",SPRACH_OPTIONEN,default=st.session_state.job_post_form["languages"],placeholder="Sprachen auswählen",label_visibility="collapsed")
    col1,col2=st.columns(2)
    with col1:
        if st.button("Zurück",key="eb103",use_container_width=True): prev_step()
    with col2:
        if st.button("Weiter",key="en103",use_container_width=True):
            st.session_state.job_post_form.update({"languages":languages}); next_step()

elif st.session_state.step==104 and st.session_state.app_mode=="biete":
    H("Skills")
    hint("Welche Skills werden benoetigt? — erscheint auf der Jobkarte unter 'Skills'")
    skills=st.multiselect("Skills",SKILL_OPTIONEN,default=st.session_state.job_post_form["skills"],placeholder="Skills auswählen",label_visibility="collapsed")
    extra_skills_text=st.text_input("Weitere Skills (Komma getrennt)",value=st.session_state.job_post_form["extra_skills_text"],placeholder="z.B. Figma, SAP, Photoshop")
    st.caption("Such-Keywords (intern, für Matching — nicht auf der Karte sichtbar)")
    keywords_text=st.text_input("Keywords",value=st.session_state.job_post_form["keywords_text"],placeholder="z.B. marketing, content, social media")
    col1,col2=st.columns(2)
    with col1:
        if st.button("Zurück",key="eb104",use_container_width=True): prev_step()
    with col2:
        if st.button("Weiter",key="en104",use_container_width=True):
            st.session_state.job_post_form.update({"skills":skills,"extra_skills_text":extra_skills_text,"keywords_text":keywords_text}); next_step()

elif st.session_state.step==105 and st.session_state.app_mode=="biete":
    H("Beschreibung & Voraussetzungen")
    hint("Beide Felder erscheinen direkt auf der Jobkarte.")
    description=st.text_area("Jobbeschreibung — erscheint auf der Karte unter 'Beschreibung'",value=st.session_state.job_post_form["description"],placeholder="Was macht man in diesem Job? Welche Aufgaben fallen an?",height=140)
    requirements_text=st.text_area("Voraussetzungen — erscheint auf der Karte unter 'Voraussetzungen'",value=st.session_state.job_post_form["requirements_text"],placeholder="Welche Qualifikationen, Erfahrungen oder Eigenschaften werden erwartet?",height=120)
    col1,col2=st.columns(2)
    with col1:
        if st.button("Zurück",key="eb105",use_container_width=True): prev_step()
    with col2:
        if st.button("Weiter",key="en105",use_container_width=True):
            st.session_state.job_post_form.update({"description":description,"requirements_text":requirements_text}); next_step()

elif st.session_state.step==106 and st.session_state.app_mode=="biete":
    H("Benefits")
    hint("Erscheinen auf der Jobkarte unter 'Benefits' — je mehr, desto attraktiver die Stelle.")
    benefits=st.multiselect("Benefits",BENEFIT_OPTIONEN,default=st.session_state.job_post_form["benefits"],placeholder="Benefits auswählen",label_visibility="collapsed")
    extra_benefits_text=st.text_input("Weitere Benefits (Komma getrennt)",value=st.session_state.job_post_form["extra_benefits_text"],placeholder="z.B. Fitnessstudio, Essenszuschuss, Firmenwagen")
    st.caption("Dringlichkeit (intern — beeinflusst Sortierung, nicht sichtbar auf der Karte)")
    urgency=st.slider("Dringlichkeit",min_value=1,max_value=10,value=st.session_state.job_post_form["urgency"])
    col1,col2=st.columns(2)
    with col1:
        if st.button("Zurück",key="eb106",use_container_width=True): prev_step()
    with col2:
        if st.button("Job speichern",key="es106",use_container_width=True):
            st.session_state.job_post_form.update({"benefits":benefits,"extra_benefits_text":extra_benefits_text,"urgency":urgency}); save_job_post()

# 
# ARBEITGEBER STEP 107 — Dashboard
# 
elif st.session_state.step==107 and st.session_state.app_mode=="biete":

    # Hilfsfunktion: Bewerbungen für einen Job zählen
    def get_bewerber_für_job(job_title):
        return [a for a in st.session_state.applications if a["title"]==job_title]

    def delete_posted_job(idx):
        if 0 <= idx < len(st.session_state.posted_jobs):
            st.session_state.posted_jobs.pop(idx)
            st.rerun()

    def set_job_status(idx, status):
        if 0 <= idx < len(st.session_state.posted_jobs):
            st.session_state.posted_jobs[idx]["job_status"] = status
            st.rerun()

    def update_bewerber_status(job_title, bewerber_idx, new_status):
        count = 0
        for a in st.session_state.applications:
            if a["title"] == job_title:
                if count == bewerber_idx:
                    a["status"] = new_status
                    break
                count += 1

    # Sicherstellen dass alle posted_jobs einen job_status haben
    for j in st.session_state.posted_jobs:
        if "job_status" not in j:
            j["job_status"] = "Aktiv"

    JOB_STATUS_OPTIONEN = ["Aktiv", "Stelle besetzt", "Kein Bedarf mehr", "Pausiert", "Archiviert"]
    BEWERBER_STATUS_OPTIONEN = ["Beworben", "In Prüfung", "Interview", "Angebot", "Angenommen", "Abgelehnt"]

    # Header mit Metriken
    H("Arbeitgeber Dashboard")
    st.write("")

    total_jobs = len(st.session_state.posted_jobs)
    aktive_jobs = len([j for j in st.session_state.posted_jobs if j.get("job_status","Aktiv")=="Aktiv"])
    total_bewerber = sum(len(get_bewerber_für_job(j["title"])) for j in st.session_state.posted_jobs)
    offene_bewerber = len([a for a in st.session_state.applications if a["status"] in ["Beworben","In Prüfung"]])

    col1,col2,col3,col4 = st.columns(4)
    with col1: st.metric("Jobs online", total_jobs)
    with col2: st.metric("Aktiv", aktive_jobs)
    with col3: st.metric("Bewerbungen", total_bewerber)
    with col4: st.metric("Offen", offene_bewerber)

    st.divider()

    # Tabs
    tab_jobs, tab_bewerber = st.tabs(["Meine Jobs", "Alle Bewerbungen"])

    #  Tab 1: Meine Jobs 
    with tab_jobs:
        if not st.session_state.posted_jobs:
            st.info("Noch keine Jobs eingestellt.")
        else:
            for i, job in enumerate(st.session_state.posted_jobs):
                bewerber = get_bewerber_für_job(job["title"])
                js = job.get("job_status","Aktiv")
                js_color = {"Aktiv":"#fff","Stelle besetzt":"#888","Kein Bedarf mehr":"#555","Pausiert":"#666","Archiviert":"#444"}.get(js,"#888")

                with st.container(border=True):
                    # Titel + Status-Badge
                    col_t, col_s = st.columns([3,1])
                    with col_t:
                        st.markdown(f"<p style='font-weight:700;color:#fff;font-size:16px;margin:0 0 2px 0;'>{job['title']}</p>",unsafe_allow_html=True)
                        st.caption(f"{job['city']} · {job['job_type']} · {job['work_model']} · ab {job['salary_min']} {job['salary_unit']}")
                    with col_s:
                        st.markdown(f"<div style='text-align:right;padding-top:4px;'><span style='font-size:11px;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:999px;padding:3px 10px;color:{js_color};'>{js}</span></div>",unsafe_allow_html=True)

                    # Bewerbungs-Zähler
                    st.markdown(f"<p style='font-size:13px;color:#666;margin:6px 0 10px 0;'>{len(bewerber)} Bewerbung(en) eingegangen</p>",unsafe_allow_html=True)

                    # Skills & Benefits kompakt
                    if job.get("skills"):
                        st.caption("Skills: " + ", ".join(job["skills"][:4]) + ("..." if len(job["skills"])>4 else ""))
                    if job.get("benefits"):
                        st.caption("Benefits: " + ", ".join(job["benefits"][:3]) + ("..." if len(job["benefits"])>3 else ""))

                    st.divider()

                    # Status ändern
                    new_js = st.selectbox(
                        "Status der Stelle",
                        JOB_STATUS_OPTIONEN,
                        index=JOB_STATUS_OPTIONEN.index(js),
                        key=f"js_{i}",
                        label_visibility="collapsed"
                    )
                    if new_js != js:
                        st.session_state.posted_jobs[i]["job_status"] = new_js
                        st.rerun()

                    # Aktionen
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if st.button("Stelle besetzt", key=f"besetzt_{i}", use_container_width=True):
                            set_job_status(i, "Stelle besetzt")
                    with col_b:
                        if st.button("Kein Bedarf", key=f"keinbedarf_{i}", use_container_width=True):
                            set_job_status(i, "Kein Bedarf mehr")
                    with col_c:
                        if st.button("Loeschen", key=f"del_{i}", use_container_width=True):
                            delete_posted_job(i)

    #  Tab 2: Alle Bewerbungen 
    with tab_bewerber:
        # Nur Bewerbungen auf eigene Jobs anzeigen
        eigene_titel = [j["title"] for j in st.session_state.posted_jobs]
        eigene_bewerbungen = [(idx, a) for idx, a in enumerate(st.session_state.applications) if a["title"] in eigene_titel]

        if not eigene_bewerbungen:
            st.info("Noch keine Bewerbungen auf deine Jobs eingegangen.")
        else:
            # Gruppiert nach Job
            for job in st.session_state.posted_jobs:
                job_bewerber = [(idx,a) for idx,a in eigene_bewerbungen if a["title"]==job["title"]]
                if not job_bewerber: continue

                st.markdown(f"<p style='font-size:15px;font-weight:700;color:#fff;margin:12px 0 8px 0;'>{job['title']} ({len(job_bewerber)} Bewerbung(en))</p>",unsafe_allow_html=True)

                for bidx, (app_idx, app) in enumerate(job_bewerber):
                    STATUS_COLORS = {
                        "Beworben":"#666","In Prüfung":"#888","Interview":"#aaa",
                        "Angebot":"#ccc","Angenommen":"#fff","Abgelehnt":"#444","Gemerkt":"#555"
                    }
                    sc = STATUS_COLORS.get(app["status"],"#666")

                    with st.container(border=True):
                        col_info, col_stat = st.columns([3,1])
                        with col_info:
                            st.markdown(f"<p style='font-weight:600;color:#fff;margin:0 0 2px 0;'>Bewerber #{bidx+1}</p>",unsafe_allow_html=True)
                            st.caption(f"{app['city']} · {app['job_type']} · {app['score']}% Match")
                            st.markdown(f"<p style='font-size:12px;color:#666;margin:4px 0 0 0;'>{app['description'][:80]}...</p>",unsafe_allow_html=True)
                        with col_stat:
                            st.markdown(f"<div style='text-align:right;padding-top:4px;'><span style='font-size:11px;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:999px;padding:3px 10px;color:{sc};'>{app['status']}</span></div>",unsafe_allow_html=True)

                        # Arbeitgeber setzt den Status
                        new_bstatus = st.selectbox(
                            "Bewerberstatus setzen",
                            BEWERBER_STATUS_OPTIONEN,
                            index=BEWERBER_STATUS_OPTIONEN.index(app["status"]) if app["status"] in BEWERBER_STATUS_OPTIONEN else 0,
                            key=f"bstat_{app_idx}_{bidx}",
                            label_visibility="collapsed"
                        )
                        if new_bstatus != app["status"]:
                            st.session_state.applications[app_idx]["status"] = new_bstatus
                            # Auto-Nachricht an Bewerber
                            app_key = f"{app['title']}_{app['city']}"
                            if app_key not in st.session_state.nachrichten:
                                st.session_state.nachrichten[app_key] = []
                            STATUS_MSG = {
                                "In Prüfung": "Ihre Bewerbung wird aktuell von unserem Team geprüft.",
                                "Interview": "Wir möchten Sie gerne zu einem Interview einladen! Bitte melden Sie sich für einen Terminvorschlag.",
                                "Angebot": "Wir freuen uns, Ihnen ein Stellenangebot unterbreiten zu können. Details folgen in Kürze.",
                                "Angenommen": "Herzlichen Glückwunsch! Ihre Bewerbung wurde angenommen. Willkommen im Team!",
                                "Abgelehnt": "Vielen Dank für Ihre Bewerbung. Leider müssen wir Ihnen mitteilen, dass wir uns für andere Kandidaten entschieden haben.",
                            }
                            if new_bstatus in STATUS_MSG:
                                st.session_state.nachrichten[app_key].append({
                                    "sender":"Arbeitgeber",
                                    "text": STATUS_MSG[new_bstatus],
                                    "time": str(date.today())
                                })
                            st.rerun()

                        # Schnell-Aktionen
                        col_x, col_y, col_z = st.columns(3)
                        with col_x:
                            if st.button("Einladen", key=f"inv_{app_idx}_{bidx}", use_container_width=True):
                                st.session_state.applications[app_idx]["status"] = "Interview"
                                app_key = f"{app['title']}_{app['city']}"
                                if app_key not in st.session_state.nachrichten: st.session_state.nachrichten[app_key]=[]
                                st.session_state.nachrichten[app_key].append({"sender":"Arbeitgeber","text":"Wir möchten Sie gerne zu einem Vorstellungsgespräch einladen. Bitte melden Sie sich für einen Terminvorschlag.","time":str(date.today())})
                                st.rerun()
                        with col_y:
                            if st.button("Absagen", key=f"rej_{app_idx}_{bidx}", use_container_width=True):
                                st.session_state.applications[app_idx]["status"] = "Abgelehnt"
                                app_key = f"{app['title']}_{app['city']}"
                                if app_key not in st.session_state.nachrichten: st.session_state.nachrichten[app_key]=[]
                                st.session_state.nachrichten[app_key].append({"sender":"Arbeitgeber","text":"Vielen Dank für Ihr Interesse. Nach sorgfältiger Prüfung haben wir uns für andere Kandidaten entschieden. Wir wünschen Ihnen viel Erfolg.","time":str(date.today())})
                                st.rerun()
                        with col_z:
                            if st.button("Angebot", key=f"off_{app_idx}_{bidx}", use_container_width=True):
                                st.session_state.applications[app_idx]["status"] = "Angebot"
                                app_key = f"{app['title']}_{app['city']}"
                                if app_key not in st.session_state.nachrichten: st.session_state.nachrichten[app_key]=[]
                                st.session_state.nachrichten[app_key].append({"sender":"Arbeitgeber","text":"Wir freuen uns sehr, Ihnen ein Stellenangebot zu unterbreiten! Bitte melden Sie sich, damit wir die Details besprechen können.","time":str(date.today())})
                                st.rerun()

    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Neuen Job einstellen", use_container_width=True): reset_employer_flow_only()
    with col2:
        if st.button("Zur Startseite", use_container_width=True): reset_all()

else:
    st.warning("Unbekannter Zustand."); reset_all()
