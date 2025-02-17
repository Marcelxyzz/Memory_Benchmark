import random
import time
import streamlit as st
from wonderwords import RandomWord
from registration_page import registration_page
from login_page import login_page
from registration_page import connect_to_mongo
from helpers import connect_to_collection


def reset_session():
    st.session_state.current_page = "Home"
    st.session_state.number_memory_score = 0
    st.session_state.number_memory_level = 1
    st.session_state.number_memory_timer = 3
    st.session_state.word_memory_score = 0
    st.session_state.word_memory_lives = 3
    st.session_state.word_memory_seen = []
    st.session_state.word_memory_word_list = []


if "current_page" not in st.session_state:
    reset_session()


def homescreen():
    st.image("https://wiltgenlab.faculty.ucdavis.edu/wp-content/uploads/sites/210/2017/04/brain-banner.jpg")
    st.markdown("<h1 style='text-align: center; color: white;'>Memory Benchmark</h1>", unsafe_allow_html=True)
    st.subheader("Put your memory through its paces")
    st.write(
        """
        Welcome to the Memory Benchmark app! This app is designed to test and improve your memory skills with engaging games.

        - Find out how many numbers you can remember in **🔢 Number Memory**
        - Identify repeated and new words in **🔠 Word Memory**.
        - Test your ability to recall sequences in **🔄 Simon Says**.


        Track your progress on the **📊 Statistics** page.
        Challenge your memory and have fun along the way!
        """
    )
    st.subheader("Navigation")
    st.write("Use the sidebar on the left to navigate through the app. Simply click on the page you want to land on!")
    st.subheader(
        "IMPORTANT: To use this app you have to create an account. Once registered/logged in you have to reload the app to create a new account or log in with a different account.")


def update_highscore_number(username, new_score):
    client = connect_to_mongo()
    collection = connect_to_collection("Streamlit", "user_registration_data")
    user_data = collection.find_one({"user_name": username}, {"_id": 0, "🔢 Highscore Number Memory": 1})
    old_highscore = user_data.get("🔢 Highscore Number Memory", 0)

    if new_score > old_highscore:
        collection.update_one({"user_name": username}, {"$set": {"🔢 Highscore Number Memory": new_score}})
        return True
    return False


def generate_number():
    st.session_state.current_number = "".join(
        [str(random.randint(0, 9)) for _ in range(st.session_state.number_memory_level)]
    )
    st.session_state.show_input = False  # Hide input


def start_new_round():
    generate_number()

    c1, c2, c3 = st.columns(3)
    with c2:
        placeholder = st.empty()
        placeholder.title(f"{st.session_state.current_number}")

    time.sleep(st.session_state.number_memory_timer)  # Show Number shorty
    placeholder.empty()  # Hide Number

    st.session_state.show_input = True  # Show input


# Number Memory Spiel
def number_memory():
    st.image(image="https://www.sparklebox.co.uk/wp-content/uploads/1-2049.jpg")
    st.markdown("<h1 style='text-align: center; color: white;'>🔢 Number Memory</h1>", unsafe_allow_html=True)
    if "username" not in st.session_state or not st.session_state.username:
        container = st.empty()
        with container.container():
            st.markdown(
                """
                <div class="fade-in" style="
                    text-align: center; 
                    font-size: 22px; 
                    color: white; 
                    background-color: #FF0000; 
                    padding: 15px; 
                    border-radius: 10px;
                    box-shadow: 2px 2px 10px rgba(0,0,0,0.2);">
                    🚨 Please login first!
                </div>
                """,
                unsafe_allow_html=True
            )
        return

    # Initialize variables
    if "current_number" not in st.session_state:
        st.session_state.current_number = None
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""
    if "number_memory_level" not in st.session_state:
        st.session_state.number_memory_level = 1
    if "number_memory_timer" not in st.session_state:
        st.session_state.number_memory_timer = 3
    if "show_input" not in st.session_state:
        st.session_state.show_input = False
    if "game_over" not in st.session_state:
        st.session_state.game_over = False
    if "new_highscore_number" not in st.session_state:
        st.session_state.new_highscore_number = False
    if "game_started" not in st.session_state:
        st.session_state.game_started = False

    # Start Button
    if not st.session_state.game_started:
        placeholder = st.empty()
        placeholder.write("🔹 Remember the number!")
        if st.button("Start Game 🚀"):
            placeholder.empty()
            st.session_state.game_started = True
            start_new_round()
            st.rerun()
        return

    st.header(f"**Level:** {st.session_state.number_memory_level}")

    # Game Over Screen
    if st.session_state.game_over:
        placeholder = st.empty()
        placeholder.error(f"❌ Game Over! You reached Level {st.session_state.number_memory_level}")
        if update_highscore_number(st.session_state.username, st.session_state.number_memory_level):
            st.session_state.new_highscore_number = True  # Neuer Rekord!
        if st.session_state.new_highscore_number:
            st.success("Congratulations! You reached a new Highscore! 🎉")
        time.sleep(2)
        # Reset game
        if st.button("Play Again"):
            placeholder.empty()
            st.session_state.number_memory_level = 1
            st.session_state.number_memory_timer = 3
            st.session_state.game_over = False
            st.session_state.game_started = False
            st.rerun()
        return

    if st.session_state.current_number is None:
        start_new_round()

    # Show input
    if st.session_state.show_input:
        placeholder = st.empty()
        user_input = placeholder.text_input("Enter the number:", key="user_input")

        if st.button("Submit"):
            placeholder.empty()
            if user_input == st.session_state.current_number:
                st.session_state.number_memory_level += 1
                st.session_state.number_memory_timer += 0.5  # Zeit verlängern
                start_new_round()
                st.rerun()
            else:
                st.session_state.game_over = True
                st.rerun()


