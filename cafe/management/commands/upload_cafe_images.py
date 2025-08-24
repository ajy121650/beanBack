# cafe/management/commands/update_cafe_images.py
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from cafe.models import Cafe

# 카페 이미지 업데이트 함수
class Command(BaseCommand):
    help = "모든 카페의 이미지를 일괄 업데이트합니다. (라운드로빈)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--base-path",
            default="/data/cafe_images/",
            help="이미지 파일들이 있는 베이스 경로 (기본: /data/cafe_images/)",
        )
        parser.add_argument(
            "--image-len",
            type=int,
            default=132,
            help="사용 가능한 이미지 파일 개수 (기본: 132, 즉 1.jpg ~ 132.jpg)",
        )
        parser.add_argument(
            "--per-cafe",
            type=int,
            default=3,
            help="카페당 할당할 이미지 개수 (기본: 3)",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=500,
            help="bulk_update 배치 크기 (기본: 500)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="DB에 저장하지 않고 어떤 값이 설정될지 로그만 출력",
        )

    def handle(self, *args, **options):
        base_path: str = options["base_path"].rstrip("/") + "/"
        image_len: int = options["image_len"]
        per_cafe: int = options["per_cafe"]
        batch_size: int = options["batch_size"]
        dry_run: bool = options["dry_run"]

        if image_len <= 0:
            raise CommandError("--image-len 은 1 이상의 정수여야 합니다.")

        cafes = Cafe.objects.all().only("id", "photo_urls")
        total = cafes.count()
        if total == 0:
            self.stdout.write(self.style.WARNING("업데이트할 카페가 없습니다."))
            return

        idx = 0
        updated_objs = []
        processed = 0

        self.stdout.write(
            f"[시작] 총 {total}개 카페 | base_path={base_path} image_len={image_len} per_cafe={per_cafe} "
            f"{'(dry-run)' if dry_run else ''}"
        )

        for cafe in cafes.iterator(chunk_size=1000):
            photo_urls = []
            for _ in range(per_cafe):
                photo_index = (idx % image_len) + 1
                photo_url = f"{base_path}{photo_index}.jpg"
                photo_urls.append(photo_url)
                idx += 1

            cafe.photo_urls = photo_urls
            updated_objs.append(cafe)
            processed += 1

            # 진행 로그(간단)
            if processed % 500 == 0 or processed == total:
                self.stdout.write(f"  진행: {processed}/{total}")

            # 배치 저장
            if not dry_run and len(updated_objs) >= batch_size:
                with transaction.atomic():
                    Cafe.objects.bulk_update(updated_objs, ["photo_urls"], batch_size=batch_size)
                updated_objs.clear()

        # 남은 것 저장
        if not dry_run and updated_objs:
            with transaction.atomic():
                Cafe.objects.bulk_update(updated_objs, ["photo_urls"], batch_size=batch_size)

        self.stdout.write(
            self.style.SUCCESS(
                f"[완료] 총 {processed}개 카페에 이미지 {'미리보기만 수행(dry-run)' if dry_run else '업데이트'}"
            )
        )