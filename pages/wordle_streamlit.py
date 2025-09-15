import streamlit as st
import random


#region Useful functions
def is_plausible_word(word, known_present_letters, known_absent_letters, known_absent_letters_in_positions, my_word):
    check_1 = all([True if letter in word else False for letter in known_present_letters])
    for letter in known_present_letters:
        occurrence = known_present_letters[letter]
        if type(occurrence) == str:
            occurrence = int(occurrence)
            if word.count(letter) != occurrence:
                return False
        else:
            if word.count(letter) < occurrence:
                return False
    check_2 = all([True if letter not in known_absent_letters else False for letter in word])
    check_3 = all([True if word[i] not in known_absent_letters_in_positions[i] else False for i in range(5)])
    check_4 = all([True if my_word[i] is None or my_word[i] == word[i] else False for i in range(5)])
    return check_1 and check_2 and check_3 and check_4


def information_value(word, known_present_letters, known_absent_letters):
    value = len(set(word).difference(set(known_present_letters.keys()).union(set(known_absent_letters))))
    return value
#endregion Useful functions

#region Store all 5-letter words and pick a target word for the game
with open("pages/words_for_wordle.txt", "r") as f:
    all_words = [line.strip().upper() for line in f if len(line.strip()) == 5]

word_length = 5
#endregion

#region Collect information variables
# known_present_letters = {} # value = letter occurence (if value is a string, letter occurence is exact)
# known_absent_letters = []
# known_absent_letters_in_positions = {0: set(), 1: set(), 2: set(), 3: set(), 4: set()}
# my_word = [None, None, None, None, None]
# possible_solutions = all_words.copy()

if "known_present_letters" not in st.session_state:
    st.session_state.known_present_letters = {} # value = letter occurence (if value is a string, letter occurence is exact)
if "known_absent_letters" not in st.session_state:
    st.session_state.known_absent_letters = []
if "known_absent_letters_in_positions" not in st.session_state:
    st.session_state.known_absent_letters_in_positions = {i: set() for i in range(5)}
if "my_word" not in st.session_state:
    st.session_state.my_word = [None] * 5
if "possible_solutions" not in st.session_state:
    st.session_state.possible_solutions = all_words.copy()

#endregion

#region Define strategy function
def suggest_word(n, possible_solutions, known_present_letters, known_absent_letters, try_1=None):
    # global possible_solutions
    print(f"---> known_present_letters:{known_present_letters}")
    if try_1 is None:
        if n == 1: # Strategy 1: guess a random word from the all words
            try_1 = random.choice(all_words)
        
        elif n == 2: # Strategy 2: guess a random word from the possible words
            try_1 = random.choice(possible_solutions)
        
        elif n == 3: # Strategy 3: guess a word that is possible and provides information according to letter variety
            print(f"---> len(possible_solutions):{len(possible_solutions)}")
            possible_solutions_with_information = {}
            for word in possible_solutions:
                value = information_value(word, known_present_letters, known_absent_letters)
                if value not in possible_solutions_with_information:
                    possible_solutions_with_information[value] = []
                possible_solutions_with_information[value].append(word)
            max_value = max(possible_solutions_with_information.keys())
            try_1 = random.choice(possible_solutions_with_information[max_value])

        elif n == 4: # Strategy 4: guess a word that provides as much information (not necessarily possible) according to letter variety
            words_with_information = {}
            for word in all_words:
                value = information_value(word, known_present_letters, known_absent_letters)
                if value not in words_with_information:
                    words_with_information[value] = []
                words_with_information[value].append(word)
            max_value = max(words_with_information.keys())
            try_1 = random.choice(words_with_information[max_value])

        elif n == 5: # Strategy 5: guess a word that provides as much information based on letter variety and letter appearance probability (from the possible words)
            pass

        elif n == 6: # Strategy 5: guess a word that provides as much information based on letter variety and letter appearance probability (from all words)
            pass
    return try_1

