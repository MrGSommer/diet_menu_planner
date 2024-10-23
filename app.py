import streamlit as st
from neo4j import GraphDatabase
from passlib.context import CryptContext
from datetime import datetime
import locale

# Setze die Sprache für die Anzeige des Datums auf Deutsch
locale.setlocale(locale.LC_TIME, "de_DE")

# Zugangsdaten für Neo4j (Admin-Daten)
neo4j_uri = st.secrets["credentials"]["AURA_NEO4J_URI"]
neo4j_user = st.secrets["credentials"]["AURA_NEO4J_USERNAME"]
neo4j_password = st.secrets["credentials"]["AURA_NEO4J_PASSWORD"]

# Session States initialisieren
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'role' not in st.session_state:
    st.session_state['role'] = None
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None
if 'registration_date' not in st.session_state:
    st.session_state['registration_date'] = None
if 'user_vorname' not in st.session_state:
    st.session_state['user_vorname'] = None
if 'membership_duration_years' not in st.session_state:
    st.session_state['membership_duration_years'] = 0
if 'membership_duration_months' not in st.session_state:
    st.session_state['membership_duration_months'] = 0
if 'connection_type' not in st.session_state:
    st.session_state['connection_type'] = 'Aura'

# CryptContext erstellen für Passwort-Hashing
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Funktion zum Hashen von Eingaben wie Passwort
def hash_value(input_value):
    # Hasht den übergebenen Wert (z.B. Passwort)
    return pwd_context.hash(input_value)

# Funktion zur Verifizierung von gehashten Werten
def verify_value(input_value, hashed_value):
    # Überprüft, ob der Input mit dem gehashten Wert übereinstimmt
    return pwd_context.verify(input_value, hashed_value)

# Neo4j-Verbindung herstellen
def call_client(neo4j_uri, neo4j_user, neo4j_password):
    # Stellt die Verbindung zu Neo4j her und gibt den Driver zurück
    try:
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        return driver
    except Exception as e:
        st.error(f"Verbindungsfehler: {e}")
        return None

# Authentifizierung des Benutzers
def authenticate_user(driver, user_email, user_password):
    # Authentifiziert den Benutzer anhand der E-Mail und des Passworts
    cypher_query = """
    MATCH (a:Nutzer {user_email: $user_email})
    RETURN a.passwort AS user_passwort, a.vorname AS user_vorname
    """
    query_params = {"user_email": user_email}
    try:
        with driver.session() as session:
            result = session.run(cypher_query, query_params)
            user = result.single()

            if user and verify_value(user_password, user["user_passwort"]):
                # Gibt True und den Vornamen zurück, wenn Authentifizierung erfolgreich
                return True, user["user_vorname"]
            else:
                st.error("Falsches Passwort oder E-Mail.")
                return False, None
    except Exception as e:
        st.error(f"Fehler bei der Authentifizierung: {e}")
        return False, None

# Passwort zurücksetzen
def reset_password(driver, user_email, new_password):
    # Setzt das Passwort eines Benutzers in der Datenbank zurück
    hashed_password = hash_value(new_password)
    cypher_query = """
    MATCH (a:Nutzer {user_email: $user_email})
    SET a.passwort = $user_passwort
    """
    query_params = {
        "user_email": user_email,
        "user_passwort": hashed_password
    }
    try:
        with driver.session() as session:
            session.run(cypher_query, query_params)
            st.success("Passwort erfolgreich zurückgesetzt.")
    except Exception as e:
        st.error(f"Fehler beim Zurücksetzen des Passworts: {e}")

# Benutzer erstellen
def create_user(driver, user_vorname, user_nachname, user_email, user_password):
    # Erstellt einen neuen Benutzer in der Datenbank mit gehashtem Passwort
    registration_date = datetime.now().strftime("%Y-%m-%d")  # Für Berechnungen
    cypher_check_query = """
    MATCH (a:Nutzer {user_email: $user_email})
    RETURN a
    """
    cypher_create_query = """
    CREATE (a:Nutzer {
        vorname: $user_vorname,
        nachname: $user_nachname,
        user_email: $user_email,
        passwort: $user_passwort,
        rolle: 'User',
        registrierungsdatum: $registration_date
    })
    """
    query_params = {
        "user_vorname": user_vorname,
        "user_nachname": user_nachname,
        "user_email": user_email,
        "user_passwort": hash_value(user_password),
        "registration_date": registration_date
    }

    try:
        with driver.session() as session:
            result = session.run(cypher_check_query, {"user_email": user_email})
            if result.single():
                st.error("Ein Benutzer mit dieser E-Mail existiert bereits.")
            else:
                session.run(cypher_create_query, query_params)
                st.success("Benutzer erfolgreich erstellt.")
    except Exception as e:
        st.error(f"Fehler beim Erstellen des Benutzers: {e}")

