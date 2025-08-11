from django.shortcuts import render

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

review_description_prompt = (
    "너는 리뷰 데이터를 기반으로 카페 소개글을 작성하는 전문가야. 각 카페에 대한 리뷰 내용을 종합하여, 원칙 1~5를 참고해 해당 카페의 전반적인 특징을 서술하는 카페의 전반적인 특성을 담은 정보 중심 소개글(cafe description)을 작성해줘.\n"
    "원칙 1. 단순한 감상 요약이 아닌, 가능한 한 객관적인 정보 중심의 요약문으로 작성한다. 어떤 분위기의 공간인지, 어떤 메뉴가 인기 있는지, 어떤 사람들이 주로 방문하는지, 공간 구성이나 좌석/소음/콘센트 등 물리적 특징이 어떤지를 구체적으로 기술한다.\n"
    "원칙 2. 리뷰에 자주 등장한 명사와 형용사를 핵심 키워드(예: 소금빵, 감성 인테리어, 카공, 조용함, 팀플, 강아지 동반 등)로 보고 이를 자연스럽게 포함한다.\n"
    "원칙 3. 길이는 3~5문장 정도로 작성하되, 정보는 최대한 풍부하게 담는다.\n"
    "원칙 4. 표현은 자연스러운 한국어 서술문으로 작성하며, 검색 유사도 계산 시 활용 가능한 풍부한 키워드가 포함되도록 한다.\n"
    "원칙 5. 출력은 하나의 단락으로 작성하며, 문장은 자연스럽게 연결되도록 한다.\n"
    "출력 예시: “이 카페는 조용한 분위기에서 카공이나 혼자 시간을 보내기에 적합한 곳으로, 콘센트와 와이파이 환경이 잘 갖춰져 있습니다. 인기 메뉴로는 소금빵과 바닐라라떼가 자주 언급되며, 감성적인 인테리어와 넓은 좌석 배치로 팀플이나 대화 공간으로도 추천됩니다. 반려동물 동반이 가능하다는 점도 특징이며, 인스타그램 감성 사진을 찍기 좋은 공간이라는 리뷰가 많습니다. 전반적으로 다양한 목적의 방문객에게 만족감을 주는 공간으로 보입니다.”"
)

review_tag_rating_prompt = (
    "너는 리뷰 데이터 분석을 기반으로 정량적인 별점 평가를 수행하는 전문가야. 각 카페에 대한 리뷰 내용을 기반으로, 원칙 1~3을 참고하여 아래 7가지 별점태그에 대해 각각 0.0~5.0점(0.1 단위)으로 별점을 매겨줘.\n"
    "원칙 1. 별점태그는 다음 7가지야: [카공], [조용], [데이트], [대화], [사진], [힐링], [팀플]\n"
    "원칙 2. 별점은 0.0 이상 5.0 이하의 범위이며, 0.1 단위로 가능한 정밀하게 평가해줘. 예: [카공] 4.2, [조용] 3.8, ...\n"
    "원칙 3. 각 별점태그는 다음 기준에 따라 평가해줘.\n"
    "- [카공]: 노트북을 사용해 공부하거나 작업하기에 적합한지에 대한 평가 (리뷰에서 “콘센트 많음”, “와이파이 빠름”, “작업하기 좋아요” 등의 내용이 있으면 높은 점수)\n"
    "- [조용]: 전반적인 소음 수준과 방해 요소가 적은지를 평가 (리뷰에서 “조용함”, “잔잔한 음악”, “통화하는 사람 없음”, “시끄럽지 않아요”, “공부에 집중하기 좋음” 등의 내용이 있으면 높은 점수)\n"
    "- [데이트]: 커플이 방문하기에 적절한 분위기와 좌석 구성, 프라이버시, 감성 등을 평가 (리뷰에서 “분위기 좋음”, “데이트로 추천”, “분위기 있는 인테리어”, “은은한 조명”, “2인용 자리 좋아요” 등의 내용이 있으면 높은 점수)\n"
    "- [대화]: 친구, 지인과의 가벼운 대화나 수다 떨기에 적합한 공간인지를 평가 (리뷰에서 “친구랑 얘기하기 좋아요”, “좌석 간 간격 넓음”, “시끄럽지 않아서 대화하기 편함” 등의 내용이 있으면 높은 점수)\n"
    "- [사진]: 사진을 찍기 좋은 포토존, 예쁜 음료/인테리어 등 비주얼 요소 중심 평가 (리뷰에서 “인스타 감성”, “느좋”, “사진 찍기 좋아요”, “감성카페”, “조명 예뻐요” 등의 내용이 있으면 높은 점수)\n"
    "- [힐링]: 감성적 안정, 편안한 분위기, 여유로움 등을 중심으로 평가 (리뷰에서 “편안함”, “혼자 시간 보내기 좋아요”, “여유로운 분위기”, “차분함” 등의 내용이 있으면 높은 점수)\n"
    "- [팀플]: 3인 이상의 사람들과 모임이나 스터디를 하기에 적합한지를 평가 (리뷰에서 “자리 넓음”, “단체 자리 있음”, “스터디 하기 좋음”, “모임 장소로 좋음” 등의 내용이 있으면 높은 점수)\n"
    "결과는 JSON 형식으로 아래와 같이 응답해줘:\n"
    "{\n"
    "  \"카공\": 4.2,\n"
    "  \"조용\": 3.8,\n"
    "  \"데이트\": 4.9,\n"
    "  ...\n"
    "}"
)

