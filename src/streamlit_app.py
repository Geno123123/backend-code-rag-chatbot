import json
import os
import re
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv


# =========================
# Streamlit 기본 설정
# =========================
st.set_page_config(
    page_title="Backend Code RAG Chatbot",
    page_icon="🔎",
    layout="wide",
)

st.title("Backend Code RAG Chatbot")
st.caption("샘플 백엔드 코드를 검색하고, 로컬 LLM이 코드 문맥을 바탕으로 답변하는 RAG 데모입니다.")


# =========================
# 환경 설정
# =========================
load_dotenv()

DOCUMENTS_PATH = Path(os.getenv("SAMPLE_DOCUMENTS_PATH", "data/sample_documents.json"))
USE_OLLAMA = os.getenv("USE_OLLAMA", "true").lower() == "true"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
TOP_N = int(os.getenv("TOP_N", "3"))


# =========================
# 데이터 로드
# =========================
def load_documents(path: Path):
    if not path.exists():
        st.error(f"샘플 문서 파일을 찾을 수 없습니다: {path}")
        st.stop()

    with path.open("r", encoding="utf-8") as file:
        documents = json.load(file)

    return documents


# =========================
# 검색 로직
# =========================
def split_camel_case(text: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", " ", text)


def normalize_text(text: str) -> str:
    text = split_camel_case(text)
    text = text.lower()
    return re.sub(r"[^a-zA-Z0-9가-힣_]+", " ", text)


def expand_korean_keywords(query: str) -> str:
    keyword_map = {
        "사용자": "user",
        "회원": "user",
        "유저": "user",
        "조회": "find get search",
        "찾": "find search",
        "컨트롤러": "controller",
        "요청": "request controller",
        "서비스": "service",
        "로직": "logic method service",
        "메서드": "method function",
        "함수": "method function",
        "클래스": "class",
        "주문": "order",
        "생성": "create",
        "검증": "validate",
        "금액": "price total calculate",
        "계산": "calculate total",
        "예외": "exception throw",
    }

    expanded = query

    for korean, english in keyword_map.items():
        if korean in query:
            expanded += f" {english}"

    return expanded


def tokenize(text: str):
    text = expand_korean_keywords(text)
    text = normalize_text(text)
    return [token for token in text.split() if len(token) >= 2]


def score_document(query: str, document: dict):
    query_tokens = tokenize(query)

    file_name = document.get("file_name", "")
    code_text = document.get("text", "")

    searchable_text = normalize_text(file_name + " " + code_text)

    score = 0

    for token in query_tokens:
        if token in searchable_text:
            score += 3

    normalized_query = normalize_text(expand_korean_keywords(query))
    normalized_file_name = normalize_text(file_name)

    for part in normalized_file_name.split():
        if part and part in normalized_query:
            score += 5

    file_stem = Path(file_name).stem.lower()
    if file_stem and file_stem in normalized_query.replace(" ", ""):
        score += 10

    return score


def search_documents(query: str, documents: list[dict]):
    results = []

    for doc in documents:
        score = score_document(query, doc)

        if score > 0:
            results.append(
                {
                    "file_name": doc.get("file_name", "unknown"),
                    "text": doc.get("text", ""),
                    "score": score,
                }
            )

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:TOP_N]


# =========================
# LLM 답변 생성
# =========================
def build_prompt(query: str, results: list[dict]):
    context_parts = []

    for index, result in enumerate(results, start=1):
        context_parts.append(
            "\n".join(
                [
                    f"[문서 {index}]",
                    f"파일명: {result['file_name']}",
                    f"검색 점수: {result['score']}",
                    "코드:",
                    result["text"],
                ]
            )
        )

    context = "\n\n".join(context_parts)

    prompt = (
        "너는 백엔드 소스코드 분석을 도와주는 RAG 기반 개발 보조 챗봇이다.\n\n"
        "규칙:\n"
        "1. 반드시 제공된 코드 문맥을 근거로 답변한다.\n"
        "2. 코드 문맥에 없는 내용은 추측하지 않는다.\n"
        "3. 답변은 한국어로 한다.\n"
        "4. 관련 파일명, 클래스 역할, 메서드 흐름을 함께 설명한다.\n"
        "5. 답변 마지막에 '근거 파일'을 짧게 적는다.\n\n"
        "아래는 사용자의 질문과 관련된 코드 문맥이다.\n\n"
        f"{context}\n\n"
        f"사용자 질문:\n{query}\n\n"
        "위 코드 문맥을 바탕으로 답변해줘."
    )

    return prompt