# Berechnung der Mitgliedsdauer basierend auf dem Registrierungsdatum
def calculate_membership_duration(registration_date):
    # Berechnet, wie lange der Benutzer bereits registriert ist
    reg_date = datetime.strptime(registration_date, "%Y-%m-%d")
    current_date = datetime.now()
    delta = current_date - reg_date
    years = delta.days // 365
    months = (delta.days % 365) // 30
    return years, months

# Login und Registrierung
def login():
    # Zeigt das Login- und Registrierungsformular an
    if not st.session_state["logged_in"]:
        st.write("Wilkommen in der X")
        st.write("Bitte einloggen oder neuen Account erstellen")
        user_email = st.text_input("Nutzer E-Mail")
        user_password = st.text_input("Nutzer Passwort", type="password")

        if st.button("Login"):
            driver = call_client(neo4j_uri, neo4j_user, neo4j_password)
            if driver:
                authenticated, user_vorname = authenticate_user(driver, user_email, user_password)
                if authenticated:
                    # Setzt die Session States nach erfolgreichem Login
                    st.session_state["logged_in"] = True
                    st.session_state["user_email"] = user_email
                    st.session_state["user_vorname"] = user_vorname  # Vorname speichern
                    cypher_query = """
                    MATCH (a:Nutzer {user_email: $user_email})
                    RETURN a.registrierungsdatum AS registration_date, a.rolle AS user_role
                    """
                    query_params = {"user_email": user_email}
                    result = driver.session().run(cypher_query, query_params)
                    user = result.single()

                    if user:
                        registration_date = user["registration_date"]
                        role = user["user_role"]
                        years, months = calculate_membership_duration(registration_date)
                        st.session_state["registration_date"] = registration_date
                        st.session_state["membership_duration_years"] = years
                        st.session_state["membership_duration_months"] = months
                        st.session_state["role"] = role

                    st.rerun()  # App neu laden nach Login
                driver.close()

        st.write("---")
        st.write("Neuen Benutzer registrieren")
        reg_user_vorname = st.text_input("Vorname")
        reg_user_nachname = st.text_input("Nachname")
        reg_user_email = st.text_input("E-Mail")
        reg_user_password = st.text_input("Passwort", type="password")

        # Rolle automatisch festlegen: "Admin" nur für gasoo@hotmail.de, sonst "User"
        # role = "Admin" if reg_user_email == "gasoo@hotmail.de" else "User"

        if st.button("Benutzer registrieren"):
            if reg_user_vorname and reg_user_nachname and reg_user_email and reg_user_password:
                driver = call_client(neo4j_uri, neo4j_user, neo4j_password)
                if driver:
                    create_user(driver, reg_user_vorname, reg_user_nachname, reg_user_email, reg_user_password)
                    driver.close()
            else:
                st.error("Bitte alle Felder ausfüllen.")
    else:
        st.success(f"Sie sind eingeloggt als: {st.session_state['user_vorname']}")

# Hauptanwendung
def main_app():
    # Motivierende Nachricht
    st.success(f"Willkommen - schön, dass Du wieder hier bist, {st.session_state['user_vorname']}! Lass uns loslegen!")
    
    # Tabs mit personalisiertem Inhalt
    tab1, tab2, tab3, tab4 = st.tabs(["Einführung", "Meal-Generator", "Ernährungsplan", "Profil"])

    with tab1:
        st.write("Willkommen bei der App!")
    with tab2:
        st.write("Meal-Generator")
    with tab3:
        st.write(f"Ernährungsplan für {st.session_state['user_vorname']}")
    with tab4:
        # Registrierungsdatum in lesbarem Format anzeigen
        readable_registration_date = datetime.strptime(st.session_state["registration_date"], "%Y-%m-%d").strftime("%d. %B %Y")
        st.write(f"Profil von {st.session_state['user_vorname']}")
        st.write(f"Registrierungsdatum: {readable_registration_date}")
        st.write(f"Mitglied seit: {st.session_state['membership_duration_years']} Jahren und {st.session_state['membership_duration_months']} Monaten.")

# Startseite
def landing_page():
    # Startpunkt der App, der den Login und die Hauptanwendung verwaltet
    driver = call_client(neo4j_uri, neo4j_user, neo4j_password)
    if driver:
        driver.close()

    if not st.session_state["logged_in"]:
        login()
    else:
        main_app()

if __name__ == "__main__":
    landing_page()
