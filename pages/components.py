import streamlit as st
import json 

st.title("💻 Streamlit Basic")

st.markdown("아래 탭을 클릭하면서 코드와 그 결과물을 직접 확인해보세요 😀")

tabs = st.tabs(
    ["📝 01 텍스트", "⌨️ 02 텍스트 입력", "🖱️ 03 선택 입력", "👇 04 버튼", "📂 05 파일 업로드", "💾 Session state"]
)

# Load the JSON data from the file
with open("resources/data.json", "r", encoding="utf-8") as f:
    data_list = json.load(f)

# Define the content for each tab
for tab, tab_data in zip(tabs, data_list):
    with tab:
        st.info(f"""{tab_data["info"]}""", icon="ℹ️")
        for data in tab_data["data"]:
            st.subheader(data["title"])
            st.code(data["code"])
            with st.container(border=True):
                exec(data["code"])
