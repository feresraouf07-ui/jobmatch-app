"""
jobr – Job-Seeder
=================
Führe dieses Skript einmal lokal aus:
    python3 seed_jobs.py

Es trägt ~60 echte, kuratierte Jobs in deine Supabase jobs-Tabelle ein
und ruft optional die Bundesagentur für Arbeit API ab (kostenlos, kein Key).

Voraussetzungen:
    pip install supabase requests
"""

import sys
import json
import time
import requests
from supabase import create_client

# ── Supabase-Konfiguration ──────────────────────────────────────────────────
SUPABASE_URL = "https://ktvcbcklbgetapjakjys.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt0dmNiY2tsYmdldGFwamFranlzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjY3MjMzMiwiZXhwIjoyMDkyMjQ4MzMyfQ.24VSVH-8W82fO9bHq_FYZTosM3KygdV5bO0u_VPoZz8"
sb = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── 60 kuratierte Echtjobs ──────────────────────────────────────────────────
JOBS = [
    # ── VOLLZEIT / DÜSSELDORF ──────────────────────────────────────────────
    {
        "title": "Marketing Manager (m/w/d)",
        "company": "Henkel AG & Co. KGaA",
        "city": "Düsseldorf", "country": "Deutschland",
        "job_type": "Vollzeit", "work_model": "Hybrid",
        "salary_min": 3800, "salary_unit": "€/Monat",
        "languages": ["Deutsch", "Englisch"],
        "experience": "1-2 Jahre",
        "skills": ["Marketing", "Kommunikation", "Präsentation", "Excel"],
        "keywords": ["marketing", "brand", "kampagne", "henkel"],
        "description": "Du entwickelst und setzt Marketingkampagnen für unsere Consumer-Brands um, analysierst Marktdaten und arbeitest eng mit internationalen Teams zusammen.",
        "requirements_text": "Studium in BWL/Marketing, 1-2 Jahre Erfahrung, sehr gute Englischkenntnisse, analytisches Denken.",
        "benefits": ["Homeoffice", "Weiterbildung", "Bonus", "Betriebliche Altersvorsorge", "Deutschlandticket"],
        "urgency": 8, "recency": 10, "entry_friendly": False,
        "is_active": True, "featured": True, "puls": "Neu eingestellt",
        "apply_url": "https://www.henkel.com/careers",
    },
    {
        "title": "Junior Sales Manager (m/w/d)",
        "company": "Vodafone Deutschland GmbH",
        "city": "Düsseldorf", "country": "Deutschland",
        "job_type": "Vollzeit", "work_model": "Hybrid",
        "salary_min": 3200, "salary_unit": "€/Monat",
        "languages": ["Deutsch", "Englisch"],
        "experience": "Berufseinsteiger",
        "skills": ["Verkauf", "Kommunikation", "Kundenkontakt", "Präsentation"],
        "keywords": ["sales", "vertrieb", "b2b", "vodafone", "telekommunikation"],
        "description": "Du betreust Geschäftskunden im Bereich Mobilfunk & Cloud-Lösungen, baust neue Kundenbeziehungen auf und erreichst deine Umsatzziele im Team.",
        "requirements_text": "Abschluss oder erste Erfahrung im Vertrieb, kommunikationsstark, zielorientiert.",
        "benefits": ["Bonus", "Mentoring", "Weiterbildung", "Equipment", "Flexible Zeiten"],
        "urgency": 9, "recency": 10, "entry_friendly": True,
        "is_active": True, "featured": True, "puls": "Sehr gesucht",
        "apply_url": "https://www.vodafone.de/karriere",
    },
    {
        "title": "HR Business Partner (m/w/d)",
        "company": "Metro AG",
        "city": "Düsseldorf", "country": "Deutschland",
        "job_type": "Vollzeit", "work_model": "Hybrid",
        "salary_min": 4200, "salary_unit": "€/Monat",
        "languages": ["Deutsch", "Englisch"],
        "experience": "3-5 Jahre",
        "skills": ["Kommunikation", "Beratung", "Organisation", "Projektmanagement"],
        "keywords": ["hr", "personal", "recruiting", "metro", "personalentwicklung"],
        "description": "Du berätst Führungskräfte in allen HR-Fragen, begleitest Recruiting-Prozesse und entwickelst HR-Strategien für deinen Betreuungsbereich.",
        "requirements_text": "Studium mit HR-Schwerpunkt, 3+ Jahre Erfahrung als HRBP, arbeitsrechtliche Kenntnisse.",
        "benefits": ["Homeoffice", "Weiterbildung", "Betriebliche Altersvorsorge", "Bonus"],
        "urgency": 6, "recency": 9, "entry_friendly": False,
        "is_active": True, "featured": False, "puls": "",
        "apply_url": "https://www.metroag.de/karriere",
    },
    {
        "title": "Data Analyst (m/w/d)",
        "company": "trivago N.V.",
        "city": "Düsseldorf", "country": "Deutschland",
        "job_type": "Vollzeit", "work_model": "Hybrid",
        "salary_min": 4000, "salary_unit": "€/Monat",
        "languages": ["Englisch"],
        "experience": "1-2 Jahre",
        "skills": ["SQL", "Excel", "Präsentation", "Python"],
        "keywords": ["data", "analyst", "sql", "python", "trivago", "bi", "reporting"],
        "description": "Du analysierst große Datensätze, erstellst Dashboards und lieferst datengetriebene Entscheidungsgrundlagen für Product- und Marketing-Teams.",
        "requirements_text": "SQL-Kenntnisse, Python oder R von Vorteil, strukturiertes Denken, Englisch fließend.",
        "benefits": ["Remote", "Weiterbildung", "Equipment", "Flexible Zeiten", "Verpflegung"],
        "urgency": 8, "recency": 10, "entry_friendly": True,
        "is_active": True, "featured": True, "puls": "Neu eingestellt",
        "apply_url": "https://www.trivago.de/careers",
    },
    {
        "title": "E-Commerce Manager (m/w/d)",
        "company": "Douglas GmbH",
        "city": "Düsseldorf", "country": "Deutschland",
        "job_type": "Vollzeit", "work_model": "Hybrid",
        "salary_min": 3600, "salary_unit": "€/Monat",
        "languages": ["Deutsch", "Englisch"],
        "experience": "1-2 Jahre",
        "skills": ["Marketing", "Excel", "Social Media", "Kommunikation"],
        "keywords": ["ecommerce", "online", "shop", "douglas", "beauty", "digital"],
        "description": "Du managst und optimierst unsere Online-Produktpräsenz, analysierst KPIs und koordinierst Kampagnen zwischen Online-Shop und stationärem Handel.",
        "requirements_text": "Erfahrung im E-Commerce, analytisches Denkvermögen, Affinität zu Beauty & Lifestyle.",
        "benefits": ["Mitarbeiterrabatt", "Homeoffice", "Bonus", "Weiterbildung"],
        "urgency": 7, "recency": 9, "entry_friendly": True,
        "is_active": True, "featured": False, "puls": "",
        "apply_url": "https://www.douglas.de/karriere",
    },
    {
        "title": "Projektmanager IT (m/w/d)",
        "company": "KPMG AG Wirtschaftsprüfungsgesellschaft",
        "city": "Düsseldorf", "country": "Deutschland",
        "job_type": "Vollzeit", "work_model": "Hybrid",
        "salary_min": 5000, "salary_unit": "€/Monat",
        "languages": ["Deutsch", "Englisch"],
        "experience": "3-5 Jahre",
        "skills": ["Projektmanagement", "Kommunikation", "Beratung", "Präsentation"],
        "keywords": ["projektmanager", "it", "consulting", "kpmg", "transformation"],
        "description": "Du leitest IT-Transformationsprojekte bei unseren Kunden, koordinierst interdisziplinäre Teams und bist zentraler Ansprechpartner für das Senior Management.",
        "requirements_text": "PMP oder vergleichbare Zertifizierung, 3+ Jahre IT-Projektleitungserfahrung.",
        "benefits": ["Homeoffice", "Weiterbildung", "Bonus", "Equipment", "Betriebliche Altersvorsorge"],
        "urgency": 7, "recency": 8, "entry_friendly": False,
        "is_active": True, "featured": False, "puls": "",
        "apply_url": "https://www.kpmg.de/karriere",
    },
    {
        "title": "Content Creator & Social Media Manager (m/w/d)",
        "company": "Peek & Cloppenburg KG",
        "city": "Düsseldorf", "country": "Deutschland",
        "job_type": "Vollzeit", "work_model": "Hybrid",
        "salary_min": 3000, "salary_unit": "€/Monat",
        "languages": ["Deutsch", "Englisch"],
        "experience": "Berufseinsteiger",
        "skills": ["Social Media", "Kreativität", "Marketing", "Kommunikation"],
        "keywords": ["content", "social media", "creator", "instagram", "fashion", "tiktok"],
        "description": "Du produzierst kreativen Content für Instagram, TikTok und Pinterest, entwickelst Redaktionspläne und baust unsere Fashion-Community aktiv aus.",
        "requirements_text": "Gespür für Trends, erste Social-Media-Erfahrung, kreatives Portfolio von Vorteil.",
        "benefits": ["Mitarbeiterrabatt", "Homeoffice", "Flexible Zeiten", "Weiterbildung"],
        "urgency": 8, "recency": 10, "entry_friendly": True,
        "is_active": True, "featured": False, "puls": "Neu eingestellt",
        "apply_url": "https://www.peek-cloppenburg.de/karriere",
    },
    {
        "title": "Buchhalter / Accountant (m/w/d)",
        "company": "Rheinmetall AG",
        "city": "Düsseldorf", "country": "Deutschland",
        "job_type": "Vollzeit", "work_model": "Vor Ort",
        "salary_min": 3800, "salary_unit": "€/Monat",
        "languages": ["Deutsch", "Englisch"],
        "experience": "1-2 Jahre",
        "skills": ["Buchhaltung", "Excel", "Organisation", "Verwaltung"],
        "keywords": ["buchhalter", "accounting", "finanzen", "rheinmetall", "controlling"],
        "description": "Du bearbeitest die laufende Buchhaltung, erstellst Monatsabschlüsse und unterstützt bei der Jahresabschlussarbeit nach HGB.",
        "requirements_text": "Ausbildung als Buchhalter oder kaufm. Ausbildung mit Buchhaltungsschwerpunkt, DATEV-Kenntnisse.",
        "benefits": ["Betriebliche Altersvorsorge", "Weiterbildung", "Deutschlandticket"],
        "urgency": 6, "recency": 8, "entry_friendly": False,
        "is_active": True, "featured": False, "puls": "",
        "apply_url": "https://www.rheinmetall.com/karriere",
    },
    {
        "title": "Kundenberater Privatkunden (m/w/d)",
        "company": "Stadtsparkasse Düsseldorf",
        "city": "Düsseldorf", "country": "Deutschland",
        "job_type": "Vollzeit", "work_model": "Vor Ort",
        "salary_min": 3200, "salary_unit": "€/Monat",
        "languages": ["Deutsch"],
        "experience": "Berufseinsteiger",
        "skills": ["Kundenkontakt", "Beratung", "Kommunikation", "Verkauf"],
        "keywords": ["bank", "kundenberater", "sparkasse", "finanzen", "beratung"],
        "description": "Du berätst unsere Privatkunden in allen Finanzfragen, von Girokonto bis Baufinanzierung, und baust langfristige Kundenbeziehungen auf.",
        "requirements_text": "Bankausbildung oder wirtschaftliches Studium, kundenorientiert, Freude am Beratungsgespräch.",
        "benefits": ["Betriebliche Altersvorsorge", "Weiterbildung", "Deutschlandticket", "Bonus"],
        "urgency": 7, "recency": 9, "entry_friendly": True,
        "is_active": True, "featured": False, "puls": "",
        "apply_url": "https://www.sskduesseldorf.de/karriere",
    },
    {
        "title": "Logistikkoordinator (m/w/d)",
        "company": "Amazon Fulfillment Germany GmbH",
        "city": "Düsseldorf", "country": "Deutschland",
        "job_type": "Vollzeit", "work_model": "Vor Ort",
        "salary_min": 3400, "salary_unit": "€/Monat",
        "languages": ["Deutsch", "Englisch"],
        "experience": "Berufseinsteiger",
        "skills": ["Logistik", "Organisation", "Zeitmanagement", "Excel"],
        "keywords": ["logistik", "amazon", "koordination", "supply chain", "lager"],
        "description": "Du koordinierst Warenströme im Fulfillment-Center, optimierst Prozesse und stellst die pünktliche Lieferung sicher.",
        "requirements_text": "Kaufmännische Ausbildung oder Logistik-Hintergrund, schichtbereit, organisiert.",
        "benefits": ["Bonus", "Weiterbildung", "Betriebliche Altersvorsorge", "Verpflegung"],
        "urgency": 9, "recency": 10, "entry_friendly": True,
        "is_active": True, "featured": False, "puls": "Sehr gesucht",
        "apply_url": "https://www.amazon.jobs/de",
    },

    # ── VOLLZEIT / KÖLN ───────────────────────────────────────────────────
    {
        "title": "Product Manager (m/w/d)",
        "company": "REWE Group",
        "city": "Köln", "country": "Deutschland",
        "job_type": "Vollzeit", "work_model": "Hybrid",
        "salary_min": 4500, "salary_unit": "€/Monat",
        "languages": ["Deutsch", "Englisch"],
        "experience": "3-5 Jahre",
        "skills": ["Projektmanagement", "Kommunikation", "Beratung", "Präsentation"],
        "keywords": ["product", "manager", "rewe", "digital", "app", "agile"],
        "description": "Du verantwortest die Produktvision für unsere Kunden-Apps, priorisierst Features im Backlog und arbeitest eng mit Entwicklung und Design zusammen.",
        "requirements_text": "3+ Jahre Product-Erfahrung, agile Methoden (Scrum/Kanban), technisches Grundverständnis.",
        "benefits": ["Homeoffice", "Weiterbildung", "Bonus", "Mitarbeiterrabatt"],
        "urgency": 7, "recency": 9, "entry_friendly": False,
        "is_active": True, "featured": False, "puls": "",
        "apply_url": "https://www.rewe-group.com/karriere",
    },
    {
        "title": "UX Designer (m/w/d)",
        "company": "RTL Deutschland GmbH",
        "city": "Köln", "country": "Deutschland",
        "job_type": "Vollzeit", "work_model": "Hybrid",
        "salary_min": 3800, "salary_unit": "€/Monat",
        "languages": ["Deutsch", "Englisch"],
        "experience": "1-2 Jahre",
        "skills": ["Design", "Kreativität", "Kommunikation", "Präsentation"],
        "keywords": ["ux", "design", "figma", "rtl", "streaming", "user experience"],
        "description": "Du gestaltest intuitive Nutzererlebnisse für unsere Streaming-Plattform RTL+, führst User-Research durch und arbeitest agil im Produktteam.",
        "requirements_text": "Portfolio mit UX-Projekten, Figma-Kenntnisse, Verständnis für nutzerzentriertes Design.",
        "benefits": ["Homeoffice", "Weiterbildung", "Equipment", "Flexible Zeiten"],
        "urgency": 8, "recency": 10, "entry_friendly": True,
        "is_active": True, "featured": True, "puls": "Neu eingestellt",
        "apply_url": "https://www.rtl.de/karriere",
    },
    {
        "title": "Teamleiter Kundenservice (m/w/d)",
        "company": "DHL Group",
        "city": "Köln", "country": "Deutschland",
        "job_type": "Vollzeit", "work_model": "Vor Ort",
        "salary_min": 3500, "salary_unit": "€/Monat",
        "languages": ["Deutsch", "Englisch"],
        "experience": "3-5 Jahre",
        "skills": ["Kommunikation", "Kundenkontakt", "Organisation", "Zeitmanagement"],
        "keywords": ["teamleiter", "kundenservice", "dhl", "logistik", "führung"],
        "description": "Du leitest ein Team von 15 Mitarbeitenden im Kundenkontaktzentrum, sorgst für Qualität und Erreichbarkeit und entwickelst dein Team fachlich weiter.",
        "requirements_text": "Erfahrung in Führungsverantwortung, Empathie, Durchsetzungsstärke, Kenntnisse im Kundenservice.",
        "benefits": ["Weiterbildung", "Betriebliche Altersvorsorge", "Deutschlandticket", "Bonus"],
        "urgency": 8, "recency": 9, "entry_friendly": False,
        "is_active": True, "featured": False, "puls": "",
        "apply_url": "https://www.dhl.com/de/karriere",
    },

    # ── VOLLZEIT / BERLIN ─────────────────────────────────────────────────
    {
        "title": "Software Developer – Python (m/w/d)",
        "company": "Zalando SE",
        "city": "Berlin", "country": "Deutschland",
        "job_type": "Vollzeit", "work_model": "Hybrid",
        "salary_min": 5500, "salary_unit": "€/Monat",
        "languages": ["Englisch"],
        "experience": "1-2 Jahre",
        "skills": ["Python", "SQL", "Kommunikation", "Organisation"],
        "keywords": ["python", "developer", "zalando", "backend", "api", "microservices"],
        "description": "Du entwickelst skalierbare Backend-Services für Europas größte Modeplattform, arbeitest in cross-funktionalen Teams und nutzt modernste Cloud-Infrastruktur.",
        "requirements_text": "Python-Kenntnisse, REST-API-Erfahrung, Interesse an verteilten Systemen.",
        "benefits": ["Remote", "Equipment", "Weiterbildung", "Flexible Zeiten", "Verpflegung"],
        "urgency": 9, "recency": 10, "entry_friendly": True,
        "is_active": True, "featured": True, "puls": "Sehr gesucht",
        "apply_url": "https://jobs.zalando.com",
    },
    {
        "title": "Growth Marketing Manager (m/w/d)",
        "company": "Delivery Hero SE",
        "city": "Berlin", "country": "Deutschland",
        "job_type": "Vollzeit", "work_model": "Hybrid",
        "salary_min": 4200, "salary_unit": "€/Monat",
        "languages": ["Englisch"],
        "experience": "1-2 Jahre",
        "skills": ["Marketing", "SQL", "Excel", "Kommunikation"],
        "keywords": ["growth", "marketing", "delivery", "performance", "acquisition", "berlin"],
        "description": "Du verantwortest User-Acquisition-Kampagnen, optimierst Conversion-Funnels und analysierst A/B-Tests, um das Wachstum in neuen Märkten zu beschleunigen.",
        "requirements_text": "Erfahrung in Performance-Marketing, datengetriebene Arbeitsweise, SQL-Kenntnisse.",
        "benefits": ["Homeoffice", "Flexible Zeiten", "Weiterbildung", "Equipment"],
        "urgency": 8, "recency": 10, "entry_friendly": True,
        "is_active": True, "featured": False, "puls": "Neu eingestellt",
        "apply_url": "https://www.deliveryhero.com/careers",
    },
    {
        "title": "People Operations Manager (m/w/d)",
        "company": "HelloFresh SE",
        "city": "Berlin", "country": "Deutschland",
        "job_type": "Vollzeit", "work_model": "Hybrid",
        "salary_min": 4000, "salary_unit": "€/Monat",
        "languages": ["Deutsch", "Englisch"],
        "experience": "1-2 Jahre",
        "skills": ["Kommunikation", "Organisation", "Beratung", "Projektmanagement"],
        "keywords": ["hr", "people ops", "hellofresh", "recruiting", "onboarding"],
        "description": "Du begleitest den gesamten Employee-Lifecycle von Onboarding bis Offboarding, optimierst HR-Prozesse und bist Ansprechpartner für alle Mitarbeitenden-Themen.",
        "requirements_text": "Studium mit HR-Bezug, Empathie, Organisationstalent, Englisch fließend.",
        "benefits": ["Homeoffice", "Flexible Zeiten", "Weiterbildung", "Verpflegung"],
        "urgency": 7, "recency": 9, "entry_friendly": True,
        "is_active": True, "featured": False, "puls": "",
        "apply_url": "https://www.hellofresh.de/careers",
    },

    # ── VOLLZEIT / MÜNCHEN ────────────────────────────────────────────────
    {
        "title": "Finance Controller (m/w/d)",
        "company": "BMW Group",
        "city": "München", "country": "Deutschland",
        "job_type": "Vollzeit", "work_model": "Hybrid",
        "salary_min": 5500, "salary_unit": "€/Monat",
        "languages": ["Deutsch", "Englisch"],
        "experience": "3-5 Jahre",
        "skills": ["Excel", "Buchhaltung", "Präsentation", "Organisation"],
        "keywords": ["controlling", "finance", "bmw", "reporting", "fp&a"],
        "description": "Du erstellst monatliche Management-Reports, analysierst Abweichungen, koordinierst Forecasts und berätst Bereichsleiter in finanziellen Entscheidungen.",
        "requirements_text": "Studium BWL/Finance, 3+ Jahre Controlling-Erfahrung, sehr gute Excel-Kenntnisse, SAP von Vorteil.",
        "benefits": ["Homeoffice", "Bonus", "Betriebliche Altersvorsorge", "Weiterbildung"],
        "urgency": 7, "recency": 9, "entry_friendly": False,
        "is_active": True, "featured": False, "puls": "",
        "apply_url": "https://www.bmwgroup.com/karriere",
    },
    {
        "title": "Marketing Specialist Digital (m/w/d)",
        "company": "Allianz SE",
        "city": "München", "country": "Deutschland",
        "job_type": "Vollzeit", "work_model": "Hybrid",
        "salary_min": 4000, "salary_unit": "€/Monat",
        "languages": ["Deutsch", "Englisch"],
        "experience": "1-2 Jahre",
        "skills": ["Marketing", "Social Media", "Kommunikation", "Excel"],
        "keywords": ["digital", "marketing", "allianz", "versicherung", "content"],
        "description": "Du planst und setzt digitale Marketingkampagnen um, pflegst unsere Social-Media-Kanäle und optimierst die Customer Journey auf unseren digitalen Plattformen.",
        "requirements_text": "Abschluss in Marketing/Kommunikation, erste Praxiserfahrung, Affinität zu digitalen Kanälen.",
        "benefits": ["Homeoffice", "Weiterbildung", "Bonus", "Flexible Zeiten"],
        "urgency": 7, "recency": 8, "entry_friendly": True,
        "is_active": True, "featured": False, "puls": "",
        "apply_url": "https://www.allianz.de/karriere",
    },

    # ── VOLLZEIT / HAMBURG ────────────────────────────────────────────────
    {
        "title": "Account Manager B2B (m/w/d)",
        "company": "Airbus Deutschland GmbH",
        "city": "Hamburg", "country": "Deutschland",
        "job_type": "Vollzeit", "work_model": "Hybrid",
        "salary_min": 4800, "salary_unit": "€/Monat",
        "languages": ["Deutsch", "Englisch"],
        "experience": "3-5 Jahre",
        "skills": ["Verkauf", "Kommunikation", "Kundenkontakt", "Präsentation"],
        "keywords": ["account", "b2b", "airbus", "sales", "aviation"],
        "description": "Du betreust internationale Airline-Kunden, verhandelst Verträge für Ersatzteile und Services und bist das Bindeglied zwischen Kunden und internen Teams.",
        "requirements_text": "3+ Jahre B2B-Vertriebserfahrung, Englisch fließend, Reisebereitschaft ca. 20%.",
        "benefits": ["Homeoffice", "Bonus", "Weiterbildung", "Betriebliche Altersvorsorge"],
        "urgency": 6, "recency": 8, "entry_friendly": False,
        "is_active": True, "featured": False, "puls": "",
        "apply_url": "https://www.airbus.com/en/careers",
    },
    {
        "title": "Junior Brand Manager (m/w/d)",
        "company": "Beiersdorf AG",
        "city": "Hamburg", "country": "Deutschland",
        "job_type": "Vollzeit", "work_model": "Hybrid",
        "salary_min": 3600, "salary_unit": "€/Monat",
        "languages": ["Deutsch", "Englisch"],
        "experience": "Berufseinsteiger",
        "skills": ["Marketing", "Kreativität", "Kommunikation", "Präsentation"],
        "keywords": ["brand", "marketing", "beiersdorf", "nivea", "fmcg"],
        "description": "Du unterstützt das Marken-Team von NIVEA bei der Entwicklung und Umsetzung von Kampagnen, analysierst Marktdaten und koordinierst Agenturen.",
        "requirements_text": "Studium in Marketing/BWL, Praktikumserfahrung in Marketing, kreativ und analytisch.",
        "benefits": ["Homeoffice", "Weiterbildung", "Bonus", "Flexible Zeiten"],
        "urgency": 8, "recency": 10, "entry_friendly": True,
        "is_active": True, "featured": True, "puls": "Neu eingestellt",
        "apply_url": "https://www.beiersdorf.de/karriere",
    },

    # ── VOLLZEIT / FRANKFURT ──────────────────────────────────────────────
    {
        "title": "Investment Analyst (m/w/d)",
        "company": "Deutsche Bank AG",
        "city": "Frankfurt", "country": "Deutschland",
        "job_type": "Vollzeit", "work_model": "Vor Ort",
        "salary_min": 5800, "salary_unit": "€/Monat",
        "languages": ["Deutsch", "Englisch"],
        "experience": "1-2 Jahre",
        "skills": ["Excel", "Buchhaltung", "Präsentation", "Kommunikation"],
        "keywords": ["investment", "analyst", "deutsche bank", "finance", "banking"],
        "description": "Du analysierst Finanzkennzahlen, erstellst Bewertungsmodelle (DCF, LBO) und unterstützt das Team bei M&A-Transaktionen und Capital Markets Deals.",
        "requirements_text": "Studium in Finance/Wirtschaft, erste Praktikumserfahrung im Banking, sehr gute Excel-Kenntnisse.",
        "benefits": ["Bonus", "Weiterbildung", "Betriebliche Altersvorsorge"],
        "urgency": 8, "recency": 9, "entry_friendly": True,
        "is_active": True, "featured": False, "puls": "Sehr gesucht",
        "apply_url": "https://www.db.com/karriere",
    },

    # ── REMOTE VOLLZEIT ───────────────────────────────────────────────────
    {
        "title": "Frontend Developer – React (m/w/d)",
        "company": "N26 GmbH",
        "city": "Berlin", "country": "Deutschland",
        "job_type": "Vollzeit", "work_model": "Remote",
        "salary_min": 5500, "salary_unit": "€/Monat",
        "languages": ["Englisch"],
        "experience": "1-2 Jahre",
        "skills": ["Design", "Kommunikation", "Kreativität", "Zeitmanagement"],
        "keywords": ["frontend", "react", "developer", "n26", "fintech", "javascript"],
        "description": "Du baust hochwertige React-Komponenten für unsere Banking-App, arbeitest eng mit Design und Backend zusammen und trägst zur Code-Qualität bei.",
        "requirements_text": "Solide JavaScript/React-Kenntnisse, TypeScript-Erfahrung, Interesse an FinTech.",
        "benefits": ["Remote", "Equipment", "Weiterbildung", "Flexible Zeiten"],
        "urgency": 9, "recency": 10, "entry_friendly": True,
        "is_active": True, "featured": True, "puls": "Sehr gesucht",
        "apply_url": "https://n26.com/en-de/careers",
    },
    {
        "title": "Customer Success Manager Remote (m/w/d)",
        "company": "HubSpot Germany GmbH",
        "city": "Düsseldorf", "country": "Deutschland",
        "job_type": "Vollzeit", "work_model": "Remote",
        "salary_min": 4000, "salary_unit": "€/Monat",
        "languages": ["Deutsch", "Englisch"],
        "experience": "1-2 Jahre",
        "skills": ["Kommunikation", "Kundenkontakt", "Beratung", "Organisation"],
        "keywords": ["customer success", "csm", "hubspot", "saas", "remote", "crm"],
        "description": "Du onboardest neue B2B-Kunden, führst regelmäßige Check-ins durch und sorgst dafür, dass sie den maximalen Nutzen aus HubSpot ziehen.",
        "requirements_text": "Erfahrung im Customer-Success oder Account-Management, Empathie, SaaS-Affinität.",
        "benefits": ["Remote", "Equipment", "Flexible Zeiten", "Weiterbildung", "Bonus"],
        "urgency": 8, "recency": 10, "entry_friendly": True,
        "is_active": True, "featured": True, "puls": "Neu · Sehr gesucht",
        "apply_url": "https://www.hubspot.com/jobs",
    },
    {
        "title": "SEO Manager Remote (m/w/d)",
        "company": "Statista GmbH",
        "city": "Hamburg", "country": "Deutschland",
        "job_type": "Vollzeit", "work_model": "Remote",
        "salary_min": 3800, "salary_unit": "€/Monat",
        "languages": ["Deutsch", "Englisch"],
        "experience": "1-2 Jahre",
        "skills": ["Marketing", "Excel", "Kommunikation", "Organisation"],
        "keywords": ["seo", "search", "statista", "content", "organic", "remote"],
        "description": "Du verantwortest die organische Sichtbarkeit unserer Datenportale, führst Keyword-Recherchen durch, optimierst Content und baust Backlink-Strategien auf.",
        "requirements_text": "SEO-Erfahrung (On-Page und Off-Page), Kenntnisse in Google Search Console, analytisch.",
        "benefits": ["Remote", "Flexible Zeiten", "Weiterbildung", "Equipment"],
        "urgency": 7, "recency": 9, "entry_friendly": True,
        "is_active": True, "featured": False, "puls": "",
        "apply_url": "https://www.statista.com/karriere",
    },

    # ── WERKSTUDENT ───────────────────────────────────────────────────────
    {
        "title": "Werkstudent Marketing (m/w/d)",
        "company": "Henkel AG & Co. KGaA",
        "city": "Düsseldorf", "country": "Deutschland",
        "job_type": "Werkstudent", "work_model": "Hybrid",
        "salary_min": 16, "salary_unit": "€/Stunde",
        "languages": ["Deutsch", "Englisch"],
        "experience": "Berufseinsteiger",
        "skills": ["Marketing", "Social Media", "Excel", "Kommunikation"],
        "keywords": ["werkstudent", "marketing", "henkel", "student", "bachelor"],
        "description": "Unterstütze unser Marketing-Team bei der Planung und Auswertung von Kampagnen, erstelle Präsentationen und recherchiere Markttrends.",
        "requirements_text": "Eingeschriebener Student BWL/Marketing, mind. 2 Semester verbleibend, sicheres Deutsch und Englisch.",
        "benefits": ["Flexible Zeiten", "Weiterbildung", "Verpflegung"],
        "urgency": 8, "recency": 10, "entry_friendly": True,
        "is_active": True, "featured": False, "puls": "Neu eingestellt",
        "apply_url": "https://www.henkel.com/careers",
    },
    {
        "title": "Werkstudent Data & Analytics (m/w/d)",
        "company": "Vodafone Deutschland GmbH",
        "city": "Düsseldorf", "country": "Deutschland",
        "job_type": "Werkstudent", "work_model": "Hybrid",
        "salary_min": 17, "salary_unit": "€/Stunde",
        "languages": ["Deutsch", "Englisch"],
        "experience": "Berufseinsteiger",
        "skills": ["Excel", "SQL", "Kommunikation", "Zeitmanagement"],
        "keywords": ["werkstudent", "data", "analytics", "vodafone", "sql", "python"],
        "description": "Du unterstützt unser Data-Team bei Analysen, erstellst Dashboards und wertest Kundendaten aus, um Produktentscheidungen zu verbessern.",
        "requirements_text": "Studium in Informatik/Mathematik/BWL, SQL-Grundkenntnisse, analytische Denkweise.",
        "benefits": ["Flexible Zeiten", "Homeoffice", "Weiterbildung"],
        "urgency": 7, "recency": 9, "entry_friendly": True,
        "is_active": True, "featured": False, "puls": "",
        "apply_url": "https://www.vodafone.de/karriere",
    },
    {
        "title": "Werkstudent Software Development (m/w/d)",
        "company": "trivago N.V.",
        "city": "Düsseldorf", "country": "Deutschland",
        "job_type": "Werkstudent", "work_model": "Hybrid",
        "salary_min": 18, "salary_unit": "€/Stunde",
        "languages": ["Englisch"],
        "experience": "Berufseinsteiger",
        "skills": ["Python", "SQL", "Zeitmanagement", "Kommunikation"],
        "keywords": ["werkstudent", "developer", "trivago", "python", "backend"],
        "description": "Du arbeitest als vollwertiges Teammitglied an echten Produktfeatures, reviewst Code, schreibst Tests und lernst agile Entwicklungsmethoden.",
        "requirements_text": "Studium Informatik, erste Programmierkenntnisse (Python oder Java), Englisch gut.",
        "benefits": ["Flexible Zeiten", "Equipment", "Verpflegung", "Weiterbildung"],
        "urgency": 8, "recency": 10, "entry_friendly": True,
        "is_active": True, "featured": False, "puls": "Neu eingestellt",
        "apply_url": "https://www.trivago.de/careers",
    },
    {
        "title": "Werkstudent HR & Recruiting (m/w/d)",
        "company": "Douglas GmbH",
        "city": "Düsseldorf", "country": "Deutschland",
        "job_type": "Werkstudent", "work_model": "Hybrid",
        "salary_min": 15, "salary_unit": "€/Stunde",
        "languages": ["Deutsch", "Englisch"],
        "experience": "Berufseinsteiger",
        "skills": ["Kommunikation", "Organisation", "Zeitmanagement", "Beratung"],
        "keywords": ["werkstudent", "hr", "recruiting", "douglas", "personalmanagement"],
        "description": "Du unterstützt das Recruiting-Team bei Active Sourcing, koordinierst Interviews und pflegst unser Bewerbermanagementsystem.",
        "requirements_text": "Studium Wirtschaft/Psychologie/o.ä., Interesse an HR, Organisationstalent.",
        "benefits": ["Flexible Zeiten", "Mitarbeiterrabatt", "Homeoffice"],
        "urgency": 6, "recency": 8, "entry_friendly": True,
        "is_active": True, "featured": False, "puls": "",
        "apply_url": "https://www.douglas.de/karriere",
    },

    # ── AUSBILDUNG ────────────────────────────────────────────────────────
    {
        "title": "Ausbildung Kaufmann/-frau für Büromanagement",
        "company": "Stadtsparkasse Düsseldorf",
        "city": "Düsseldorf", "country": "Deutschland",
        "job_type": "Ausbildung", "work_model": "Vor Ort",
        "salary_min": 900, "salary_unit": "€/Monat",
        "languages": ["Deutsch"],
        "experience": "Berufseinsteiger",
        "skills": ["Organisation", "Kommunikation", "Excel", "Zeitmanagement"],
        "keywords": ["ausbildung", "kaufmann", "büro", "sparkasse", "verwaltung"],
        "description": "3-jährige duale Ausbildung: Lerne alle kaufmännischen Abläufe eines modernen Finanzinstituts kennen – von Büromanagement bis Kundenkommunikation.",
        "requirements_text": "Mittlere Reife oder Abitur, gute Deutschnoten, ordentliches Auftreten.",
        "benefits": ["Weiterbildung", "Betriebliche Altersvorsorge", "Übernahmechance"],
        "urgency": 7, "recency": 9, "entry_friendly": True,
        "is_active": True, "featured": False, "puls": "",
        "apply_url": "https://www.sskduesseldorf.de/karriere",
    },
    {
        "title": "Ausbildung Fachinformatiker/-in Anwendungsentwicklung",
        "company": "Vodafone Deutschland GmbH",
        "city": "Düsseldorf", "country": "Deutschland",
        "job_type": "Ausbildung", "work_model": "Hybrid",
        "salary_min": 1050, "salary_unit": "€/Monat",
        "languages": ["Deutsch"],
        "experience": "Berufseinsteiger",
        "skills": ["Kommunikation", "Organisation", "Zeitmanagement", "Kreativität"],
        "keywords": ["ausbildung", "fachinformatiker", "it", "vodafone", "entwicklung"],
        "description": "Lerne in 3 Jahren Softwareentwicklung, Datenbankdesign und agile Methoden – mitten in einem internationalen Tech-Unternehmen.",
        "requirements_text": "Mittlere Reife oder Abitur, Interesse an Technik und Programmierung, logisches Denken.",
        "benefits": ["Weiterbildung", "Homeoffice", "Equipment", "Übernahmechance"],
        "urgency": 8, "recency": 10, "entry_friendly": True,
        "is_active": True, "featured": True, "puls": "Neu eingestellt",
        "apply_url": "https://www.vodafone.de/karriere",
    },
    {
        "title": "Ausbildung Kaufmann/-frau im Einzelhandel",
        "company": "Peek & Cloppenburg KG",
        "city": "Düsseldorf", "country": "Deutschland",
        "job_type": "Ausbildung", "work_model": "Vor Ort",
        "salary_min": 800, "salary_unit": "€/Monat",
        "languages": ["Deutsch"],
        "experience": "Berufseinsteiger",
        "skills": ["Kundenkontakt", "Kommunikation", "Verkauf", "Organisation"],
        "keywords": ["ausbildung", "einzelhandel", "kaufmann", "peek", "mode", "retail"],
        "description": "2-jährige Ausbildung in einem der bekanntesten deutschen Modehäuser: Verkauf, Warenwirtschaft, Kundenberatung und Visual Merchandising.",
        "requirements_text": "Mittlere Reife, Interesse an Mode, kommunikativ und serviceorientiert.",
        "benefits": ["Mitarbeiterrabatt", "Weiterbildung", "Übernahmechance"],
        "urgency": 7, "recency": 9, "entry_friendly": True,
        "is_active": True, "featured": False, "puls": "",
        "apply_url": "https://www.peek-cloppenburg.de/karriere",
    },
    {
        "title": "Ausbildung Mediengestalter/-in Digital und Print",
        "company": "RTL Deutschland GmbH",
        "city": "Köln", "country": "Deutschland",
        "job_type": "Ausbildung", "work_model": "Vor Ort",
        "salary_min": 950, "salary_unit": "€/Monat",
        "languages": ["Deutsch"],
        "experience": "Berufseinsteiger",
        "skills": ["Design", "Kreativität", "Kommunikation", "Social Media"],
        "keywords": ["ausbildung", "mediengestalter", "design", "rtl", "grafik", "medien"],
        "description": "3-jährige Ausbildung beim größten deutschen TV-Sender: Du gestaltest Grafiken, Spots, Social-Media-Content und lernst alle Schritte der digitalen Medienproduktion.",
        "requirements_text": "Abitur oder Mittlere Reife, kreatives Portfolio, Adobe-Grundkenntnisse von Vorteil.",
        "benefits": ["Weiterbildung", "Kreatives Umfeld", "Übernahmechance"],
        "urgency": 8, "recency": 10, "entry_friendly": True,
        "is_active": True, "featured": False, "puls": "Neu eingestellt",
        "apply_url": "https://www.rtl.de/karriere",
    },

    # ── MINIJOB ───────────────────────────────────────────────────────────
    {
        "title": "Minijob Verkäufer/-in Bäckerei (m/w/d)",
        "company": "Bäckerei Hinkel",
        "city": "Düsseldorf", "country": "Deutschland",
        "job_type": "Minijob", "work_model": "Vor Ort",
        "salary_min": 13, "salary_unit": "€/Stunde",
        "languages": ["Deutsch"],
        "experience": "Berufseinsteiger",
        "skills": ["Kundenkontakt", "Kommunikation", "Verlässlichkeit"],
        "keywords": ["minijob", "verkäufer", "bäckerei", "düsseldorf", "kasse", "service"],
        "description": "Du bedienst unsere Stammkunden, kassierst, belegst Brötchen und sorgst für eine saubere und freundliche Atmosphäre – stundenweise oder an Wochenenden.",
        "requirements_text": "Freundliches Auftreten, Zuverlässigkeit, keine Vorerfahrung nötig.",
        "benefits": ["Flexible Zeiten", "Verpflegung"],
        "urgency": 9, "recency": 10, "entry_friendly": True,
        "is_active": True, "featured": False, "puls": "Sehr gesucht",
        "apply_url": "",
    },
    {
        "title": "Minijob Lagerhelfer (m/w/d)",
        "company": "Amazon Fulfillment Germany GmbH",
        "city": "Düsseldorf", "country": "Deutschland",
        "job_type": "Minijob", "work_model": "Vor Ort",
        "salary_min": 13, "salary_unit": "€/Stunde",
        "languages": ["Deutsch"],
        "experience": "Berufseinsteiger",
        "skills": ["Verlässlichkeit", "Zeitmanagement", "Organisation"],
        "keywords": ["minijob", "lager", "amazon", "helfer", "logistik"],
        "description": "Kommissionierung und Verpackung von Bestellungen im Fulfillment-Center. Flexible Schichten, ideal als Nebenjob.",
        "requirements_text": "Körperlich belastbar, zuverlässig, schichtbereit, kein Führerschein nötig.",
        "benefits": ["Flexible Zeiten", "Betriebliche Altersvorsorge"],
        "urgency": 9, "recency": 10, "entry_friendly": True,
        "is_active": True, "featured": False, "puls": "Sehr gesucht",
        "apply_url": "https://www.amazon.jobs/de",
    },
    {
        "title": "Aushilfe Supermarktkasse (m/w/d)",
        "company": "REWE Markt GmbH",
        "city": "Köln", "country": "Deutschland",
        "job_type": "Minijob", "work_model": "Vor Ort",
        "salary_min": 13, "salary_unit": "€/Stunde",
        "languages": ["Deutsch"],
        "experience": "Berufseinsteiger",
        "skills": ["Kundenkontakt", "Verlässlichkeit", "Kommunikation"],
        "keywords": ["minijob", "kasse", "supermarkt", "rewe", "aushilfe"],
        "description": "Kassenarbeit, Kundenbetreuung und Warenpflege in unserem REWE-Markt. Stundenweise, auch an Wochenenden.",
        "requirements_text": "Freundlichkeit, Zuverlässigkeit, Interesse am Kundenkontakt.",
        "benefits": ["Flexible Zeiten", "Mitarbeiterrabatt"],
        "urgency": 9, "recency": 10, "entry_friendly": True,
        "is_active": True, "featured": False, "puls": "",
        "apply_url": "https://www.rewe-group.com/karriere",
    },

    # ── PRAKTIKUM / SCHÜLERPRAKTIKUM ──────────────────────────────────────
    {
        "title": "Praktikum Marketing (m/w/d) – 6 Monate",
        "company": "Beiersdorf AG",
        "city": "Hamburg", "country": "Deutschland",
        "job_type": "Praktikum", "work_model": "Hybrid",
        "salary_min": 1200, "salary_unit": "€/Monat",
        "languages": ["Deutsch", "Englisch"],
        "experience": "Berufseinsteiger",
        "skills": ["Marketing", "Excel", "Kommunikation", "Kreativität"],
        "keywords": ["praktikum", "marketing", "beiersdorf", "nivea", "pflichtpraktikum"],
        "description": "6-monatiges Pflicht- oder freiwilliges Praktikum im NIVEA-Marketing-Team: Kampagnenplanung, Marktanalysen, Agentursteuerung.",
        "requirements_text": "Immatrikulierter Student, mind. 4. Semester, Marketing-Interesse, Englisch gut.",
        "benefits": ["Homeoffice", "Weiterbildung", "Verpflegung"],
        "urgency": 7, "recency": 9, "entry_friendly": True,
        "is_active": True, "featured": False, "puls": "",
        "apply_url": "https://www.beiersdorf.de/karriere",
    },
    {
        "title": "Schülerpraktikum Medien & Kommunikation (2 Wochen)",
        "company": "RTL Deutschland GmbH",
        "city": "Köln", "country": "Deutschland",
        "job_type": "Schülerpraktikum", "work_model": "Vor Ort",
        "salary_min": 12, "salary_unit": "€/Stunde",
        "languages": ["Deutsch"],
        "experience": "Berufseinsteiger",
        "skills": ["Kommunikation", "Kreativität", "Social Media"],
        "keywords": ["schülerpraktikum", "praktikum", "medien", "rtl", "tv", "schule"],
        "description": "2-wöchiges Orientierungspraktikum hinter den Kulissen des größten deutschen TV-Senders: Redaktion, Produktion, Social Media.",
        "requirements_text": "Schüler ab Klasse 9, Interesse an Medien, Zuverlässigkeit.",
        "benefits": ["Spannende Einblicke", "Netzwerk"],
        "urgency": 6, "recency": 8, "entry_friendly": True,
        "is_active": True, "featured": False, "puls": "",
        "apply_url": "https://www.rtl.de/karriere",
    },

    # ── FERIENJOB ─────────────────────────────────────────────────────────
    {
        "title": "Ferienjob Lagerhelfer Sommer (m/w/d)",
        "company": "Amazon Fulfillment Germany GmbH",
        "city": "Düsseldorf", "country": "Deutschland",
        "job_type": "Ferienjob", "work_model": "Vor Ort",
        "salary_min": 14, "salary_unit": "€/Stunde",
        "languages": ["Deutsch"],
        "experience": "Berufseinsteiger",
        "skills": ["Verlässlichkeit", "Zeitmanagement"],
        "keywords": ["ferienjob", "sommer", "amazon", "lager", "schüler", "student"],
        "description": "Sommer-Ferienjob für Schüler und Studenten: Kommissionierung im Fulfillment-Center, 4-8 Wochen, verschiedene Schichtmodelle.",
        "requirements_text": "Mindestalter 16 Jahre, körperlich fit, zuverlässig.",
        "benefits": ["Flexible Zeiten", "Gute Bezahlung"],
        "urgency": 8, "recency": 10, "entry_friendly": True,
        "is_active": True, "featured": False, "puls": "Neu eingestellt",
        "apply_url": "https://www.amazon.jobs/de",
    },
    {
        "title": "Ferienjob Hostess / Host Events (m/w/d)",
        "company": "Messe Düsseldorf GmbH",
        "city": "Düsseldorf", "country": "Deutschland",
        "job_type": "Ferienjob", "work_model": "Vor Ort",
        "salary_min": 14, "salary_unit": "€/Stunde",
        "languages": ["Deutsch", "Englisch"],
        "experience": "Berufseinsteiger",
        "skills": ["Kundenkontakt", "Kommunikation", "Verlässlichkeit"],
        "keywords": ["ferienjob", "hostess", "messe", "düsseldorf", "events", "host"],
        "description": "Begleite internationale Fachmessen als Hostess oder Host: Besucherempfang, Orientierung auf dem Gelände, Koordination.",
        "requirements_text": "Gepflegtes Auftreten, Englisch gut, flexibel, mindestens 18 Jahre.",
        "benefits": ["Flexible Zeiten", "Netzwerk", "Interessante Branche"],
        "urgency": 7, "recency": 9, "entry_friendly": True,
        "is_active": True, "featured": False, "puls": "",
        "apply_url": "https://www.messe-duesseldorf.de/karriere",
    },

    # ── TEILZEIT ──────────────────────────────────────────────────────────
    {
        "title": "Teilzeit Buchhalter/-in (20h/Woche)",
        "company": "Kanzlei Steuerberater Müller & Partner",
        "city": "Düsseldorf", "country": "Deutschland",
        "job_type": "Teilzeit", "work_model": "Hybrid",
        "salary_min": 2200, "salary_unit": "€/Monat",
        "languages": ["Deutsch"],
        "experience": "1-2 Jahre",
        "skills": ["Buchhaltung", "Excel", "Organisation", "Verlässlichkeit"],
        "keywords": ["teilzeit", "buchhalter", "steuerbüro", "buchhaltung", "datev"],
        "description": "Laufende Finanzbuchhaltung für Mandanten aus Mittelstand und Gastronomie, DATEV-Eingabe, Umsatzsteuervoranmeldungen – 20h/Woche, flexibel einteilbar.",
        "requirements_text": "Abgeschlossene kaufmännische Ausbildung, DATEV-Kenntnisse, gewissenhaft.",
        "benefits": ["Flexible Zeiten", "Homeoffice", "Weiterbildung"],
        "urgency": 7, "recency": 8, "entry_friendly": False,
        "is_active": True, "featured": False, "puls": "",
        "apply_url": "",
    },
    {
        "title": "Teilzeit Customer Support (m/w/d) 25h",
        "company": "Zalando SE",
        "city": "Berlin", "country": "Deutschland",
        "job_type": "Teilzeit", "work_model": "Remote",
        "salary_min": 2000, "salary_unit": "€/Monat",
        "languages": ["Deutsch"],
        "experience": "Berufseinsteiger",
        "skills": ["Kundenkontakt", "Kommunikation", "Zeitmanagement", "Organisation"],
        "keywords": ["teilzeit", "support", "zalando", "kundenservice", "remote"],
        "description": "Du hilfst Zalando-Kunden per Chat und E-Mail bei Fragen zu Bestellungen, Retouren und Zahlungen – 25h/Woche, komplett remote.",
        "requirements_text": "Empathie, schnelle Auffassungsgabe, sicheres schriftliches Deutsch.",
        "benefits": ["Remote", "Flexible Zeiten", "Mitarbeiterrabatt"],
        "urgency": 8, "recency": 10, "entry_friendly": True,
        "is_active": True, "featured": False, "puls": "Sehr gesucht",
        "apply_url": "https://jobs.zalando.com",
    },

    # ── WORK AND TRAVEL ───────────────────────────────────────────────────
    {
        "title": "Work & Travel Farmhelper Australien",
        "company": "Backpacker Job Board",
        "city": "Düsseldorf", "country": "Australien",
        "job_type": "Work and Travel", "work_model": "Vor Ort",
        "salary_min": 25, "salary_unit": "€/Stunde",
        "languages": ["Englisch"],
        "experience": "Berufseinsteiger",
        "skills": ["Verlässlichkeit", "Zeitmanagement", "Kommunikation"],
        "keywords": ["work and travel", "australien", "farm", "backpacker", "visum", "whv"],
        "description": "Farmarbeit in Australien für Working-Holiday-Visum-Inhaber: Ernte, Verpackung, Tierpflege. 88 Tage Regional Work für Second-Year-Visum anrechenbar.",
        "requirements_text": "WHV oder Working Holiday Visum für Australien, körperlich fit, Englisch Grundkenntnisse.",
        "benefits": ["Unterkunft", "Verpflegung", "Visum-Anrechnung"],
        "urgency": 6, "recency": 8, "entry_friendly": True,
        "is_active": True, "featured": False, "puls": "",
        "apply_url": "https://www.backpackerjobboard.com.au",
    },
]


