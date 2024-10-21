import streamlit as st
import os
from supabase import create_client, Client
import supabase
import neo4j
from neo4j import GraphDatabase


# Zugangsdaten aus den Secrets laden
stored_username = st.secrets["credentials"]["username"]
stored_password = st.secrets["credentials"]["password"]
neo4j_uri = st.secrets["credentials"]["uri"]  # URI der Neo4j-Datenbank


# Funktion zur Erstellung eines Neo4j-Clients
def call_client():
    uri = neo4j_uri
    username = stored_username
    password = stored_password
    
    try:
        # Verbindung mit der Neo4j-Datenbank herstellen
        driver = GraphDatabase.driver(uri, auth=(username, password))
        return driver
    except Exception as e:
        st.error(f"Keine Verbindung mit der Datenbank möglich: {str(e)}")
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
    # Hier die Hauptfunktionen der App hinzufügen

    st.tabs = tab1, tab2, tab3, tab4


    with tab1:
        # Hello you two sporty sexy people
        # Greetings and explenaiton of app

    with tab2:
        # Meal-Generator
        # Goal is for the meal decide how many gramms of each ingridient is for whom (Gabriel or Anita) -> we will cook the meal in the same pan but need to know how much gramms of the final meal is for whom in % or by tiping in the total weight of the meal and it calculates
        # Selection of all menues done by the two members Gabriel & Anita
        # Selection of all menues not done by the two


    with tab3:
        # Name: Gabriel
        # Set-Up for Gabriel and all data related

        # First Dropdown with menue facorite
        # col1 = breakfast, col2 = lunch, col3 = dinner

        # Snackdropdown

        # Then display all available food types and gramms to use of each meal-tipe (breakfast, snack, lunch, snack, dinner, snack)
        # possible to select the meal-typ and the main ingridient and then display possible meals
    

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
