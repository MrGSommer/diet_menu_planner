import streamlit as st
from neo4j import GraphDatabase
from passlib.context import CryptContext

# Zugangsdaten für Neo4j (Admin-Daten)
neo4j_uri = st.secrets["credentials"]["AURA_NEO4J_URI"]
neo4j_user = st.secrets["credentials"]["AURA_NEO4J_USERNAME"]
neo4j_password = st.secrets["credentials"]["AURA_NEO4J_PASSWORD"]

# CryptContext erstellen
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Initialisierung von session_states
if 'connection_type' not in st.session_state:
    st.session_state['connection_type'] = 'Aura'

if 'logged_in' not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["role"] = None
    st.session_state["user_email"] = None

# Neo4j driver
def call_client(uri, user, password):
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        return driver
    except Exception as e:
        st.error(f"Error connecting to Neo4j: {e}")
        return None

# Funktion zur Überprüfung von Schreib- und Leserechten
def check_database_permissions(driver):
    """Prüft, ob die Verbindung Schreib- und Leserechte auf der Neo4j-Datenbank hat."""
    try:
        with driver.session() as session:
            # Test-Leseabfrage
            session.run("MATCH (n) RETURN n LIMIT 1")

            # Test-Schreibabfrage (erstellt und löscht temporär einen Knoten)
            session.run("CREATE (t:TestNode {test: 'test'})")
            session.run("MATCH (t:TestNode {test: 'test'}) DELETE t")

            st.info("Schreib- und Leserechte auf der Neo4j-Datenbank sind vorhanden.")
    except Exception as e:
        st.warning(f"Fehler bei der Prüfung der Schreib- und Leserechte: {e}")

# Authenticate user using platform login data (e.g., diet tool)
def authenticate_user(driver, user_email, user_password):
    """Authentifiziert einen Benutzer, indem die Daten aus Neo4j für das Diet-Tool abgerufen und das Passwort geprüft wird."""
    cypher_query = """
    MATCH (a:Nutzer {user_email: $user_email})
    RETURN a.passwort AS user_passwort, a.rolle AS user_role, a.vorname AS user_vorname
    """
    query_params = {"user_email": user_email}
    try:
        with driver.session() as session:
            result = session.run(cypher_query, query_params)
            user = result.single()
            # Passwort mit passlib verifizieren
            if user and pwd_context.verify(user_password, user["user_passwort"]):
                st.success("Benutzer erfolgreich authentifiziert.")
                return True, user["user_role"], user["user_vorname"]
            else:
                st.error("Falsches Passwort.")
                return False, None, None
    except Exception as e:
        st.error(f"Fehler bei der Authentifizierung: {e}")
        return False, None, None


# Funktion für das Login- und Registrierungsformular und Überprüfung
def login():
    """Zeigt das Login-Formular an und verarbeitet die Eingaben. Ermöglicht die Erstellung eines neuen Benutzers."""
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    # Wenn nicht eingeloggt, Login-Formular anzeigen
    if not st.session_state["logged_in"]:
        st.write("Bitte einloggen oder neuen Account erstellen")
        user_email = st.text_input("E-Mail / Nutzername")
        user_password = st.text_input("Password", type="password")

        # Login-Button
        if st.button("Login"):
            # Verbindung zur Neo4j-Datenbank herstellen
            driver = call_client(neo4j_uri, neo4j_user, neo4j_password)
            if driver:
                authenticated, role, vorname = authenticate_user(driver, user_email, user_password)
                if authenticated:
                    st.session_state["logged_in"] = True
                    st.session_state["user_email"] = user_email
                    st.session_state["role"] = role
                    st.success(f"Willkommen, {vorname}!")
                else:
                    st.error("Falsches E-Mail oder Passwort. Bitte versuchen Sie es erneut.")
                driver.close()

        # Benutzer erstellen - Registrierungsformular
        st.write("---")
        st.write("Neuen Benutzer registrieren")
        reg_user_vorname = st.text_input("Vorname")
        reg_user_nachname = st.text_input("Nachname")
        reg_user_email = st.text_input("E-Mail")
        reg_user_password = st.text_input("Passwort", type="password")

        # Rolle automatisch festlegen: "Admin" nur für gasoo@hotmail.de, sonst "User"
        role = "Admin" if reg_user_email == "gasoo@hotmail.de" else "User"

        if st.button("Benutzer registrieren"):
            if reg_user_vorname and reg_user_nachname and reg_user_email and reg_user_password:
                # Verbindung zur Neo4j-Datenbank herstellen
                driver = call_client(neo4j_uri, neo4j_user, neo4j_password)
                if driver:
                    create_user(driver, reg_user_vorname, reg_user_nachname, reg_user_email, reg_user_password, role)
                    st.success(f"Benutzer {reg_user_vorname} erfolgreich als {role} registriert.")
                    driver.close()
            else:
                st.error("Bitte alle Felder ausfüllen, um einen Benutzer zu registrieren.")
    else:
        st.success(f"Sie sind eingeloggt als: {st.session_state['user_email']}")


