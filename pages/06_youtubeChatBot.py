import streamlit as st 
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
import yt_dlp
import requests
# -------------------------------------------------------------
# 기본 설정
# ------------------------------------------------------------- 
# 환경 변수 불러오기 
load_dotenv()

# 사용자 이름 설정하기
username = "youtubechatbot"

# 프로필 사진 설정하기
profile = {
    "user": "resources/user.png",
    "ai": "resources/chatbot_cat.png"
}

# Youtube 정보 추출 관련 옵션
ydl_opts = {
    'writesubtitles': True,
    'writeautomaticsub': True,
    'subtitleslangs': ['ko'],
    'skip_download': True,
    'no_warnings': True,
    'extract_flat': False,
}

# Sesstion State에 Youtube 정보를 저장할 Key 만들기
if "info" not in st.session_state:
    st.session_state["info"] = None
# Sesstion State에 Chain을 저장할 Key 만들기
if "chain" not in st.session_state:
    st.session_state["chain"] = None
# Sesstion State에 Chat History를 저장할 Key 만들기
if "history" not in st.session_state:
    st.session_state["history"] = {}

# 다운로드 데이터 만들어주는 함수 만들기
def get_history_data():
    data = []
    if username in st.session_state["history"]:
        for chat in st.session_state["history"][username].messages:
            if isinstance(chat, HumanMessage):
                role = "user"
                avatar = profile["user"]
            elif isinstance(chat, AIMessage):
                role = "ai"
                avatar = profile["ai"]
            
            data.append({"role": role, "content": chat.content})

    json_data = json.dumps(data, ensure_ascii=False, indent=4)
    return json_data
# -------------------------------------------------------------
# Langchain 관련 설정 I
# ------------------------------------------------------------- 
# Model 생성
model = ChatOpenAI(
    model="gpt-4o-mini",  # 비용 gpt-4.1-nano < gpt-4o-mini < gpt-4
    temperature=0.7       # 창의성 정도(0~1 사이의 값. 1에 가까울수록 창의적인 답변)
)

# 시스템 프롬프트 정의
system_prompt = """
너는 사용자가 제공한 유튜브 스크립트 내용을 기반으로 질문에 답변하는 챗봇이야.

[역할]
- 스크립트에 관련된 정보성 질문에는 스크립트 내용을 근거로 정확하게 답변한다.
- 스크립트에 없는 정보성 질문에는 "제공된 정보에서는 해당 내용을 찾을 수 없습니다."라고 정중히 안내한다.
- 단순한 감정 표현, 소감, 공감 요청 등 일반적인 대화가 들어오면 자연스럽게 공감하고 간단히 응대한다.

[답변 스타일]
- 친근하고 자연스러운 대화톤으로 응답한다.
- 정보성 답변은 핵심만 간결하게 전달한다.
- 불필요한 장황한 설명은 하지 않는다.

[유튜브 스크립트 내용]
{script}
"""

# Prompt 생성
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="history"),
    ("user", "{input}")
])

# 세션 ID별 히스토리를 가져오는 함수
def get_session_history(session_id):
    # Session State의 "history" key 불러오기
    history = st.session_state["history"]

    # store의 key에 session_id가 없는 경우 session_id를 key에 추가
    if session_id not in history: 
        history[session_id] = ChatMessageHistory()
        
    # session_id 키의 값을 반환
    return history[session_id]
# -------------------------------------------------------------
# File Uploader 인터페이스
# ------------------------------------------------------------- 
st.title("💻 Youtube ChatBot")
st.info("Youtube 영상 기반 챗봇입니다. 영상과 관련하여 질문하고 그에 대한 응답을 체험해보세요", icon="ℹ️")

with st.expander(label="⚙️ 입력 정보", expanded=True):
    # URL 입력창
    url = st.text_input(
        label="URL",
        placeholder="URL을 입력하세요",
        value="https://www.youtube.com/watch?v=SRLWoE9jyAs"
    )
    # 버튼
    button = st.button(
        label="챗봇 생성", 
        type="primary", 
        use_container_width=True
    )
