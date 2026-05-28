# Backend Code RAG Chatbot

백엔드 소스코드를 검색하고, 검색된 코드 문맥을 기반으로 로컬 LLM이 답변하는 RAG 기반 코드 질의응답 챗봇 데모입니다.

이 프로젝트는 과거 백엔드 소스코드 기반 RAG 챗봇을 구현했던 경험을 바탕으로, 공개 가능한 더미 Java 코드 샘플을 사용해 검색·응답 흐름을 재구성한 포트폴리오용 저장소입니다.

## 프로젝트 개요

기존 프로젝트에서는 백엔드 소스코드를 chunk 단위로 분할하고, 사용자의 질문과 관련된 코드 조각을 검색해 답변하는 RAG 구조를 구현했습니다.

공개 저장소에서는 실제 소스코드와 내부 데이터가 포함되지 않도록, 민감정보를 제거한 샘플 Java 코드 문서를 사용했습니다. 사용자는 Streamlit 웹 화면에서 코드에 대한 질문을 입력할 수 있고, 애플리케이션은 관련 코드 문서를 검색한 뒤 로컬 LLM에게 문맥과 질문을 전달해 답변을 생성합니다.

## 주요 기능

* 백엔드 코드 문서 기반 질의응답
* 한국어 질문 키워드 확장 검색
* 관련 코드 파일 검색 및 점수화
* Ollama 기반 로컬 LLM 응답 생성
* Streamlit 기반 챗봇 UI
* 검색된 관련 코드 확인
* 질문 시간, 질문 내용, 검색된 파일, 답변 로그 저장

## 사용 기술

* Python
* Streamlit
* Ollama
* Llama / Local LLM
* RAG
* JSON
* requests
* python-dotenv

## 프로젝트 구조

```text
backend-code-rag-chatbot/
├── data/
│   └── sample_documents.json
├── src/
│   └── streamlit_app.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## RAG 처리 흐름

```text
사용자 질문 입력
        ↓
한국어 키워드 확장 및 정규화
        ↓
샘플 코드 문서 검색
        ↓
관련 파일 Top-K 추출
        ↓
검색된 코드 문맥 + 사용자 질문을 프롬프트로 구성
        ↓
Ollama 로컬 LLM 호출
        ↓
답변 출력 및 로그 저장
```

## 실행 방법

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. Ollama 모델 준비

Ollama를 설치한 뒤 사용할 로컬 모델을 다운로드합니다.

```bash
ollama pull llama3.2
```

또는 한국어 응답 품질을 높이고 싶다면 한국어/한영 특화 모델을 사용할 수 있습니다.

```bash
ollama pull exaone3.5:2.4b
```

### 3. 환경 변수 설정

`.env.example` 파일을 참고해 `.env` 파일을 생성합니다.

```env
SAMPLE_DOCUMENTS_PATH=data/sample_documents.json
LOG_DIR=logs

USE_OLLAMA=true
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=llama3.2
TOP_N=3
```

사용할 모델을 변경하려면 `OLLAMA_MODEL` 값을 수정합니다.

```env
OLLAMA_MODEL=exaone3.5:2.4b
```

### 4. Streamlit 실행

```bash
python -m streamlit run src/streamlit_app.py
```

## 예시 질문

```text
UserController는 어떤 역할을 해?
```

```text
UserService는 어디에서 사용자를 조회해?
```

```text
주문 생성 로직은 어디에 있어?
```

```text
OrderService의 검증 로직 알려줘
```

## Demo Evaluation

공개 데모에서는 실제 내부 소스코드 대신 더미 백엔드 코드 샘플을 사용해 RAG 흐름을 검증했습니다.

| Test Query                  | Expected Retrieved File | Result  |
| --------------------------- | ----------------------- | ------- |
| UserController는 어떤 역할을 해?   | UserController.java     | Success |
| UserService는 어디에서 사용자를 조회해? | UserService.java        | Success |
| 주문 생성 로직은 어디에 있어?           | OrderService.java       | Success |
| OrderService의 검증 로직 알려줘     | OrderService.java       | Success |

## Logging

사용자가 질문을 입력하면 다음 정보가 로그 파일에 저장됩니다.

* 질문 시간
* 사용자 질문
* 검색된 관련 파일
* 생성된 답변

로그는 `logs/YYYY-MM-DD.log` 형식으로 저장됩니다.

```text
[2026-05-28 18:10:25]
Question: 주문 생성 로직은 어디에 있어?
Retrieved Files: OrderService.java
Answer: ...
--------------------------------------------------------------------------------
```

`logs/` 폴더는 실행 기록이므로 GitHub에는 업로드하지 않습니다.

## 공개용 데이터 처리

이 저장소에는 실제 회사명, 내부 시스템명, 원본 소스코드, 실제 임베딩 데이터, API Key가 포함되어 있지 않습니다.

실제 프로젝트에서는 백엔드 소스코드를 기반으로 RAG 흐름을 구성했지만, 공개 저장소에서는 보안상 더미 Java 코드 샘플을 사용해 동일한 흐름을 재현했습니다.

## Limitations

* 공개 데모는 실제 내부 소스코드가 아닌 샘플 문서 기반으로 동작합니다.
* 현재 검색 방식은 가벼운 키워드 기반 검색입니다.
* 로컬 LLM 응답 품질은 사용자가 설치한 Ollama 모델 성능에 영향을 받습니다.
* 실제 프로젝트에서 사용한 전체 데이터와 내부 경로는 공개하지 않습니다.

## Future Improvements

* SentenceTransformer 기반 embedding 검색 적용
* 코드 chunking 전략 고도화
* 검색 점수 정규화 및 Top-K 검색 품질 개선
* 질문/답변 로그를 CSV 또는 JSON 형태로 저장
* Streamlit UI에서 검색 이력 확인 기능 추가
* 실제 프로젝트 구조를 반영한 더 다양한 샘플 문서 추가

## 주요 학습 내용

* RAG 기반 코드 질의응답 흐름 설계
* 코드 문서 검색 및 프롬프트 구성
* 로컬 LLM과 Streamlit 연동
* 민감정보를 제거한 공개용 포트폴리오 구성
* 질문/답변 로그 저장 기능 구현
