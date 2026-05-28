# Backend Code RAG Chatbot

백엔드 소스코드를 임베딩하고, 사용자의 질문과 관련된 코드 조각을 검색해 답변하는 RAG 기반 코드 질의응답 챗봇입니다.

## 프로젝트 개요

이 프로젝트는 백엔드 소스코드 파일을 chunk 단위로 분할한 뒤 embedding을 생성하고, 사용자의 질문과 가장 유사한 코드 조각을 검색하여 GPT 모델에 함께 전달하는 방식으로 동작합니다.

Streamlit 기반 웹 UI를 통해 코드 구조, 클래스 역할, 메서드 위치, 파일 설명 등을 질문할 수 있도록 구성했습니다.

## 주요 기능

- 백엔드 소스코드 기반 RAG 질의응답
- 코드 chunk 검색 및 유사도 기반 정렬
- OpenAI embedding 모델을 활용한 벡터 검색
- Streamlit 기반 챗봇 UI
- 질문/답변 로그 저장
- 검색된 관련 코드 chunk 확인

## 사용 기술

- Python
- Streamlit
- OpenAI API
- Embedding
- RAG
- pandas
- scipy
- tiktoken

## 프로젝트 구조

```text
backend-code-rag-chatbot/
├── src/
│   └── streamlit_app.py
├── data/
├── logs/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md