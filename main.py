import streamlit as st
import json 

st.set_page_config(page_title="뉴콘텐츠아카데미", layout="centered")


pages = [
    st.Page("pages/components.py", title="Basic", icon=":material/code:", default=True),
    st.Page("pages/copywriterBot.py", title="CopywriterBot", icon=":material/lightbulb_2:"),
    st.Page("pages/chatbot.py", title="Chatbot", icon=":material/pets:"),
    st.Page("pages/chatbot_npc.py", title="Chatbot NPC", icon=":material/robot:")
]

nav = st.navigation(pages)
nav.run()