# Reset password
def reset_password(driver, user_email, new_password):
    """Setzt das Passwort für einen Benutzer in Neo4j zurück."""
    # Neues Passwort hashen mit passlib
    hashed_password = pwd_context.hash(new_password)
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


# Create user (Admin function)
def create_user(driver, user_vorname, user_nachname, user_email, user_password, user_role):
    """Erstellt einen neuen Benutzer in der Neo4j-Datenbank."""
    if not check_role("admin"):
        return
    # Passwort hashen mit passlib
    hashed_password = pwd_context.hash(user_password)
    cypher_query = """
    CREATE (a:Nutzer {
        vorname: $user_vorname,
        nachname: $user_nachname,
        user_email: $user_email,
        passwort: $user_passwort,
        rolle: $user_role
    })
    """
    query_params = {
        "user_vorname": user_vorname,
        "user_nachname": user_nachname,
        "user_email": user_email,
        "user_passwort": hashed_password,
        "user_role": user_role
    }
    try:
        with driver.session() as session:
            session.run(cypher_query, query_params)
            st.success("Benutzer erfolgreich erstellt.")
    except Exception as e:
        st.error(f"Fehler beim Erstellen des Benutzers: {e}")


def check_role(role):
    """Prüft, ob der eingeloggte Benutzer die entsprechende Rolle hat."""
    if st.session_state.get("role") != role:
        st.warning(f"Diese Aktion ist nur für {role}s verfügbar.")
        return False
    return True

# Hauptanwendung der App
def main_app():
    """Die Hauptfunktionalität der App, sichtbar nach erfolgreichem Login."""
    st.success(f"Sie sind eingeloggt als: {st.session_state['username']}")

    # Tabs für verschiedene Bereiche der App
    tab1, tab2, tab3, tab4 = st.tabs(["Begrüßung", "Meal-Generator", "Gabriel's Daten", "Anita's Daten"])

    # Tab 1: Begrüßung und Einführung
    with tab1:
        st.write("Willkommen, Gabriel und Anita!")
        st.write("Hier könnt ihr eure Mahlzeiten verwalten und personalisierte Gerichte erstellen.")

    # Tab 2: Meal-Generator
    with tab2:
        st.write("Meal-Generator")
        st.write("Ziel: Für das Gericht entscheiden, wie viele Gramm jeder (Gabriel oder Anita) bekommt.")
        st.write("Ihr könnt das Gesamtgewicht des Essens eingeben und es berechnet, wie viel Gramm für wen ist.")
        st.write("Auswahl der Menüs, die von Gabriel & Anita erstellt wurden:")
        st.write("...")

    # Tab 3: Gabriel's Daten
    with tab3:
        st.write("Name: Gabriel")
        st.write("Setup für Gabriel und alle dazugehörigen Daten")
        st.write("Lieblingsmenü:")
        st.write("Dropdown mit Auswahl für Frühstück, Mittagessen, Abendessen")
        st.write("Snack-Dropdown:")
        st.write("Alle verfügbaren Lebensmittel anzeigen, sortiert nach Mahlzeitentyp.")
        st.write("...")

    # Tab 4: Anita's Daten
    with tab4:
        st.write("Name: Anita")
        st.write("Setup für Anita und alle dazugehörigen Daten")
        st.write("...")

# In der landing_page die Prüfung zu Beginn einfügen
def landing_page():
    """Startpunkt der App, stellt sicher, dass der Nutzer eingeloggt ist, bevor die Hauptanwendung geladen wird."""
    driver = call_client(neo4j_uri, neo4j_user, neo4j_password)
    if driver:
        check_database_permissions(driver)
        driver.close()

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        login()
    else:
        main_app()

if __name__ == "__main__":
    landing_page()
