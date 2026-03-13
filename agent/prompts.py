from langchain_core.prompts import ChatPromptTemplate

# 지원 카테고리 목록
SUPPORTED_CATEGORIES = [
    "spring-boot",
    "spring-data-jpa",
    "spring-data-redis",
    "spring-security",
    "spring-cloud-gateway",
]

# ──────────────────────────────────────────────
# Rewrite Prompt
#   - 검색에 최적화된 영어 쿼리로 변환
# ──────────────────────────────────────────────
REWRITE_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a query optimization assistant for a technical documentation search engine.\n"
        "Rewrite the given user question into a concise, English search query optimized for semantic search.\n"
        "Also return the most relevant category from the list below. If no specific category is clearly implied, return null.\n"
        "Rules:\n"
        "- Keep it under 20 words.\n"
        "- Use technical terminology from Spring Framework.\n"
        "Categories:\n{categories}"
    ),
    ("human", "{question}"),
])

# ──────────────────────────────────────────────
# Grade Prompt
#   - 검색된 결과가 질문에 답하기에 충분한지 판단
# ──────────────────────────────────────────────
GRADE_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a documentation quality grader for a Spring Framework RAG system.\n"
        "Given a user's question and a set of retrieved documents, determine if the documents contain enough information to provide a complete and accurate answer.\n"
        "If the information is missing, ambiguous, or irrelevant to the core question, mark 'should_rewrite' as true to trigger a query reformulation.\n"
        "Only answer 'should_rewrite' as false if you are confident that the documents provide a direct answer."
    ),
    (
        "human",
        "Question: {question}\n\nRetrieved Context:\n{context}"
    ),
])

# ──────────────────────────────────────────────
# Generate Prompt
#   - 검색 결과를 바탕으로 최종 답변 생성
# ──────────────────────────────────────────────
GENERATE_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a technical documentation answer generator for a Spring Framework RAG system.\n"
        "Given a user's question and a set of retrieved documents, generate a complete and accurate answer in Korean.\n"
        "Rules:\n"
        "- Use technical terminology from Spring Framework.\n"
        "- Answer honestly and directly. if you don't know the answer, say so.\n"
        "- All answers must be based on the retrieved documents. Do not answer questions that are not based on the documents. \n"
    ),
    ("human", "{question}\n\nRetrieved Context:\n{context}"),
])
