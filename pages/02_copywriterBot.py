import streamlit as st 
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
# -------------------------------------------------------------
# Chatbot 관련 설정
# ------------------------------------------------------------- 
# 환경변수 불러오기
load_dotenv()

# Model 생성
model = ChatOpenAI(
    model="gpt-4o-mini",  # 비용 gpt-4.1-nano < gpt-4o-mini < gpt-4
    temperature=0.5       # 창의성 정도(0~1 사이의 값. 1에 가까울수록 창의적인 답변)
)

# PromptTemplate 정의
template = """
너는 광고를 기획하는 카피라이터야.
다음 정보에 맞춰서 관람객을 끌어들일 창의적인 공연 홍보 문구를 {count}개 만들어줘.

- 공연 주제: {title}
- 문구 길이: {length}
- 말투: {tone}
- 상세 설명: {description}
"""

# Prompt 생성
prompt = PromptTemplate.from_template(template)

# OutputParser 생성
output_parser = StrOutputParser()

# Chain 생성
chain = prompt | model | output_parser 
# -------------------------------------------------------------
# Copywriter Bot 인터페이스
# ------------------------------------------------------------- 
st.title("📝 Copywriter Bot")
st.info("공연 홍보를 위한 카피라이팅 작성을 도와주는 도구입니다. 조건을 입력하여 직접 실행해보세요.", icon="ℹ️")

tone_options = ["유쾌한", "감성적인", "도발적인", "직설적인", "공손한", "흥미유발형", "친근한", "고급스러운"]
# 입력 폼
with st.expander(label="⚙️ 입력 정보", expanded=True):
    title = st.text_input(label="제목", value="별이 빛나는 밤, 고흐의 이야기")
    count = st.number_input(label="문구 개수", min_value=1, max_value=10, value=3)
    length = st.select_slider(label="문구 길이", options=(100, 200, 300, 400, 500), value=200)
    tone = st.multiselect(label="말투", options = tone_options, default=["감성적인", "고급스러운"])
    description = st.text_area(label="세부 설명", height=100, value="빈센트 반 고흐의 대표작을 몰입형 미디어아트로 감상할 수 있는 전시입니다. 고흐의 삶과 감정을 따라가며 별이 빛나는 밤을 직접 체험해보세요. 가족, 연인, 친구와 함께하기 좋은 힐링 전시입니다.")

    submit = st.button("문구 생성", type="primary", use_container_width=True)

if submit:
    with st.spinner("문구 생성 중..."):
        answer = chain.invoke({
            "title": title,
            "count": count,
            "length": length,
            "tone": ", ".join(tone),
            "description": description
        })
        with st.container(border=True):
            st.subheader("💡 실행 결과")
            st.markdown(answer)
