# review/management/commands/crawl_reviews.py
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, close_old_connections

from cafe.models import Cafe
from review.models import Review
from review.utils.crawling import get_reviews_by_cafe_name


class Command(BaseCommand):
    help = "모든 카페에 대해 리뷰를 크롤링하여 저장합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--max-workers",
            type=int,
            default=3,
            help="동시에 크롤링할 스레드(worker) 수 (기본: 3)"
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=60,
            help="bulk_create batch size (기본: 60)"
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="처리할 카페 수를 제한 (디버그/부분 실행용)"
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="DB에 저장하지 않고 크롤링만 수행"
        )
        parser.add_argument(
            "--retries",
            type=int,
            default=3,
            help="카페별 크롤링 실패 시 재시도 횟수 (기본: 3)"
        )
        parser.add_argument(
            "--starts-with",
            type=str,
            default=None,
            help="카페명 prefix로 필터링해 일부 카페만 크롤링"
        )

    def handle(self, *args, **options):
        max_workers = options["max_workers"]
        batch_size = options["batch_size"]
        limit = options["limit"]
        dry_run = options["dry_run"]
        retries = options["retries"]
        starts_with = options["starts_with"]

        qs = Cafe.objects.all().order_by("id")
        if starts_with:
            qs = qs.filter(name__startswith=starts_with)
        if limit:
            qs = qs[:limit]

        cafes = list(qs)
        if not cafes:
            self.stdout.write(self.style.WARNING("대상 카페가 없습니다."))
            return

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"크롤링 시작: 대상 카페 {len(cafes)}개 · workers={max_workers} · batch_size={batch_size} · dry_run={dry_run}"
            )
        )

        total_created = 0
        total_errors = 0

        # 스레드 워커에서 DB 커넥션 안전하게 사용
        def crawl_and_save_one_cafe(cafe) -> Dict:
            """
            1) close_old_connections()로 워커 스레드에서 DB 연결 안전화
            2) 크롤링
            3) Review 인스턴스 만들고 bulk_create
            """
            close_old_connections()

            def crawl_with_retry(try_left: int):
                try:
                    reviews = get_reviews_by_cafe_name(cafe.name)
                    return reviews
                except Exception as e:
                    if try_left > 1:
                        self.stdout.write(f"[재시도] {cafe.name} ({retries - try_left + 1}/{retries}) - {e}")
                        return crawl_with_retry(try_left - 1)
                    raise

            try:
                reviews_texts = crawl_with_retry(retries)
                if not reviews_texts:
                    return {"cafe": cafe.name, "created": 0}

                if dry_run:
                    # 저장 안 하고 개수만 보고
                    return {"cafe": cafe.name, "created": len(reviews_texts)}

                # 생성할 Review 객체 준비 (가능하면 bulk_create)
                objs = [
                    Review(
                        user=None,     # 필요 시 로직에 맞게 지정
                        cafe=cafe,
                        content=txt
                    )
                    for txt in reviews_texts
                ]

                # 트랜잭션: 카페 하나 단위로 묶어 안전하게
                with transaction.atomic():
                    # 중복 방지가 필요하면 unique 제약/해시를 모델에 두거나,
                    # 여기서 중복 필터링을 추가하세요.
                    Review.objects.bulk_create(
                        objs,
                        batch_size=batch_size,
                        ignore_conflicts=True  # unique 제약이 있으면 충돌 무시
                    )
                return {"cafe": cafe.name, "created": len(objs)}

            except Exception as e:
                return {"cafe": cafe.name, "error": f"{e}\n{traceback.format_exc()}"}

        # 병렬 실행
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_cafe = {executor.submit(crawl_and_save_one_cafe, cafe): cafe for cafe in cafes}

            for future in as_completed(future_to_cafe):
                res = future.result()
                cafe_name = res.get("cafe", "(unknown)")
                if "error" in res:
                    total_errors += 1
                    self.stdout.write(self.style.ERROR(f"[실패] {cafe_name}\n{res['error']}"))
                else:
                    created = res.get("created", 0)
                    total_created += created
                    self.stdout.write(self.style.SUCCESS(f"[성공] {cafe_name}: {created}건 생성"))

        self.stdout.write(
            self.style.SUCCESS(
                f"완료: 총 생성 {total_created}건 · 실패 {total_errors}건 · dry_run={dry_run}"
            )
        )
