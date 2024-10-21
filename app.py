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