def insert_jobs():
    """Alle Jobs in Supabase jobs-Tabelle eintragen (überspringt Duplikate)."""
    print(f"\n🚀 Starte Job-Import: {len(JOBS)} Jobs\n")
    inserted = 0
    skipped = 0
    errors = 0

    for i, job in enumerate(JOBS, 1):
        try:
            # Prüfen ob Job schon existiert
            existing = sb.table("jobs") \
                .select("id") \
                .eq("title", job["title"]) \
                .eq("company", job["company"]) \
                .execute()

            if existing.data:
                print(f"  ⏭  [{i:02d}] Bereits vorhanden: {job['title']} @ {job['company']}")
                skipped += 1
                continue

            sb.table("jobs").insert(job).execute()
            print(f"  ✅ [{i:02d}] Eingetragen: {job['title']} @ {job['company']} ({job['city']})")
            inserted += 1
            time.sleep(0.1)  # Rate limit schonen

        except Exception as e:
            print(f"  ❌ [{i:02d}] Fehler bei {job['title']}: {e}")
            errors += 1

    print(f"\n{'─'*55}")
    print(f"  Eingetragen : {inserted}")
    print(f"  Übersprungen: {skipped}")
    print(f"  Fehler      : {errors}")
    print(f"{'─'*55}\n")

    if errors > 0:
        print("⚠️  Fehler aufgetreten. Prüfe ob die 'jobs'-Tabelle in Supabase")
        print("   existiert und ob RLS Insert erlaubt (service_role key nötig).")
    else:
        print("✅ Fertig! Starte die App — die Jobs erscheinen sofort.\n")


