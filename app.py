import streamlit as st
import os
from supabase import create_client, Client
import supabase
import neo4j
from neo4j import GraphDatabase
import bcrypt



# Zugangsdaten aus den Secrets laden
stored_username = st.secrets["credentials"]["username"]
stored_password = st.secrets["credentials"]["password"]
neo4j_uri = st.secrets["credentials"]["AURA_NEO4J_URI"]  # URI der Neo4j-Datenbank


# Neo4j driver
def call_client(uri, user, password):
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        return driver
    except Exception as e:
        st.error(f"Error connecting to Neo4j: {e}")
        return None


# Funktion zum Testen von Schreib- und Löschoperationen
def test_write_read_delete():
    driver = call_client()
    
    if driver:
        try:
            with driver.session() as session:
                # 1. Schreiben: Ein Beispielknoten erstellen
                session.run("CREATE (n:TestNode {name: 'StreamlitTest'})")
                st.write("Knoten erstellt.")

                # 2. Lesen: Den Knoten abfragen
                result = session.run("MATCH (n:TestNode {name: 'StreamlitTest'}) RETURN n")
                nodes = [record["n"] for record in result]
                
                if nodes:
                    st.write("Knoten gelesen:", nodes)
                else:
                    st.error("Fehler beim Lesen des Knotens.")

                # 3. Löschen: Den Knoten entfernen
                session.run("MATCH (n:TestNode {name: 'StreamlitTest'}) DETACH DELETE n")
                st.write("Knoten gelöscht.")

                # Erfolgreicher Abschluss, Schreibrechte vorhanden
                st.session_state["write_test_successful"] = True
                st.success("Schreibrechte vorhanden.")
        except Exception as e:
            st.error(f"Fehler bei der Testabfrage: {str(e)}")
        finally:
            driver.close()

# Button zur Auslösung des Tests
if st.button("Test Schreibrechte"):
    test_write_read_delete()

# Ausgabe des Session-Status
if "write_test_successful" in st.session_state and st.session_state["write_test_successful"]:
    st.write("Schreibrechte erfolgreich getestet.")

# Create user (Admin function)
def create_user(driver, vorname, nachname, username, password, role):
    if not check_role("admin"):
        return
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cypher_query = """
    CREATE (a:Nutzer {
        vorname: $vorname,
        nachname: $nachname,
        username: $username,
        passwort: $passwort,
        rolle: $rolle
    })
    """
    query_params = {
        "vorname": vorname,
        "nachname": nachname,
        "username": username,
        "passwort": hashed_password.decode('utf-8'),
        "rolle": role
    }
    try:
        with driver.session() as session:
            session.run(cypher_query, query_params)
            st.success("Benutzer erfolgreich erstellt.")
    except Exception as e:
        st.error(f"Fehler beim Erstellen des Benutzers: {e}")

def forgot_passwort(driver, username, role):
    # hilft das passwort neu zu erstellen
    # zeigt das neue passwort mit sucsess an und schreibt es in die datenbank mit hash
    # nur wenn role ist admin funktion offen mit tab(Admin)


# Funktion für das Login-Formular und Überprüfung
def login():
    """Zeigt das Login-Formular an und verarbeitet die Eingaben."""
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    # Wenn nicht eingeloggt, Login-Formular anzeigen
    if not st.session_state["logged_in"]:
        st.write("Bitte einloggen")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username == stored_username and password == stored_password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success(f"Willkommen, {username}!")
            else:
                st.error("Falscher Username oder Passwort. Wenden Sie sich an Ihren Systemadministrator.")
    else:
        st.success(f"Sie sind eingeloggt als: {st.session_state['username']}")
        
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

# Ausführen der App
def landing_page():
    """Startpunkt der App, stellt sicher, dass der Nutzer eingeloggt ist, bevor die Hauptanwendung geladen wird."""
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        login()
    else:
        main_app()

if __name__ == "__main__":
    landing_page()