review_keyword_prompt = (
    "너는 리뷰 데이터를 분석해 카페의 고유한 특징을 추출하는 키워드 분석 전문가야. 각 카페에 대한 리뷰 내용을 기반으로, 원칙 1~4을 참고하여 해당 카페에 대한 고유한 특징들을 가장 잘 나타낼 수 있는 키워드를 각 카페마다 5개씩 추출해줘.\n"
    "원칙 1. 최종 키워드는 명확하고 간결한 한 단어 또는 짧은 구(띄어쓰기 포함 10자 이내)로 표현한다. 문장 형태(X)나 감탄 표현(X)은 제외한다.\n"
    "원칙 2. 불용어(예: '정말', '너무', '진짜', '그리고')나 평서문은 제외하고, 핵심 명사 위주로 추출한다.\n"
    "원칙 3. 아래와 같은 뾰족한 정보에 기반한 키워드를 선호한다:\n"
    "- 메뉴명 (예: 소금빵, 바닐라라떼, 에그타르트 등)\n"
    "- 분위기나 목적 (예: 조용함, 카공, 팀플, 감성카페 등)\n"
    "- 공간 특징 (예: 콘센트 많음, 좌석 넓음, 햇살 잘 들어옴 등)\n"
    "- 사용 용도 (예: 혼카, 데이트, 스터디, 인스타감성 등)\n"
    "- 기타 독특한 요소 (예: 강아지 동반 가능, 뷰맛집 등)\n"
    "원칙 4. 키워드는 중립적이고 일반적인 표현(예: '좋아요', '굿', '이뻐요')은 제외한다.\n"
    "결과는 JSON 배열 형식으로 5개 이하의 키워드를 반환해줘. 예: [\"소금빵\", \"카공\", \"콘센트 많음\", \"감성카페\", \"데이트\"]"
)

query_keyword_prompt = (
    "너는 카페 검색 질의에서 핵심 키워드를 추출하는 전문가다.\n"
    "아래 원칙을 지켜 0~5개의 키워드를 JSON 배열로만 출력하라(설명 금지).\n"
    "[원칙]\n"
    "1) 질의가 짧거나 뾰족한 정보가 없으면 빈 배열([])을 출력한다.\n"
    "2) 키워드는 명확하고 간결한 한 단어 또는 짧은 구(띄어쓰기 포함 10자 이내)로 표기한다.\n"
    "3) 불용어·감탄사·서술형 문장·이모지·해시태그·따옴표를 제거하고, 핵심 명사/명사구만 남긴다.\n"
    "4) 동의어/중복은 하나로 통일한다(예: ‘조용함’, ‘소음 적음’ → ‘조용함’).\n"
    "5) 아래 유형의 뾰족한 정보를 우선한다:\n"
    "- 메뉴명: 소금빵, 바닐라라떼, 에그타르트\n"
    "- 분위기/목적: 조용함, 카공, 팀플, 감성카페\n"
    "- 공간 특징: 콘센트 많음, 좌석 넓음, 햇살 잘 들어옴\n"
    "- 사용 용도: 혼카, 데이트, 스터디, 인스타감성\n"
    "- 기타: 강아지 동반 가능, 뷰맛집\n"
    "6) 출력은 유효한 JSON 배열이어야 하며, 그 외 텍스트를 섞지 않는다.\n"
    "7) 가능하면 표준 형태로 정규화한다(예: ‘카공하기 좋음’ → ‘카공’).\n"
    "[출력 형식 예]\n"
    "[\"소금빵\",\"카공\",\"콘센트 많음\",\"감성카페\",\"데이트\"]"
)

def review_description(review_text):
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": review_description_prompt},
            {"role": "user", "content": review_text}
        ]
    )
    return response.choices[0].message.content

@csrf_exempt
def review_tag_rating(review_text: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": review_tag_rating_prompt},
            {"role": "user", "content": review_text}
        ]
    )
    content = response.choices[0].message.content
    return json.loads(content)

@csrf_exempt
def review_keyword(review_text: str) -> list:
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": review_keyword_prompt},
            {"role": "user", "content": review_text}
        ]
    )
    content = response.choices[0].message.content
    return json.loads(content)

@csrf_exempt
def query_keyword(query_text: str) -> list:
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": query_keyword_prompt},
            {"role": "user", "content": query_text}
        ]
    )
    content = response.choices[0].message.content
    return json.loads(content) if content else []