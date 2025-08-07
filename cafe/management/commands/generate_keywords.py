from django.core.management.base import BaseCommand
from cafe.models import Cafe, CafeTagRating
from review.models import Review
from tag.models import Tag
from cafe.utils.gpt import review_keyword
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from openai import RateLimitError

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

def get_review_keywords_with_retry(text, retries=3):
    for i in range(retries):
        try:
            return review_keyword(text)
        except RateLimitError:
            wait = 60  # 60s
            print(f"RateLimitError, retry in {wait}s…")
            time.sleep(wait)
    raise RuntimeError("GPT 호출 재시도 모두 실패")

def process_keyword(cafe):
    reviews = Review.objects.filter(cafe=cafe)
    combined = "\n".join(r.content for r in reviews).strip()
    if not combined:
        return cafe.pk, []
    raw = get_review_keywords_with_retry(combined)
    if any(isinstance(x, list) for x in raw):
        keywords = flatten_once(raw)
    else:
        keywords = raw
    return cafe.pk, keywords

class Command(BaseCommand):
    help = "Generate and save GPT-based keywords for each cafe"

    def handle(self, *args, **options):
        cafes = list(Cafe.objects.all())

        with ThreadPoolExecutor(max_workers=5) as pool:
            futures = {pool.submit(process_keyword, cafe): cafe for cafe in cafes}

            for future in as_completed(futures):
                cafe = futures[future]
                try:
                    pk, keywords = future.result()
                    if not keywords:
                        self.stdout.write(f"[{cafe.name}] no review → skip")
                        continue

                    tag_objs = []
                    for content in keywords:
                        tag, _ = Tag.objects.get_or_create(content=content)
                        tag_objs.append(tag)

                    Cafe.objects.get(pk=pk).keywords.set(tag_objs)
                    self.stdout.write(f"[{cafe.name}] saved  → {keywords}")

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"[{cafe.name}] error: {e}"))
