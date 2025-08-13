# cafe/utils/in_memory_faiss.py

import threading
import faiss
import numpy as np
import openai
from django.conf import settings
from cafe.models import Cafe
from tag.models import Tag
from django.db.models import Prefetch
from cafe.utils.gpt import query_keyword
from typing import List, Tuple
from cafe.utils.area import extract_area_tokens
from django.db.models import Q

# OpenAI 키
openai.api_key = settings.OPENAI_API_KEY

_index = None
_ids = None
_lock = threading.Lock()  # 멀티 쓰레드 안전

def l2_normalize(vectors):
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / norms

def get_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    text = text.replace("\n", " ")
    response = openai.embeddings.create(input=[text], model=model)
    return response.data[0].embedding

def flatten_once(nested):
    """
    1단계 중첩 리스트를 평면화합니다.
    """
    flat = []
    for item in nested:
        if isinstance(item, list):
            flat.extend(item)
        else:
            flat.append(item)
    return flat

def build_index():
    """
    한 번만 호출되어 FAISS 인덱스를 메모리에 생성합니다.
    """
    global _index, _ids

    with _lock:
        if _index is None:
            # 1) embedding 필드가 채워진 카페 로드
            cafes = list(Cafe.objects.exclude(embeddings=[]))
            vectors = [c.embeddings for c in cafes]
            _ids = [c.id for c in cafes]

            vectors = np.array(vectors, dtype="float32")
            normalized_vectors = l2_normalize(vectors)

            # 2) FAISS 인덱스 생성
            dim = len(vectors[0])
            index = faiss.IndexFlatIP(dim)
            index.add(normalized_vectors)

            _index = index

    return _index, _ids

# ---- 후보군으로 임시 인덱스 만들어 임베딩 검색 ----
def build_temp_index_from_cafes(cafes: List[Cafe]) -> Tuple[faiss.Index, List[int]]:
    """
    주어진 Cafe 리스트로만 구성된 임시 FAISS 인덱스를 만든다.
    embeddings가 비어있는 row는 제외한다.
    반환: (index, ids)  # ids는 cafes[i].id 매핑
    """
    # 임베딩이 있는 것만 남김
    cafes_with_vec = [c for c in cafes if c.embeddings]
    if not cafes_with_vec:
        return None, []

    vectors = np.array([c.embeddings for c in cafes_with_vec], dtype="float32")
    vectors = vectors.reshape(len(vectors), -1)
    vectors = l2_normalize(vectors)  # cosine용

    dim = vectors.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(vectors)

    ids = [c.id for c in cafes_with_vec]
    return index, ids

def filter_cafes_by_keywords_simple(query_text: str, candidate_cafes: List[Cafe]) -> List[Cafe]:
    # 1) 키워드 추출
    kws = flatten_once(query_keyword(query_text))  # ["카공","조용함",...]
    #print(f"키워드: {kws}\n")

    # 1) 키워드 없으면 전체 인기순 반환
    if not kws:
        return candidate_cafes

    # 2) 존재하는 태그만
    tag_qs = Tag.objects.filter(content__in=kws)
    if not tag_qs.exists():
        return candidate_cafes  # 키워드가 없으면 전체 반환
    
    ids = [c.id for c in candidate_cafes]

    # 3) keywords(M2M)에 하나라도 포함되면 OK (OR)
    qs = (
        Cafe.objects
        .filter(id__in=ids, keywords__in=tag_qs)
        .distinct()
    )

    MIN_RESULTS = 5  # 최소 결과 수

    if qs.count() < MIN_RESULTS:
        return candidate_cafes  # 키워드가 없으면 전체 반환
    
    #print(f"필터링된 카페: {[c.name for c in qs]}  ({len(qs)}개)\n")
    return list(qs)

def search_with_address_and_keywords_then_embedding(query: str, top_k: int = 15):
    """
    1) 쿼리에서 지역 토큰 추출
    2) 지역 토큰이 있으면 해당 지역 카페로 필터링
    3) 키워드로 후보군 추출
    4) 후보군으로 임시 인덱스 생성
    5) 쿼리 임베딩으로 cosine 검색
    6) 상위 top_k 반환
    - 후보가 없거나 인덱스 구성 불가 시, 전역 인덱스 fallback
    """
    # 1) 쿼리에서 지역 토큰 추출
    area_tokens = extract_area_tokens(query)
    #print(f"지역 토큰: {area_tokens}\n")

    # 2) 지역 토큰이 있으면 해당 지역 카페로 필터링
    base_qs = Cafe.objects.all()
    if area_tokens:
        q_addr = Q()
        for tok in area_tokens:
            q_addr |= Q(address__icontains=tok)
        candidate_cafes = list(base_qs.filter(q_addr).distinct())
    else:
        # 지역이 없으면 전체(또는 최근/평점순 등으로 제한 가능)
        candidate_cafes = list(base_qs)

    if area_tokens and not candidate_cafes:
        # 지역 토큰이 있는데 후보가 없으면 전체로 fallback
        candidate_cafes = list(base_qs)

    #print(f"후보카페 이름: {[c.name for c in candidate_cafes]}  ({len(candidate_cafes)}개)\n\n")
    
    # 3) 키워드로 후보군 추출
    candidate_cafes = filter_cafes_by_keywords_simple(query, candidate_cafes)

    # 4) 임시 인덱스 생성 시도
    tmp_index, tmp_ids = build_temp_index_from_cafes(candidate_cafes)

    if not tmp_index:  # 후보에 임베딩이 없으면 전역으로 fallback
        return search_similar_cafes(query, top_k=top_k)

    # 5) 쿼리 임베딩
    qv = np.array(get_embedding(query), dtype="float32").reshape(1, -1)
    qv = l2_normalize(qv)

    # 6) 검색
    k = min(top_k, len(tmp_ids))
    distances, indices = tmp_index.search(qv, k)

    # 7) ids 매핑 및 정렬 유지
    result_ids = [tmp_ids[i] for i in indices[0]]
    id2dist = dict(zip(result_ids, distances[0]))

    cafes = list(Cafe.objects.filter(id__in=result_ids))
    cafes.sort(key=lambda c: id2dist[c.id], reverse=True)  # IP(=cosine) 점수는 높을수록 좋음
    return cafes

# fallback 검색
def search_similar_cafes(query: str, top_k: int = 15):
    """
    메모리 인덱스를 사용해 즉시 검색 결과를 리턴합니다.
    """
    # 1) 인덱스가 없으면 빌드
    index, ids = build_index()

    # 2) 질문 임베딩
    qv = np.array(get_embedding(query), dtype="float32").reshape(1, -1)
    normalized_qv = l2_normalize(qv)

    # 3) FAISS 검색
    distances, indices = index.search(normalized_qv, top_k)

    # 4) 인덱스 번호 → Cafe.id 매핑
    result_cafe_ids = [ids[i] for i in indices[0]]

    # 5) 실제 Cafe 객체 반환 (거리 순서 유지)
    id2dist = dict(zip(result_cafe_ids, distances[0]))
    cafes = list(Cafe.objects.filter(id__in=result_cafe_ids))
    cafes.sort(key=lambda c: id2dist[c.id])
    return cafes