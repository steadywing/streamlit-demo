import streamlit as st 
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
# -------------------------------------------------------------
# Chatbot 관련 설정
# ------------------------------------------------------------- 
# 환경 변수 불러오기 
load_dotenv()

# 사용자 이름 설정하기
username = "mynpc"

# 프로필 사진 설정하기
profile = {
    "user": "resources/user.png",
    "ai": "resources/npc.png"
}

# Sesstion State에 Chat History를 저장할 Key 만들기
if "history" not in st.session_state:
    st.session_state["history"] = {}
# -------------------------------------------------------------
# File Uploader 인터페이스
# ------------------------------------------------------------- 
st.title("💻 Chatbot NPC")
st.info("NPC 챗봇 인터페이스를 구현한 페이지입니다. 세계관이 설명된 파일을 업로드한 후, 대화해보세요.", icon="ℹ️")

# 텍스트파일 업로드(npc.txt)
expander = st.expander(label="📂 NPC 정보 파일 업로드", expanded=True)
uploaded_file = expander.file_uploader("텍스트 파일을 업로드하세요", type=["txt"])
if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8")
# -------------------------------------------------------------
# Langchain 관련 설정
# ------------------------------------------------------------- 
    # Model 생성
    model = ChatOpenAI(
        model="gpt-4o-mini",  # 비용 gpt-4.1-nano < gpt-4o-mini < gpt-4
        temperature=0.7       # 창의성 정도(0~1 사이의 값. 1에 가까울수록 창의적인 답변)
    )

    # 시스템 프롬프트 정의
    system_prompt = """
    너는 세계관 속 NPC 캐릭터야. 정보는 다음과 같아:

    {content}

    행동은 소괄호로 표현하고, 말투는 캐릭터답게 유지해.  
    답변은 짧고 인상 깊게 해줘. (100자 이내)
    """

    # Prompt 생성
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("user", "{input}")
    ])
    # 시스템 프롬프트에 업로드된 파일 내용 삽입
    prompt_with_variables = prompt.partial(content=content)

    # OutputParser 생성
    output_parser = StrOutputParser()

    # Runnable 생성
    runnable = prompt_with_variables | model | output_parser

    # 세션 ID별 히스토리를 가져오는 함수
    def get_session_history(session_id):
        # Session State의 "history" key 불러오기
        history = st.session_state["history"]

        # store의 key에 session_id가 없는 경우 session_id를 key에 추가
        if session_id not in history: 
            history[session_id] = ChatMessageHistory()
            
        # session_id 키의 값을 반환
        return history[session_id]

    # Chain 생성
    chain = (
        RunnableWithMessageHistory(          # RunnableWithMessageHistory 객체 생성
            runnable,                        # 실행할 Runnable 객체
            get_session_history,             # 세션 ID별 히스토리를 가져오는 함수
            input_messages_key="input",      # 입력 메시지의 키
            history_messages_key="history",  # 기록 메시지의 키
        )
    )
    # -------------------------------------------------------------
    # Chatbot 인터페이스
    # -------------------------------------------------------------     
    st.markdown("텍스트 파일을 반영하여 챗봇이 만들어졌습니다. 대화해보세요 😀")

    # Session State에 Chat History가 있으면, 이전 대화 출력하기
    if username in st.session_state["history"]:
        for chat in st.session_state["history"][username].messages:
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

