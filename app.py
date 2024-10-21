import streamlit as st
import os
from supabase import create_client, Client
import supabase



# Zugangsdaten aus den Secrets laden
stored_username = st.secrets["credentials"]["username"]
stored_password = st.secrets["credentials"]["password"]


def call_client():
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    
    if url and key:
        supabase: Client = create_client(url, key)
    else:
        st.error("Keine Verbindung mit der Datenbank möglich. Prüfen Sie die Credentials")


def fetch_table(table_name):
    response = supabase.table(f"{table_name}").select("*").execute()

    if response:
        return response
    else:
        st.error("Keine Daten gefunden")



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
