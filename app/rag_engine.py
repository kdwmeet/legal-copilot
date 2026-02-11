import os
from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from app.config import MODEL_NAME, SYSTEM_PROMPT

# 전역 변수로 벡터 DB 저장
vector_store = None

def process_document(temp_file_path):
    """PDF를 쪼개서 벡터 DB에 저장"""
    global vector_store

    # 문서 로드
    loader = PyPDFLoader(temp_file_path)
    docs = loader.load()

    # 문서 분할 -1000자 단위로 자르고 200자는 겹치게 함
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    # 임베딩 및 저장
    # OpenAI의 임베딩 모델을 사용하여 텍스트를 숫자로 변환
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Chroma DB 생성 (휘발성 메모리)
    vector_store = Chroma.from_documents(documents=splits, embedding=embeddings)

    return True

def get_answer(question):
    """질문에 대한 답변을 벡터 DB에서 검색하여 생성"""
    global vector_store

    if not vector_store:
        return "먼저 문서를 업로드해주세요."
    
    # 검색기 설정
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})

    # LLM 설정
    llm = ChatOpenAI(model=MODEL_NAME, reasoning_effort="low")

    # 프롬프트 연결
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("system", "참고 문서\n{context}"),
        ("human", "{input}")
    ])

    # 체인 생성
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    # 실행
    response = rag_chain.invoke({"input": question})
    return response["answer"]