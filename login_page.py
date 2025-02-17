import streamlit as st
from pymongo.mongo_client import MongoClient
import pandas as pd
from helpers import connect_to_collection
import time

if "username" not in st.session_state:
    st.session_state.username = ""


def connect_to_mongo():
    user = st.secrets["username"]
    db_password = st.secrets["password"]

    # This is our database connection string, for a cluster called tb-ii
    uri = f"mongodb+srv://{user}:{db_password}@tb2.yubsq.mongodb.net/?retryWrites=true&w=majority&appName=TB2"

    # Let's connect to our MongoClient
    client = MongoClient(uri)

    return client


def login_page():
    st.title("🔑 LOGIN")
    placeholder = st.empty()

    with placeholder.form("LOGIN"):
        st.write("Hello! Please enter your log info.")
        st.write("If this is your first time on my app then please go to the Registration Page.")
        st.session_state.username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")

    if login_button:
        connect_to_mongo()
        # connect to collection
        # define the database
        db_name = 'Streamlit'
        # define the collection
        collection_name = 'user_registration_data'
        collection = connect_to_collection(db_name, collection_name)

        # check username
        # read the data from the collection and identify user names
        user_registration_data = pd.DataFrame(list(collection.find()))
        user_names = list(user_registration_data.user_name)

        # check password
        if st.session_state.username in user_names:
            # this selects the password of the user that is entering information
            registered_password = \
                list(user_registration_data[user_registration_data.user_name == st.session_state.username].password)[0]

            if password == registered_password:
                credentials_check = True
                placeholder.empty()
                with st.spinner("Fetching Data..."):
                    time.sleep(3)
                login_success(st.session_state.username)
            else:
                st.error("The username/password is not correct")
        else:
            st.error("Please provide correct user name or click on register as new user")


def login_success(username):
    st.markdown(
        """
        <style>
            @keyframes fadeIn {
                from {opacity: 0;}
                to {opacity: 1;}
            }
            .fade-in {
                animation: fadeIn 1.5s ease-in-out;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    container = st.empty()

    with container.container():
        st.markdown(f"<h1 class='fade-in' style='text-align: center;'>🎉 Welcome back, {username}!</h1>",
                    unsafe_allow_html=True)
        time.sleep(0.5)

        st.markdown(
            """
            <div class="fade-in" style="
                text-align: center; 
                font-size: 22px; 
                color: white; 
                background-color: #4CAF50; 
                padding: 15px; 
                border-radius: 10px;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.2);">
                ✅ Login successful!
            </div>
            """,
            unsafe_allow_html=True
        )
        time.sleep(0.8)

    st.session_state.is_registered = True
    st.session_state.is_logged_in = True
    start_button = st.button("Go to Homepage 🚀")
    if start_button:
        st.session_state.options = "🏠 Home"
        st.rerun()