def store_feedback_information(try_1, feedback_1, known_present_letters, known_absent_letters, known_absent_letters_in_positions, my_word, possible_solutions):
    # global possible_solutions
    # Store feedback information into collected information variables
    for i in range(word_length):
        if feedback_1[i] == "Green" and my_word[i] is None: # i.e. correctly positioned
            my_word[i] = try_1[i]
            print("HEY 1")
        elif feedback_1[i] == "Green" and my_word[i] is not None and my_word[i] != try_1[i]: # i.e. two correctly positioned letters interfering
            my_word[i] = "?"
            print("HEY 2")
        if feedback_1[i] == "Orange" and my_word[i] is None: # i.e. present but incorrectly positioned
            known_absent_letters_in_positions[i].add(try_1[i])
        if feedback_1[i] in ["Orange", "Green"]: # i.e. present inside target word
            if type(known_present_letters.get(try_1[i])) != str: # i.e. occurrence is not yet known
                occurrence_in_target = len([True for j in range(word_length) if feedback_1[j] in ["Orange", "Green"] and try_1[j] == try_1[i]])
                occurrence_black_in_target = len([True for j in range(word_length) if feedback_1[j] == "Black" and try_1[j] == try_1[i]])
                if occurrence_black_in_target == 0:
                    if known_present_letters.get(try_1[i]) is None:
                        known_present_letters[try_1[i]] = occurrence_in_target
                    else:
                        known_present_letters[try_1[i]] = max(known_present_letters[try_1[i]], occurrence_in_target)
                else:
                    known_present_letters[try_1[i]] = str(occurrence_in_target)
        elif feedback_1[i] == "Black" and try_1[i] not in known_absent_letters: # i.e. not present (unless occurrence in try is greater than 1)
            occurrence_in_try = try_1.count(try_1[i])
            if occurrence_in_try == 1:
                known_absent_letters.append(try_1[i])
            else:
                if type(known_present_letters.get(try_1[i])) != str: # i.e. occurrence is not yet known
                    occurrence_in_target = len([True for j in range(word_length) if feedback_1[j] in ["Orange", "Green"] and try_1[j] == try_1[i]])
                    if occurrence_in_target == 0:
                        known_absent_letters.append(try_1[i])
                    else:
                        known_present_letters[try_1[i]] = str(occurrence_in_target)
    st.session_state.possible_solutions = [word for word in st.session_state.possible_solutions if is_plausible_word(word, known_present_letters, known_absent_letters, known_absent_letters_in_positions, my_word)]
    # possible_solutions = [word for word in possible_solutions if is_plausible_word(word, known_present_letters, known_absent_letters, known_absent_letters_in_positions, my_word)]
    
    print(f"func2: ---> len(possible_solutions): {len(possible_solutions)}")

#endregion



st.set_page_config(page_title="Wordle Solver", layout="centered")
st.title("Wordle Solver")

# --- User-selectable strategy settings ---
st.markdown("### Strategy Settings")
strategy_n = st.selectbox("Choose strategy (1–4):", [1, 2, 3, 4], index=2, key="strategy_n")

# ---- CHANGED BLOCK: Safely reset the input BEFORE rendering it ----
# Handle custom input reset before rendering
if "custom_word" not in st.session_state:
    st.session_state.custom_word = ""

# If reset flag is on, clear the value and disable the key for one render
if st.session_state.get("reset_custom_word", False):
    custom_value = ""
    st.session_state["reset_custom_word"] = False  # Reset the flag
else:
    custom_value = st.session_state.get("custom_word", "")

# Always use a consistent key and control the input via value=
custom = st.text_input("Or enter a custom 5-letter word (optional):", 
                       key="custom_word", value=custom_value)


# Layout with two columns: main content and sidebar info panel
main_col, info_col = st.columns([3, 1])

# Initialize toggle state
if "show_info_panel" not in st.session_state:
    st.session_state.show_info_panel = False

# Define toggle behavior
def toggle_info():
    st.session_state.show_info_panel = not st.session_state.show_info_panel


with info_col:
    button_label = "📊 Hide Info Variables" if st.session_state.show_info_panel else "📊 Show Info Variables"
    st.button(button_label, on_click=toggle_info)

    if st.session_state.show_info_panel:
        with info_col:
            st.markdown("### ℹ️ Info Variables")

            st.markdown("**✅ Known Present Letters**")
            if st.session_state.known_present_letters:
                st.json(st.session_state.known_present_letters)
            else:
                st.write("None")

            st.markdown("**❌ Known Absent Letters**")
            if st.session_state.known_absent_letters:
                st.write(", ".join(st.session_state.known_absent_letters))
            else:
                st.write("None")

            st.markdown("**🚫 Letters Not in Positions**")
            formatted_positions = {
                str(k): list(v) for k, v in st.session_state.known_absent_letters_in_positions.items()
            }
            st.json(formatted_positions)

            st.markdown("**📌 Confirmed Positions (my_word)**")
            formatted_word = [l if l is not None else "_" for l in st.session_state.my_word]
            st.write(" ".join(formatted_word))

            st.markdown("**🔍 Possible Solutions**")
            st.write(f"Count: {len(st.session_state.possible_solutions)}")

            if st.session_state.possible_solutions:
                st.dataframe({"Word": st.session_state.possible_solutions})