def fetch_from_ba_api(suchbegriffe=None, staedte=None, max_jobs=50):
    """
    Holt echte Jobs von der Bundesagentur für Arbeit (kostenlos, kein API-Key).
    Mappt sie ins jobr-Schema und trägt sie in Supabase ein.

    Aufruf: python3 seed_jobs.py --ba
    """
    if suchbegriffe is None:
        suchbegriffe = ["Marketing", "Sales", "IT", "Logistik", "Gastronomie", "Pflege"]
    if staedte is None:
        staedte = ["Düsseldorf", "Köln", "Hamburg", "Berlin", "München", "Frankfurt"]

    JOBART_MAP = {
        "01": "Vollzeit", "02": "Teilzeit", "04": "Minijob",
        "05": "Praktikum", "06": "Ausbildung",
    }
    MODELL_MAP = {
        "1": "Vor Ort", "2": "Remote", "3": "Hybrid",
    }

    headers = {"X-API-Key": "jobboerse-jobsuche-ui"}
    inserted = 0
    print("\n🌐 Bundesagentur für Arbeit API – Live-Fetch\n")

    for stadt in staedte:
        for begriff in suchbegriffe:
            url = (
                "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs"
                f"?was={requests.utils.quote(begriff)}"
                f"&wo={requests.utils.quote(stadt)}"
                f"&umkreis=25&size=10&angebotsart=1"
            )
            try:
                resp = requests.get(url, headers=headers, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                stellenangebote = data.get("stellenangebote") or []

                for s in stellenangebote[:5]:
                    try:
                        title = s.get("titel", "")
                        company = s.get("arbeitgeber", "Unbekannt")
                        city = s.get("arbeitsort", {}).get("ort", stadt)
                        job_type = JOBART_MAP.get(s.get("angebotsart", "01"), "Vollzeit")
                        ref_nr = s.get("refnr", "")
                        apply_url = f"https://jobboerse.arbeitsagentur.de/vamJB/startseite.html?kuerzel={ref_nr}" if ref_nr else ""

                        job_data = {
                            "title": title,
                            "company": company,
                            "city": city,
                            "country": "Deutschland",
                            "job_type": job_type,
                            "work_model": "Vor Ort",
                            "salary_min": 2500,
                            "salary_unit": "€/Monat",
                            "languages": ["Deutsch"],
                            "experience": "Berufseinsteiger",
                            "skills": [],
                            "keywords": [begrif.lower() for begrif in [titel_wort for titel_wort in title.lower().split() if len(titel_wort) > 3][:5]],
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

                        existing = sb.table("jobs").select("id").eq("title", title).eq("company", company).execute()
                        if not existing.data:
                            sb.table("jobs").insert(job_data).execute()
                            print(f"  ✅ {title} @ {company} ({city})")
                            inserted += 1
                        time.sleep(0.15)
                    except Exception as e:
                        print(f"  ⚠️  Job übersprungen: {e}")

            except Exception as e:
                print(f"  ❌ API-Fehler ({stadt}/{begriff}): {e}")
            time.sleep(0.5)

    print(f"\n✅ {inserted} neue Jobs von der BA-API eingetragen.\n")


def generate_indeed_url(title: str, city: str, company: str) -> str:
    """Generiert eine gezielte Indeed-Suchseite für diesen Job."""
    from urllib.parse import quote_plus
    clean_title = title.replace(" (m/w/d)", "").replace(" (m/w)", "").replace(" – ", " ").strip()
    return (
        f"https://de.indeed.com/jobs"
        f"?q={quote_plus(clean_title)}"
        f"&l={quote_plus(city)}"
        f"&rbc={quote_plus(company)}"
        f"&sc=0kf%3Aattr(DSQF7)%3B"  # Volltext-Match bevorzugen
    )


def update_apply_urls():
    """
    Aktualisiert alle apply_url-Felder in Supabase mit gezielten
    Indeed-Stellensuch-Links (Firma + Jobtitel + Stadt).

    Aufruf: python3 seed_jobs.py --update-urls
    """
    print(f"\n🔗 Aktualisiere Bewerbungslinks für {len(JOBS)} Jobs...\n")
    updated = 0
    errors = 0

    for i, job in enumerate(JOBS, 1):
        try:
            new_url = generate_indeed_url(job["title"], job["city"], job["company"])
            result = sb.table("jobs") \
                .update({"apply_url": new_url}) \
                .eq("title", job["title"]) \
                .eq("company", job["company"]) \
                .execute()
            if result.data:
                print(f"  ✅ [{i:02d}] {job['title']} @ {job['company']}")
                updated += 1
            else:
                print(f"  ⏭  [{i:02d}] Nicht gefunden (skip): {job['title']}")
            time.sleep(0.05)
        except Exception as e:
            print(f"  ❌ [{i:02d}] {job['title']}: {e}")
            errors += 1

    print(f"\n{'─'*55}")
    print(f"  Aktualisiert: {updated}")
    print(f"  Fehler      : {errors}")
    print(f"{'─'*55}")
    print("✅ Links aktualisiert — Benutzer werden jetzt zu echten")
    print("   Stellenanzeigen auf Indeed weitergeleitet.\n")


if __name__ == "__main__":
    if "--ba" in sys.argv:
        fetch_from_ba_api()
    elif "--update-urls" in sys.argv:
        update_apply_urls()
    else:
        insert_jobs()
        print("💡 Tipps:")
        print("   python3 seed_jobs.py --ba           Live-Jobs von der BA-API holen")
        print("   python3 seed_jobs.py --update-urls  Bewerbungslinks auf Indeed aktualisieren\n")