# Update highscore for game in MongoDB
def update_highscore_word(username, new_score):
    client = connect_to_mongo()
    collection = connect_to_collection("Streamlit", "user_registration_data")

    user_data = collection.find_one({"user_name": username}, {"_id": 0, "🔢 Highscore Word Memory": 1})
    old_highscore = user_data.get("🔢 Highscore Word Memory", 0)

    if new_score > old_highscore:
        collection.update_one({"user_name": username}, {"$set": {"🔢 Highscore Word Memory": new_score}})
        return True
    return False


def word_memory():
    if "word_memory_started" not in st.session_state:
        st.session_state.word_memory_started = False

    if not st.session_state.word_memory_started:
        st.image(image="https://as2.ftcdn.net/jpg/01/42/89/99/1000_F_142899942_BJ9qtVpCEXdGpYHA9ZzhTTpBUY0ei6zj.jpg")
        st.markdown("<h1 style='text-align: center; color: white;'>🔠 Word Memory</h1>", unsafe_allow_html=True)

        # If not logged in the user is not able to play
        if "username" not in st.session_state or not st.session_state.username:
            container = st.empty()
            with container.container():
                st.markdown(
                    """
                    <div class="fade-in" style="
                        text-align: center; 
                        font-size: 22px; 
                        color: white; 
                        background-color: #FF0000; 
                        padding: 15px; 
                        border-radius: 10px;
                        box-shadow: 2px 2px 10px rgba(0,0,0,0.2);">
                        🚨 Please login first!
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            return

        placeholder = st.empty()
        placeholder.write("🔹 Have you **seen** this word before or is it **new**?")
        if st.button("Start Game 🚀"):
            placeholder.empty()
            st.session_state.word_memory_started = True
            st.rerun()
        return

    # Initialize variables
    if "word_memory_score" not in st.session_state:
        st.session_state.word_memory_score = 0
    if "word_memory_lives" not in st.session_state:
        st.session_state.word_memory_lives = 3
    if "word_memory_seen_words" not in st.session_state:
        st.session_state.word_memory_seen_words = []
    if "word_memory_current_word" not in st.session_state:
        st.session_state.word_memory_current_word = ""
    if "word_memory_word_pool" not in st.session_state:
        st.session_state.word_memory_word_pool = []
    if "new_highscore_word" not in st.session_state:
        st.session_state.new_highscore_word = False

    # Generate new random word
    def generate_word():
        if not st.session_state.word_memory_word_pool:
            rw = RandomWord()
            st.session_state.word_memory_word_pool = [rw.word() for _ in range(50)]
        return random.choice(st.session_state.word_memory_word_pool)

    # End Game when loosing all lives
    if st.session_state.word_memory_lives <= 0:
        st.title("You Lost!")
        placeholder = st.empty()
        placeholder.error(f"❌ Game Over! You final score: {st.session_state.word_memory_score}")
        if update_highscore_word(st.session_state.username, st.session_state.word_memory_score):
            st.session_state.new_highscore_word = True
        if st.session_state.new_highscore_word:
            st.success("Congratulations! You reached a new Highscore! 🎉")

        # Reset game to play again
        if st.button("Play Again"):
            placeholder.empty()
            st.session_state.word_memory_score = 0
            st.session_state.word_memory_lives = 3
            st.session_state.word_memory_seen_words = []
            st.session_state.word_memory_current_word = ""
            st.session_state.word_memory_word_pool = []
            st.session_state.new_highscore_word = False
            st.session_state.word_memory_started = False
            st.rerun()
        return

    # UI for Game
    st.image(image="https://as2.ftcdn.net/jpg/01/42/89/99/1000_F_142899942_BJ9qtVpCEXdGpYHA9ZzhTTpBUY0ei6zj.jpg")
    st.markdown("<h1 style='text-align: center; color: white;'>🔠 Word Memory</h1>", unsafe_allow_html=True)
    st.subheader(f"**Score:** {st.session_state.word_memory_score}")
    st.subheader(f"**Lives:** {st.session_state.word_memory_lives}")

    # Generate Word if there is none
    if not st.session_state.word_memory_current_word:
        st.session_state.word_memory_current_word = generate_word()

    # Show Word

    st.title(f"{st.session_state.word_memory_current_word}")

    # New and Seen Buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("New"):
            if st.session_state.word_memory_current_word in st.session_state.word_memory_seen_words:
                st.error("Wrong! This word has already been seen.")
                st.session_state.word_memory_lives -= 1
            else:
                st.success("Correct! New word added.")
                st.session_state.word_memory_seen_words.append(st.session_state.word_memory_current_word)
                st.session_state.word_memory_score += 1

            st.session_state.word_memory_current_word = generate_word()
            st.rerun()

    with col2:
        if st.button("Seen"):
            if st.session_state.word_memory_current_word in st.session_state.word_memory_seen_words:
                st.success("Correct! This word has already been seen.")
                st.session_state.word_memory_score += 1
            else:
                st.error("Wrong! This word has not been seen before.")
                st.session_state.word_memory_lives -= 1

            st.session_state.word_memory_current_word = generate_word()
            st.rerun()


def update_highscore_simon(username, new_score):
    client = connect_to_mongo()
    collection = connect_to_collection("Streamlit", "user_registration_data")

    user_data = collection.find_one({"user_name": username}, {"_id": 0, "🔄 Highscore Simon Says": 1})
    old_highscore = user_data.get("🔄 Highscore Simon Says", 0)

    if new_score > old_highscore:
        collection.update_one({"user_name": username}, {"$set": {"🔄 Highscore Simon Says": new_score}})
        return True
    return False


def simon_says():
    if "sequence" not in st.session_state:
        st.session_state.sequence = []
    if "user_input2" not in st.session_state:
        st.session_state.user_input2 = []
    if "level" not in st.session_state:
        st.session_state.level = 0
    if "game_over2" not in st.session_state:
        st.session_state.game_over2 = False
    if "show_pattern" not in st.session_state:
        st.session_state.show_pattern = False
    if "game_started2" not in st.session_state:
        st.session_state.game_started2 = False
    if "new_highscore_sequence" not in st.session_state:
        st.session_state.new_highscore_sequence = False

    buttons = ["🔴", "🟢", "🔵", "🟡"]

    def start_game():
        st.session_state.sequence = []
        st.session_state.user_input2 = []
        st.session_state.level = 1
        st.session_state.game_over2 = False
        st.session_state.game_started2 = True
        add_new_step()
        show_pattern()

    def add_new_step():
        st.session_state.sequence.append(random.choice(buttons))

    def show_pattern():
        st.session_state.show_pattern = True
        st.write("🧠 Memorize the pattern!")

        for button in st.session_state.sequence:
            st.write(f"**{button}**")
            time.sleep(1)

        st.session_state.show_pattern = False  # Allow input

    # Check if user input is correct
    def check_input(choice):
        st.session_state.user_input2.append(choice)

        index = len(st.session_state.user_input2) - 1
        if st.session_state.user_input2[index] != st.session_state.sequence[index]:
            st.session_state.game_over2 = True
        elif len(st.session_state.user_input) == len(st.session_state.sequence):
            st.success("✅ Correct! Next level...")
            time.sleep(1)
            st.session_state.level += 1
            st.session_state.user_input2 = []
            add_new_step()
            show_pattern()
            st.rerun()

    # Streamlit UI

    st.image(image="https://m.media-amazon.com/images/I/71CFNeOUB3L.png")
    st.markdown("<h1 style='text-align: center; color: white;'>🔄 Simon says</h1>", unsafe_allow_html=True)

    if "username" not in st.session_state or not st.session_state.username:
        container = st.empty()
        with container.container():
            st.markdown(
                """
                <div class="fade-in" style="
                    text-align: center; 
                    font-size: 22px; 
                    color: white; 
                    background-color: #FF0000; 
                    padding: 15px; 
                    border-radius: 10px;
                    box-shadow: 2px 2px 10px rgba(0,0,0,0.2);">
                    🚨 Please login first!
                </div>
                """,
                unsafe_allow_html=True
            )
        return

    if not st.session_state.game_started2:
        placeholder = st.empty()
        placeholder.write("🔹 Remember the sequence of colors!")
        if st.button("Start Game 🚀"):
            placeholder.empty()
            start_game()
            st.rerun()
    else:
        st.write(f"**Level: {st.session_state.level}**")

        if st.session_state.game_over2:
            st.error("❌ Game Over! You made a mistake.")
            if update_highscore_simon(st.session_state.username, st.session_state.level):
                st.session_state.new_highscore_sequence = True
            if st.session_state.new_highscore_sequence:
                st.success("Congratulations! You reached a new Highscore! 🎉")
            if st.button("Try Again"):
                start_game()
                st.rerun()
        elif not st.session_state.show_pattern:
            st.write("🔹 Repeat the sequence:")
            cols = st.columns(4)
            for i, button in enumerate(buttons):
                with cols[i]:
                    if st.button(button):
                        check_input(button)
                        st.rerun()


def get_user_data(username):
    return st.session_state.collection.find_one({"username": st.session_state.username})


def stats():
    st.image(image="https://www.rak4cloud.com/upload/analytics_pic2.jpg")
    st.markdown("<h1 style='text-align: center; color: white;'>📊 Statistics</h1>", unsafe_allow_html=True)

    def get_user_data(username):
        client = connect_to_mongo()
        collection = connect_to_collection("Streamlit", "user_registration_data")
        return collection.find_one({"user_name": username},
                                   {"_id": 0, "password": 0, "user_name": 0})  # hide id and password

    # Check if user is logged in yet
    if "username" not in st.session_state or not st.session_state.username:
        container = st.empty()
        with container.container():
            st.markdown(
                """
                <div class="fade-in" style="
                    text-align: center; 
                    font-size: 22px; 
                    color: white; 
                    background-color: #FF0000; 
                    padding: 15px; 
                    border-radius: 10px;
                    box-shadow: 2px 2px 10px rgba(0,0,0,0.2);">
                    🚨 Please login first!
                </div>
                """,
                unsafe_allow_html=True
            )
        return
    else:
        user_data = get_user_data(st.session_state.username)

        if user_data:
            st.success(f"🎉 Welcome, {st.session_state.username}!")
            st.json(user_data)  # Shoes MongoDB document of the user
        else:
            st.error("Error: Your Account couldn't be found.")


if "options" not in st.session_state:
    st.session_state.options = ""

if "registered" not in st.session_state:
    st.session_state.registered = False

if st.session_state.registered and "Register" in st.session_state.options:
    st.session_state.options.remove("Register")

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/5431/5431045.png",
                 use_container_width=True)
st.sidebar.title("Navigation")
st.sidebar.markdown("---")

if "is_registered" not in st.session_state:
    st.session_state.is_registered = False

if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False

st.session_state.options = ["🏠 Home", "🔢 Number Memory", "🔠 Word Memory", "🔄 Simon Says",
                            "📊 Statistics"]

# Only show "Register" page in sidebar, when User not registered yet
if not st.session_state.is_registered:
    st.session_state.options.insert(1, "➕ Registration")

# Only show "Login" page in sidebar, when User not registered yet
if not st.session_state.is_logged_in:
    st.session_state.options.insert(1, "🔑 Login")

# Sidebar Navigation
page_selection = st.sidebar.radio("Choose", st.session_state.options)

# pages
if page_selection == "🏠 Home":
    homescreen()
elif page_selection == "🔑 Login":
    login_page()
elif page_selection == "➕ Registration":
    registration_page()
elif page_selection == "🔢 Number Memory":
    number_memory()
elif page_selection == "🔠 Word Memory":
    word_memory()
elif page_selection == "🔄 Simon Says":
    simon_says()
elif page_selection == "📊 Statistics":
    stats()
