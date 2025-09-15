import streamlit as st
from utils.spelling_bee_agent import spelling_bee_reply, message_to_HumanMessage, message_to_AIMessage


spelling_bee_intro = "Have a tricky puzzle on your hands? Just provide the seven letters from today’s Spelling Bee — one center letter and six outer letters — and our AI agent will solve it for you providing all the valid words. (e.g. [A, [B, C, D, E, F, G]])"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display title
st.title("Spelling Bee")
st.write(spelling_bee_intro)
messages_placeholder = st.empty()

# Query bar
with st.form(key="sb_form"):
    SB_query = st.text_input(
        label="Enter your 'Spelling Bee' puzzle:",
        placeholder="Enter puzzle",
        key="sb_input",
        label_visibility="collapsed"
    )
    submit_button = st.form_submit_button(label="Send")

# Reset game button
if st.button("Reset Game"):
    st.session_state.messages = []
    st.session_state.processed_input = None
    # Force update the placeholder
    messages_placeholder.markdown("<h2 style='text-align: center;'>Spelling Bee Mode</h2>", unsafe_allow_html=True)
    messages_placeholder.write("Game reset. Enter a new prompt.")

# Display messages in the placeholder
with messages_placeholder.container():
    for i, msg in enumerate(st.session_state.messages):
        if i % 2 == 0:
            st.write(f"**You:** {msg.content if hasattr(msg, 'content') else msg}")
        else:
            st.write(f"**AI:** {msg.content if hasattr(msg, 'content') else msg}")

# Submit button
if submit_button and SB_query:
    # Store user query in messages
    SB_query = message_to_HumanMessage(SB_query)
    st.session_state.messages.append(SB_query)
    # Get AI response
    ai_response = spelling_bee_reply(st.session_state.messages)
    # Store AI response in messages
    ai_response = message_to_AIMessage(ai_response)
    st.session_state.messages.append(ai_response)
    # Force update the placeholder
    with messages_placeholder.container():
        for i, msg in enumerate(st.session_state.messages):
            if i % 2 == 0:
                st.write(f"**You:** {msg.content if hasattr(msg, 'content') else msg}")
            else:
                st.write(f"**AI:** {msg.content if hasattr(msg, 'content') else msg}")
