# BeanBack (카페 추천 및 관리 백엔드)

## 프로젝트 개요

BeanBack은 카페 추천 챗봇, 점주 관리, 좌석/도면 관리 등 다양한 기능을 제공하는 Django 기반 백엔드입니다.
AI 기술 스택으로는 OpenAI 임베딩, FAISS 벡터 DB 생성, RAG 검색, Roboflow 이미지 처리 api가 사용되었습니다.
벡엔드 프로그램은 AWS 환경에서 배포되었습니다.

---

## 주요 기능

### 1. Cafe Side - 카페 관리

- 카페 등록/수정/조회 API
- 카페별 태그, 키워드, 사진, 설명 등 관리
- 점주별 카페 관리 기능

### 2. Cafe Side - 좌석/도면 관리 (활용 AI - RoboFlowAi)

- 카페별 좌석(Table), 도면(FloorPlan) 등록/조회/수정/삭제
- 도면 요소 탐지 API

### 3. Cafe Side - 회원가입 및 인증

- JWT 기반 인증 (access/refresh token)
- 쿠키 기반 인증 지원 (커스텀 CookieJWTAuthentication)

### 4. User Side - 검색 및 추천 챗봇 (활용 AI - OpenAI, FAISS)

- OpenAI 임베딩 + FAISS + RAG 검색을 활용한 유사도 기반 카페 추천
- 지역 토큰(구/동/역/핫플) 추출 및 필터링
- 임베딩 검색 후 지역 필터링 방식으로 효율적 추천

---

## AI 활용 영역 설명

### 도면 관리

- 카페를 운영하는 점주 측에서 카페의 자리 상태를 설정하는 것을 더 편리하게 하기 위해서, 카페의 자리 배치 상태 도면만 업로드하면 자동으로 AI가 도면을 인식해서 카페의 자리 배치도를 생성합니다. 이후 변화가 생긴 부분만 점주측에서 직접 자리 상태를 설정할 수 있습니다.

### 카페 추천 챗봇

- 카페를 이용하고자 하는 사용자 측에서 원하는 카페를 더 편리하게 찾도록 하기 위해서, 찾고자 하는 카페의 정보를 챗봇에 자연어로 입력하면 AI가 자동으로 조건에 맞는 카페를 추천 및 재정렬합니다. 사용자는 추천된 카페 리스트와 실시간 혼잡도를 확인하고 원하는 카페를 효율적으로 선택할 수 있습니다.

---

## 기술 스택

- **Django**: 백엔드 프레임워크
- **Django REST Framework**: API 개발
- **drf-yasg**: Swagger 기반 API 문서화
- **MySQL (RDS)**: 데이터베이스
- **OpenAI API**: 임베딩 생성
- **FAISS**: 벡터 DB 생성 및 검색/추천
- **Gunicorn**: WSGI 서버
- **Nginx**: Reverse Proxy
- **Docker/EC2**: 배포 환경

---

## 배포 및 운영

- EC2 서버에서 Gunicorn + Nginx 조합으로 운영
- 코드 변경 시 반드시 Gunicorn 재시작 필요  
  (`sudo systemctl restart gunicorn` 또는 직접 프로세스 재시작)
- requirements.txt 생성:  
  `pip freeze > requirements.txt`
- DB 초기화 시 업체 등록(signUp)부터 다시 진행 필요

---

## 사전 DB 설정용 커맨드

챗봇 AI 프로세스의 원활한 구동을 위해서 프로세스 구동에 필요한 데이터를 DB에 미리 구축하는 커맨드를 설계하였습니다.

### 1. 챗봇 추천에 활용될 사전 cafe data 등록

추천 챗봇 기능을 시연하기 위해 한국 공공 데이터 파일에서 서울시의 카페 데이터를 받아서 DB에 사전 등록합니다.

```bash
python manage.py upload_cafes
```

### 2. 챗봇 운영을 위한 사전 등록한 cafe의 review data 등록

추천 챗봇 기능을 시연하기 사전 등록한 카페들의 리뷰 데이터를 크롤링하고 DB에 사전 등록합니다.

```bash
python manage.py crawl_reviews
```

### 3. 카페 이미지 dummy data 등록

카페 이미지로 활용될 dummy data를 카페 DB에 일괄 등록합니다.

```bash
python manage.py upload_cafe_images
```

### 4. 카페 설명 데이터 구축

카페 추천 챗봇의 임베딩에 활용될 카페 설명 데이터를 카페의 리뷰 데이터를 기반으로 OpenAi 프롬프트를 활용해 생성하고 DB에 저장합니다.

```bash
python manage.py generate_descriptions
```

- 카페의 description을 OpenAi를 활용해 생성하고 DB에 일괄 등록합니다.

### 5. 카페 임베딩 데이터 구축

카페 추천 챗봇의 임베딩 검색을 위해 모든 카페의 임베딩 벡터를 미리 생성하여 DB에 저장합니다.

```bash
python manage.py embed_cafes
```

- 모든 카페의 설명/키워드를 OpenAI 임베딩으로 변환하여 DB에 저장합니다.
- FAISS 인덱스 구축에 필요한 벡터 데이터를 준비합니다.

### 6. 카페 태그/키워드 사전 데이터 구축

카페 정보 생성에 활용되는 태그와 키워드를 미리 등록합니다.

```bash
python manage.py generate_tag_ratings
python manage.py generate_keywords
```

- 카페를 설명하는 태그와 키워드를 DB에 일괄 등록합니다.

---

**위 커맨드들은 서비스 초기화, 테스트, 운영 환경 구축 시 빠르고 효율적인 데이터 준비를 위해 사용됩니다.**
