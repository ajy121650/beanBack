# cafe/utils/in_memory_faiss.py

import threading
import faiss
import numpy as np
import openai
from django.conf import settings
from cafe.models import Cafe

# OpenAI 키
openai.api_key = settings.OPENAI_API_KEY

# 전역 변수(싱글톤)로 인덱스와 ID 매핑 저장
_INDEX = None
_IDS   = None
_LOCK  = threading.Lock()  # 멀티 쓰레드 안전

def l2_normalize(vectors):
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / norms

def get_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    text = text.replace("\n", " ")
    response = openai.embeddings.create(input=[text], model=model)
    return response.data[0].embedding

def _build_index():
    """
    한 번만 호출되어 FAISS 인덱스를 메모리에 생성합니다.
    """
    global _INDEX, _IDS

    with _LOCK:
        if _INDEX is None:
            # 1) embedding 필드가 채워진 카페 로드
            cafes = list(Cafe.objects.exclude(embeddings=[]))
            vectors = [c.embeddings for c in cafes]
            _IDS = [c.id for c in cafes]

            vectors = np.array(vectors, dtype="float32")
            normalizedVectors = l2_normalize(vectors)

            # 2) FAISS 인덱스 생성
            dim = len(vectors[0])
            index = faiss.IndexFlatIP(dim)
            index.add(normalizedVectors)

            _INDEX = index

    return _INDEX, _IDS

def search_similar_cafes(query: str, top_k: int = 15):
    """
    메모리 인덱스를 사용해 즉시 검색 결과를 리턴합니다.
    """
    # 1) 인덱스가 없으면 빌드
    index, ids = _build_index()

    # 2) 질문 임베딩
    qv = np.array(get_embedding(query), dtype="float32").reshape(1, -1)
    normalizedQv = l2_normalize(qv)

    # 3) FAISS 검색
    distances, indices = index.search(normalizedQv, top_k)

    # 4) 인덱스 번호 → Cafe.id 매핑
    result_cafe_ids = [ids[i] for i in indices[0]]

    # 5) 실제 Cafe 객체 반환 (거리 순서 유지)
    id2dist = dict(zip(result_cafe_ids, distances[0]))
    cafes = list(Cafe.objects.filter(id__in=result_cafe_ids))
    cafes.sort(key=lambda c: id2dist[c.id])
    return cafes