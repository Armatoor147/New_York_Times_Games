import streamlit as st

st.title("The New York Times: Game Solver")

# Define the buttons for each game
st.write("Choose a game to solve:")
if st.button("Letter Box"):
    st.switch_page("pages/letter_boxed_streamlit.py")

if st.button("Wordle"):
    st.switch_page("pages/wordle_streamlit.py")

if st.button("Spelling Bee"):
    st.switch_page("pages/spelling_streamlit.py")
