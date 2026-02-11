import streamlit as st
import os
import tempfile
from app.rag_engine import process_document, get_answer

st.set_page_config(page_title="Legal Copilot", layout="wide")

# --- 헤더 ---
st.title("AI 판례/법률 검색 비서")
st.caption("수백 페이지의 판례집이나 계약서를 업로드하세요. AI가 관련 조항을 찾아드립니다.")
st.divider()

# --- 사이드바: 문서 업로드 ---
with st.sidebar:
    st.header("문서 업로드")
    uploaded_file = st.file_uploader("PDF 파일을 드래그하세요", type=["pdf"])
    
    if uploaded_file:
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        if st.button("문서 학습 시작", type="primary"):
            with st.spinner("AI가 문서를 읽고 기억하는 중입니다..."):
                process_document(tmp_path)
                st.success("학습 완료! 이제 질문하세요.")
                os.remove(tmp_path)# 임시 파일 삭제

# --- 메인 : 채팅 인터페이스 ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "법률 문서를 업로드해주시면 내용을 분석해 드립니다."}]

# 이전 대화 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 사용자 입력 처리
if prompt := st.chat_input("질문을 입력하세요"):
    # 사용자 메시지 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 답변 생성
    with st.chat_message("assistant"):
        with st.spinner("관련 조항을 검색 중..."):
            response = get_answer(prompt)
            st.markdown(response)

    # AI 메시지 저장
    st.session_state.messages.append({"role": "assistant", "content": response})