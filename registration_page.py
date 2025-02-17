import streamlit as st
from pymongo.mongo_client import MongoClient
import random
import time

if "collection" not in st.session_state:
    st.session_state.collection = ""


def connect_to_mongo():
    user = st.secrets["username"]
    db_password = st.secrets["password"]

    # This is our database connection string, for a cluster called tb-ii
    uri = f"mongodb+srv://{user}:{db_password}@tb2.yubsq.mongodb.net/?retryWrites=true&w=majority&appName=TB2"

    # Let's connect to our MongoClient
    client = MongoClient(uri)

    return client


usernames = []

if "username" not in st.session_state:
    st.session_state.username = ""


def registration_page():
    st.title("➕ REGISTRATION")
    placeholder = st.empty()

    with placeholder.form("USER DATA"):
        st.write("Hello! Please enter your information to register.")
        st.session_state.username = st.text_input("Username")
        password = st.text_input("Choose a password", type="password")
        password2 = st.text_input("Repeat password", type="password")
        submit_button = st.form_submit_button("Submit")

    if submit_button:
        if len(password) < 8:
            st.error("Password needs at least 8 characters", icon="🚨")
        elif len(st.session_state.username) < 1:
            st.error("Username needs at least 1 character", icon="🚨")
        elif password != password2:
            st.error("Passwords do not match", icon="🚨")
        else:
            client = connect_to_mongo()

            db = client["Streamlit"]
            st.session_state.collection = db["user_registration_data"]

            document = {f"user_name": st.session_state.username,
                        "password": password,
                        }

            st.session_state.collection.insert_one(document)

            placeholder.empty()

            registration_success()


QUOTES = [
    "Welcome aboard! The journey to greatness begins now. 🚀",
    "Your adventure starts here. Make it legendary! ✨",
    "You've joined an elite group of memory masters! 🧠",
    "Small steps lead to big achievements. Let's go! 🔥",
    "Memory is the key to knowledge. Unlock your potential! 🔑"
]


def registration_success():
    st.markdown(
        """
        <style>
        .big-text {
            font-size: 40px;
            text-align: center;
            font-weight: bold;
            color: #4CAF50;
        }
        .sub-text {
            font-size: 20px;
            text-align: center;
            color: #FFFFFF;
        }
        .animated {
            animation: fadeIn 2s ease-in-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Headline
    st.markdown('<p class="big-text animated">🎉 Registration Successful! 🎉</p>', unsafe_allow_html=True)

    # Zufälliges Zitat
    quote = random.choice(QUOTES)
    st.markdown(f'<p class="sub-text animated">"{quote}"</p>', unsafe_allow_html=True)

    # Animationseffekt
    with st.spinner("Setting up your profile..."):
        time.sleep(2)

    st.success("You're all set! Start exploring now. 🚀")

    # Weiter-Button
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    start_button = st.button("Start Now ➡️")
    st.markdown('</div>', unsafe_allow_html=True)
    st.session_state.is_registered = True  # Nutzer als registriert markieren
    st.session_state.is_logged_in = True
    if start_button:
        st.session_state.options = "🏠 Home"
        st.rerun()
