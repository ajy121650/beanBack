# utils/area.py
import re

# 필요한 지역 키워드만 추가해 가세요 (동/구/역/핫플 상권 키워드)
AREA_PATTERNS = [
    r"[가-힣]+구", r"[가-힣]+동", r"[가-힣]+역",
    r"홍대|강남|건대|신림|봉천|관악|신촌|합정|성수|압구정|여의도|잠실|사당|노원|왕십리",
]

def extract_area_tokens(text: str) -> list[str]:
    found = set()
    for pat in AREA_PATTERNS:
        for m in re.findall(pat, text):
            found.add(m)
    # 길이가 짧거나 애매한 토큰 정리(선택)
    toks = [t.strip() for t in found if len(t.strip()) >= 2]
    # 관악/관악구 같이 둘 다 잡히면 '관악구' 우선 등 정규화도 가능
    return sorted(toks, key=lambda x: -len(x))