def fallback_answer(results: list[dict]):
    top = results[0]
    file_name = top["file_name"]

    answer = f"가장 관련 있는 파일은 `{file_name}`입니다.\n\n"

    if "Controller" in file_name:
        answer += (
            "이 파일은 사용자의 요청을 받아 서비스 계층으로 전달하는 컨트롤러 역할을 합니다. "
            "`UserController`는 `UserService`를 사용해 사용자 조회 요청을 처리합니다."
        )
    elif "OrderService" in file_name:
        answer += (
            "이 파일은 주문 생성 관련 비즈니스 로직을 담당합니다. "
            "`createOrder()` 메서드에서 주문 항목을 검증하고, 총 금액을 계산한 뒤 결과를 반환합니다."
        )
    elif "UserService" in file_name:
        answer += (
            "이 파일은 사용자 조회 관련 비즈니스 로직을 담당합니다. "
            "`findUserById()` 메서드에서 저장소를 통해 사용자를 조회하고, 없으면 예외를 발생시킵니다."
        )
    else:
        answer += "검색된 코드 문맥을 기준으로 관련 기능을 확인할 수 있습니다."

    answer += f"\n\n근거 파일: `{file_name}`"
    return answer


def ask_llm(query: str, results: list[dict]):
    if not results:
        return (
            "관련된 샘플 코드를 찾지 못했습니다.\n\n"
            "예시 질문:\n"
            "- UserController는 어떤 역할을 해?\n"
            "- UserService는 어디에서 사용자를 조회해?\n"
            "- 주문 생성 로직은 어디에 있어?"
        )

    if not USE_OLLAMA:
        return fallback_answer(results)

    prompt = build_prompt(query, results)

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=180,
        )

        response.raise_for_status()
        data = response.json()

        answer = data.get("response", "").strip()

        if not answer:
            return fallback_answer(results)

        return answer

    except requests.exceptions.RequestException as error:
        return (
            "Ollama 호출에 실패했습니다.\n\n"
            f"- 모델명: `{OLLAMA_MODEL}`\n"
            f"- URL: `{OLLAMA_URL}`\n"
            f"- 오류: `{error}`\n\n"
            "대신 검색된 코드 기준으로 간단 답변을 표시합니다.\n\n"
            + fallback_answer(results)
        )


# =========================
# UI
# =========================
documents = load_documents(DOCUMENTS_PATH)

with st.sidebar:
    st.header("RAG Settings")
    st.write(f"Mode: `{'Ollama + Local LLM' if USE_OLLAMA else 'Fallback Demo'}`")
    st.write(f"Model: `{OLLAMA_MODEL}`")
    st.write(f"Documents: `{len(documents)}`")
    st.write(f"Top N: `{TOP_N}`")

with st.expander("예시 질문 보기"):
    st.markdown(
        """
- UserController는 어떤 역할을 해?
- UserService는 어디에서 사용자를 조회해?
- 주문 생성 로직은 어디에 있어?
- OrderService의 검증 로직 알려줘
        """
    )

query = st.chat_input("코드에 대해 질문해보세요.")

if query:
    with st.chat_message("user"):
        st.markdown(query)

    results = search_documents(query, documents)

    with st.chat_message("assistant"):
        with st.spinner("관련 코드를 검색하고 답변을 생성하는 중입니다..."):
            answer = ask_llm(query, results)

        st.markdown(answer)

        if results:
            with st.expander("검색된 관련 코드 보기"):
                for index, result in enumerate(results, start=1):
                    st.markdown(f"### {index}. {result['file_name']}")
                    st.markdown(f"검색 점수: `{result['score']}`")
                    st.code(result["text"], language="java")