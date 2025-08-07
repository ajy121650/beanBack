from django.core.management.base import BaseCommand
from cafe.models import Cafe
from django.conf import settings

import openai
import numpy as np
import concurrent.futures
from django.db import close_old_connections

openai.api_key = settings.OPENAI_API_KEY

def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    response = openai.embeddings.create(
        model=model,
        input=[text]
    )
    return response.data[0].embedding

def process_cafe(cafe):
    # 각 스레드에서 새로운 DB 커넥션을 사용하도록
    close_old_connections()
    try:
        embedding_addr_text = f"{cafe.address}"
        embedding_desc_text = f"{cafe.description}"
        addr_vec = get_embedding(embedding_addr_text)
        desc_vec = get_embedding(embedding_desc_text)

        addr_arr = np.array(addr_vec, dtype="float32")
        desc_arr = np.array(desc_vec, dtype="float32")

        combined_arr = 0.5 * addr_arr + 0.5 * desc_arr

        vec = combined_arr.tolist()

        cafe.embeddings = vec
        cafe.save()
        print(f"[OK] Cafe {cafe.id}: {cafe.name}")
    except Exception as e:
        print(f"[ERROR] Cafe {cafe.id}: {e}")
    finally:
        # 작업 후 커넥션 닫기
        close_old_connections()

class Command(BaseCommand):
    help = "Embed cafe descriptions (with address) in parallel"

    def handle(self, *args, **kwargs):
        cafes = list(Cafe.objects.exclude(description=""))
        total = len(cafes)
        print(f"[INFO] 벡터화할 카페 수: {total}")

        # 최대 10개 스레드로 동시에 처리
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(process_cafe, cafe): cafe.id for cafe in cafes}
            for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
                # 진행률 출력 (선택)
                print(f"[PROGRESS] {i}/{total} 완료")

        print("[DONE] 모든 카페 임베딩 저장 완료.")