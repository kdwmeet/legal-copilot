# Legal Copilot (AI 법률 판례 검색 및 분석 솔루션)

## 1. 프로젝트 개요

Legal Copilot은 방대한 법률 문서(판례, 계약서, 법령 등)를 인공지능이 분석하여, 사용자의 질의에 대한 정확한 법적 근거와 답변을 제공하는 리걸테크(Legal Tech) 솔루션입니다.

기존 LLM(대규모 언어 모델)이 가진 환각 현상(Hallucination, 사실이 아닌 내용을 사실처럼 생성하는 문제)을 해결하기 위해 **RAG (Retrieval-Augmented Generation, 검색 증강 생성)** 기술을 도입했습니다. 사용자가 업로드한 PDF 문서를 벡터 데이터베이스에 저장하고, 질문과 의미적으로 가장 유사한 법률 조항이나 판례를 검색(Retrieval)한 뒤, 이를 근거로 OpenAI의 **gpt-5-mini** 모델이 답변을 생성합니다. 이를 통해 변호사 및 법무 실무자는 수천 페이지의 문서를 직접 검토하는 시간을 획기적으로 단축할 수 있습니다.

### 주요 기능
* **PDF 문서 분석:** 사용자가 업로드한 판례집, 근로계약서, 임대차계약서 등의 비정형 텍스트 데이터를 자동으로 추출 및 분석.
* **Semantic Search (의미 기반 검색):** 단순 키워드 매칭이 아닌, 질문의 법적 맥락과 의도를 파악하여 가장 관련성 높은 문서 조항을 검색.
* **Evidence-based Q&A:** 반드시 업로드된 문서 내에 존재하는 내용만을 근거로 답변을 생성하며, 출처(조항 번호 등)를 명시하여 신뢰성 확보.
* **Context Awareness:** 긴 법률 문서를 문맥이 끊기지 않도록 최적의 크기(Chunk)로 분할하여 처리.

## 2. 시스템 아키텍처 (RAG Pipeline)

본 시스템은 LangChain 프레임워크를 기반으로 구축되었으며, 다음과 같은 데이터 처리 파이프라인을 따릅니다.

1.  **Document Loading:** `PyPDFLoader`를 사용하여 PDF 파일의 텍스트를 추출.
2.  **Text Splitting:** `RecursiveCharacterTextSplitter`를 사용하여 문서를 1000자 단위의 청크(Chunk)로 분할하되, 문맥 유지를 위해 200자의 중복 구간(Overlap)을 설정.
3.  **Embedding:** OpenAI의 임베딩 모델을 사용하여 텍스트 청크를 고차원 벡터(Vector)로 변환.
4.  **Vector Store:** 변환된 벡터 데이터를 `ChromaDB`에 저장하여 고속 유사도 검색 인덱스 생성.
5.  **Retrieval:** 사용자의 질문을 벡터로 변환 후, DB에서 가장 유사도가 높은 상위 3개의 문서 조항을 검색.
6.  **Augmented Generation:** 검색된 문서 조항을 프롬프트 컨텍스트(Context)에 주입하고, **gpt-5-mini** 모델이 이를 바탕으로 최종 답변 생성.

## 3. 기술 스택

* **Language:** Python 3.10 이상
* **LLM:** OpenAI **gpt-5-mini**
* **Orchestration:** LangChain (RetrievalQA Chain)
* **Vector Database:** ChromaDB
* **Embedding Model:** OpenAI text-embedding-3-small
* **UI Framework:** Streamlit
* **Document Processing:** pypdf

## 4. 프로젝트 구조

유지보수와 확장성을 고려하여 UI, 비즈니스 로직, 설정을 분리한 모듈형 구조입니다.

```text
legal-copilot/
├── .env                  # 환경 변수 (API Key)
├── requirements.txt      # 의존성 패키지 목록
├── main.py               # 애플리케이션 진입점 및 채팅 UI
└── app/
    ├── __init__.py
    ├── config.py         # AI 변호사 페르소나 및 시스템 프롬프트 정의
    └── rag_engine.py     # 문서 임베딩, 벡터 저장, 검색 및 답변 생성 로직
```

## 5. 설치 및 실행 가이드
### 5.1. 사전 준비
Python 환경이 설치되어 있어야 합니다. 터미널에서 저장소를 복제하고 프로젝트 디렉토리로 이동하십시오.

```Bash
git clone [레포지토리 주소]
cd legal-copilot
```
### 5.2. 의존성 설치
RAG 구현을 위한 LangChain 및 ChromaDB 관련 라이브러리를 설치합니다.

```Bash
pip install -r requirements.txt
```
### 5.3. 환경 변수 설정
프로젝트 루트 경로에 .env 파일을 생성하고, 유효한 OpenAI API 키를 입력하십시오.

```Ini, TOML
OPENAI_API_KEY=sk-your-api-key-here
```
### 5.4. 실행
Streamlit 애플리케이션을 실행합니다.

```Bash
streamlit run main.py
```
## 6. 데이터 처리 및 보안
* 본 시스템은 데모 버전으로 설계되어 ChromaDB를 인메모리(휘발성) 모드로 구동합니다. 따라서 애플리케이션 재실행 시 학습된 데이터는 초기화됩니다.

* 실제 상용 환경 배포 시에는 벡터 데이터베이스를 영구 저장소(Persistent Storage)로 설정하거나 Pinecone, Milvus 등의 클라우드 벡터 DB를 사용하는 것을 권장합니다.

* 사용자가 업로드한 문서는 텍스트 추출 및 임베딩 과정에서 OpenAI API 서버로 전송되므로, 민감한 개인정보가 포함된 문서는 마스킹 처리 후 사용하는 것을 권장합니다.

## 7. 실행 화면
<img width="1349" height="621" alt="스크린샷 2026-02-11 110632" src="https://github.com/user-attachments/assets/95b7471d-9e76-48cf-8809-63925ec78b9d" />