if button:
    with st.spinner("챗봇 생성 중..."):
        # 대화 기록 초기화
        st.session_state["history"] = {}

        # -------------------------------------------------------------
        # Youtube 정보 추출
        # ------------------------------------------------------------- 
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            st.session_state["info"] = info
        # -------------------------------------------------------------
        # Youtube Script 추출
        # ------------------------------------------------------------- 
        # video_id = url.split("v=")[1]
        # transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["ko"])

        # script = ""
        # for item in transcript:
        #     script = script + item["text"] + " "
        info = st.session_state["info"]
        test_url = info['automatic_captions']['ko'][0]['url']  # 자동 생성 자막 정보 확인
        response = requests.get(test_url)

        result = response.json()
        script = ""
        for event in result['events']:
            if 'segs' in event:
                script += "".join(seg['utf8'] for seg in event['segs'] if 'utf8' in seg)

        script = script.replace("\n", " ").replace("  ", " ")  # 줄바꿈과 다중 공백 제거
        # -------------------------------------------------------------
        # Langchain 관련 설정 II
        # ------------------------------------------------------------- 
        # 시스템 프롬프트에 업로드된 파일 내용 삽입
        prompt_with_variables = prompt.partial(script=script)

        # OutputParser 생성
        output_parser = StrOutputParser()

        # Runnable 생성
        runnable = prompt_with_variables | model | output_parser

        # Chain 생성
        chain = (
            RunnableWithMessageHistory(          # RunnableWithMessageHistory 객체 생성
                runnable,                        # 실행할 Runnable 객체
                get_session_history,             # 세션 ID별 히스토리를 가져오는 함수
                input_messages_key="input",      # 입력 메시지의 키
                history_messages_key="history",  # 기록 메시지의 키
            )
        )
        st.session_state["chain"] = chain
# -------------------------------------------------------------
# Chatbot 인터페이스
# -------------------------------------------------------------     
# Session State에서 데이터 가져오기
info = st.session_state["info"]
chain = st.session_state["chain"]
history = st.session_state["history"]

# Chain이 있을 때만 챗봇 인터페이스 출력
if chain is not None:

    # 사이드바에 Youtube 정보 출력
    with st.sidebar:
        st.download_button(
            label="대화 기록 다운로드",
            data=get_history_data(),
            file_name="chat_history.json",
            mime="application/json",
            type="primary",
            use_container_width=True
        )
        st.video(url)
        st.markdown(info["title"])
        st.markdown(info["description"])

    # ChatBot 생성 안내 메세지 출력
    st.markdown("Youtube 기반 챗봇이 생성되었습니다. 대화해보세요 😀")

    # Session State에 Chat History가 있으면, 이전 대화 출력하기
    if username in history:
        for chat in history[username].messages:
            if isinstance(chat, HumanMessage):
                role = "user"
                avatar = profile["user"]
            elif isinstance(chat, AIMessage):
                role = "ai"
                avatar = profile["ai"]
            
            st.chat_message(role, avatar=avatar).markdown(chat.content)

    # 사용자 입력 창
    question = st.chat_input(placeholder="여기에 질문을 입력하세요...")

    # 사용자가 입력 받을 때마다, 입력된 질문을 세션 상태에 저장하고, AI의 답변을 생성하여 출력하기
    if question:
        ## Step1: 사용자 질문을 출력
        st.chat_message("user", avatar=profile["user"]).markdown(question)
        ## Step2: AI의 답변을 생성(자동으로 사용자, AI 메시지 히스토리에 반영됨)
        answer = chain.invoke({"input": question}, {"configurable": {"session_id": username}})
        ## Step3: AI의 답변을 출력
        st.chat_message("ai", avatar=profile["ai"]).markdown(answer)

