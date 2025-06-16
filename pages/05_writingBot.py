import streamlit as st 
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.document_loaders import WebBaseLoader
# -------------------------------------------------------------
# Chatbot 관련 설정
# ------------------------------------------------------------- 
# 환경변수 불러오기
load_dotenv()

# Model 생성
model = ChatOpenAI(
    model="gpt-4o-mini",  # 비용 gpt-4.1-nano < gpt-4o-mini < gpt-4
    temperature=0.7       # 창의성 정도(0~1 사이의 값. 1에 가까울수록 창의적인 답변)
)

# PromptTemplate 정의
template = """
너는 유튜브 숏츠 시나리오를 작성하는 콘텐츠 기획자야.
다음 작업을 단계별로 차례대로 수행하여 최종 숏츠 스크립트를 만들어줘.

[작업 목적]
- 온라인에서 유행하는 밈을 소개하고, 그 밈이 어떻게 탄생했는지 간략한 배경을 설명해주는 영상을 제작한다.
- 시청자가 짧은 시간 안에 해당 밈을 쉽게 이해하고 공감할 수 있도록 예시로 설명하는 것이 목표이다.

[작업 절차]
1단계: 먼저 텍스트를 읽고 핵심 키워드를 5개 추출한다.
2단계: 추출한 키워드를 참고하여 전체 내용을 간략히 요약한다.(500자 이내)
3단계: 요약과 키워드를 참고하여 유튜브 숏츠 시나리오를 작성한다.
- 시나리오는 오프닝 멘트 → 핵심 정보 전달 → 클로징 멘트 순서로 작성한다.
- 총 길이는 약 60초 분량을 가정하여 작성한다.
- 시청자의 흥미를 끌 수 있도록 친근하고 캐주얼한 톤으로 작성한다.

[입력 텍스트]
{text}

[출력 형식]
{{
    "keywords": [...],
    "summary": "...",
    "title" : "...",
    "scenario": "..."
}}
"""

# Prompt 생성
prompt = PromptTemplate.from_template(template)

# OutputParser 생성
output_parser = JsonOutputParser()

# Chain 생성
chain = prompt | model | output_parser 
# -------------------------------------------------------------
# 인터페이스
# ------------------------------------------------------------- 
st.title("📝 Writing Bot")
st.info("웹 페이지에서 키워드를 추출하고 요약한 후 이를 기반으로 숏츠 시나리오를 생성하는 도구입니다.", icon="ℹ️")

with st.expander(label="⚙️ 입력 정보", expanded=True):
    # URL 입력창
    url = st.text_input(
        label="URL",
        placeholder="URL을 입력하세요",
        value="https://namu.wiki/w/Chill%20guy"
    )
    # 버튼
    button = st.button(
        label="시나리오 생성", 
        type="primary", 
        use_container_width=True
    )

with st.container(border=True):
    if button:
        with st.spinner("시나리오 생성 중..."):
            # 웹 사이트 내용 추출
            loader = WebBaseLoader(
                web_path=url,
                header_template = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
                }
            )
            docs = loader.load()
            content = docs[0].page_content
            text = " ".join(content.split())

            # Chain 요청
            result = chain.invoke({"text": text})

            # 결과 출력
            st.subheader("💡 실행 결과")

            ## 요약
            with st.expander(label="요약", expanded=True):
                st.text(result["summary"])

            ## 결과
            st.markdown(f"### **{result['title']}**")
            st.markdown(", ".join([f"#{item}" for item in result["keywords"]]))
            st.markdown(result["scenario"])

    



