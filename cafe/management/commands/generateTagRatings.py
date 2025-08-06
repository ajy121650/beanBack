from django.core.management.base import BaseCommand
from cafe.models import Cafe, CafeTagRating
from review.models import Review
from tag.models import Tag
from cafe.utils.gpt import review_tag_rating
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from openai import RateLimitError

def get_review_tag_rating_with_retry(text, retries=3):
    for i in range(retries):
        try:
            return review_tag_rating(text)
        except RateLimitError:
            wait = 60  # 60s
            print(f"RateLimitError, retry in {wait}s…")
            time.sleep(wait)
    raise RuntimeError("GPT 호출 재시도 모두 실패")


def process_tag_rating(cafe):
    reviews = Review.objects.filter(cafe=cafe)
    combined = "\n".join(r.content for r in reviews).strip()
    if not combined:
        return None
    
    return get_review_tag_rating_with_retry(combined)

class Command(BaseCommand):
    help = "Generate and save GPT-based CafeTagRating for each cafe"

    def handle(self, *args, **options):
        cafes = list(Cafe.objects.all())

        with ThreadPoolExecutor(max_workers=5) as pool:
            futures = {pool.submit(process_tag_rating, cafe): cafe for cafe in cafes}
            time.sleep(5)

            for future in as_completed(futures):
                cafe = futures[future]
                try:
                    ratings = future.result()
                    if not ratings:
                        self.stdout.write(f"[{cafe.name}] no review → skip")
                        continue
                    
                    # DB 저장
                    for tag_name, score in ratings.items():
                        tag_obj, _ = Tag.objects.get_or_create(content=tag_name)
                        CafeTagRating.objects.update_or_create(
                            cafe=cafe,           # ← 여기!
                            tag=tag_obj,
                            defaults={"rating": score}
                        )
                    self.stdout.write(f"[{cafe.name}] saved")
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"[{cafe.name}] error: {e}"))
