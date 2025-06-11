import streamlit as st

st.set_page_config(page_title="뉴콘텐츠아카데미", layout="wide")

pages = [
    st.Page(
        page="pages/components.py", 
        title="Basic", 
        icon=":material/code:", 
        default=True
    ),
    st.Page(
        page="pages/02_copywriterBot.py", 
        title="CopywriterBot", 
        icon=":material/lightbulb_2:"
    ),
    st.Page(
        page="pages/03_chatbot.py", 
        title="Chatbot", 
        icon=":material/pets:"
    ),
    st.Page(
        page="pages/03_chatbot_history.py", 
        title="Chatbot(대화 저장 기능 추가)", 
        icon=":material/pets:"
    ),
    st.Page(
        page="pages/04_chatbot_npc.py", 
        title="Chatbot NPC", 
        icon=":material/robot:"
    )
]

nav = st.navigation(pages)
nav.run()
