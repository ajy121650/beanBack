from django.core.management.base import BaseCommand
from concurrent.futures import ThreadPoolExecutor, as_completed
from cafe.models import Cafe, CafeTagRating
from review.models import Review
from tag.models import Tag
from cafe.utils.gpt import review_description
import time
from openai import RateLimitError

def get_review_keywords_with_retry(text, retries=3):
    for i in range(retries):
        try:
            return review_description(text)
        except RateLimitError:
            wait = 60
            print(f"RateLimitError, retry in {wait}s…")
            time.sleep(wait)
    raise RuntimeError("GPT 호출 재시도 모두 실패")

def process_description(cafe):
    reviews = Review.objects.filter(cafe=cafe)
    combined = "\n".join(r.content for r in reviews).strip()
    if not combined:
        return cafe.pk, None

    desc = review_description(combined)
    return cafe.pk, desc

class Command(BaseCommand):
    help = "Generate and save GPT-based cafe descriptions (multi‐threaded)"

    def handle(self, *args, **options):
        cafes = list(Cafe.objects.all())

        with ThreadPoolExecutor(max_workers=5) as pool:
            futures = {pool.submit(process_description, cafe): cafe for cafe in cafes}

            for future in as_completed(futures):
                cafe = futures[future]
                try:
                    pk, description = future.result()
                    if not description:
                        self.stdout.write(f"[{cafe.name}] mo review → skip")
                    else:
                        # DB update in main thread
                        Cafe.objects.filter(pk=pk).update(description=description)
                        self.stdout.write(f"[{cafe.name}] saved")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"[{cafe.name}] error: {e}"))