with main_col:
    # Dummy word suggestions (looping); replace with your real logic
    # fixed_suggestions = ["APPLE", "PROUD", "THING", "CRANE", "BLAST", "MIGHT", "SWEET", "TRUCK"]

    # Initialize app state
    if "guesses" not in st.session_state:
        st.session_state.guesses = []  # Each: {"word", "colors", "locked", "feedback_given", "suggestion_made"}

    def add_new_guess():
        # index = len(st.session_state.guesses)
        # word = fixed_suggestions[index % len(fixed_suggestions)]
        n = strategy_n
        custom = st.session_state.get("custom_word", "").strip().upper()
        try_1 = custom if len(custom) == 5 and custom.isalpha() else None
        word = suggest_word(n, st.session_state.possible_solutions, st.session_state.known_present_letters, st.session_state.known_absent_letters, try_1)
        st.session_state.guesses.append({
            "word": word,
            "colors": [0] * 5,
            "locked": False,
            "feedback_given": False,
            "suggestion_made": False
        })

    # Show "Suggest Word" if none yet
    if not st.session_state.guesses:
        if st.button("Suggest Word", key="initial_suggest"):
            add_new_guess()
            st.rerun()


    # Color mapping
    color_map = {
        0: "#111",      # black
        1: "orange",    # orange
        2: "green",     # green
    }

    # UI Loop
    for guess_index, guess_data in enumerate(st.session_state.guesses):
        word = guess_data["word"]
        print(f"WORD: {word}")
        colors = guess_data["colors"]
        locked = guess_data["locked"]

        st.subheader(f"Suggested Word #{guess_index + 1}")
        cols = st.columns(5)

        for i, letter in enumerate(word):
            with cols[i]:
                if not locked:
                    with st.form(key=f"form_{guess_index}_{i}"):
                        submitted = st.form_submit_button(letter)
                        if submitted:
                            colors[i] = (colors[i] + 1) % 3
                            st.rerun()

                    # Show color patch on letter (styled div)
                    bg_color = color_map[colors[i]]
                    st.markdown(
                        f"""
                        <div style="
                            height:50px;
                            width:50px;
                            background-color:{bg_color};
                            color:white;
                            font-size:24px;
                            font-weight:bold;
                            display:flex;
                            align-items:center;
                            justify-content:center;
                            border-radius:5px;
                            ">
                            {letter}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    # Locked: show static colored square with letter
                    bg_color = color_map[colors[i]]
                    st.markdown(
                        f"""
                        <div style="
                            height:50px;
                            width:50px;
                            background-color:{bg_color};
                            color:white;
                            font-size:24px;
                            font-weight:bold;
                            display:flex;
                            align-items:center;
                            justify-content:center;
                            border-radius:5px;
                            ">
                            {letter}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        # ENTER FEEDBACK button
        if not guess_data["feedback_given"] and not locked:
            if st.button(f"Enter Feedback #{guess_index + 1}", key=f"feedback_btn_{guess_index}"):
                feedback = [{0: "Black", 1: "Orange", 2: "Green"}[color] for color in colors]
                store_feedback_information(word, feedback, st.session_state.known_present_letters, st.session_state.known_absent_letters, st.session_state.known_absent_letters_in_positions, st.session_state.my_word, st.session_state.possible_solutions)
                print(f"func2 - outside: ---> len(possible_solutions): {len(st.session_state.possible_solutions)}")
                print(word)
                print(st.session_state.known_present_letters)
                st.session_state.guesses[guess_index]["locked"] = True
                st.session_state.guesses[guess_index]["feedback_given"] = True
                st.session_state[f"show_suggest_{guess_index}"] = True
                st.session_state["reset_custom_word"] = True
                st.rerun()

        # SUGGEST NEW WORD button
        if st.session_state.get(f"show_suggest_{guess_index}", False):
            if not guess_data["suggestion_made"]:
                if len(st.session_state.possible_solutions) == 0:
                    st.warning("No possible words remain. Please check the feedback or reset.")
                else:
                    if st.button(f"Suggest New Word #{guess_index + 2}", key=f"suggest_btn_{guess_index}"):
                        st.session_state.guesses[guess_index]["suggestion_made"] = True
                        add_new_guess()
                        st.rerun()

    st.markdown("---")
    if st.button("🔁 Reset Game"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


