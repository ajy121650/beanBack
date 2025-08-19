import json
import os
import sys
import traceback
from typing import List

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, IntegrityError

from cafe.models import Cafe  # 모델 경로는 프로젝트 구조에 맞게 조정


class Command(BaseCommand):
    help = "Load cafes from a JSON file and insert into DB."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            "-f",
            default="data/cafe_opened_data.json",
            help="Path to the JSON file. Default: data/cafe_opened_data.json",
        )
        parser.add_argument(
            "--batch-size",
            "-b",
            type=int,
            default=500,
            help="bulk_create batch size (default: 500)",
        )
        parser.add_argument(
            "--update-existing",
            action="store_true",
            help="If a cafe with same (name, address) exists, update it instead of skipping.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and validate only, do not write to DB.",
        )

    def handle(self, *args, **options):
        file_path = options["file"]
        batch_size = options["batch_size"]
        update_existing = options["update_existing"]
        dry_run = options["dry_run"]

        if not os.path.exists(file_path):
            raise CommandError(f"File not found: {file_path}")

        # 1) JSON 로드
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            raise CommandError(f"Invalid JSON format: {exc}") from exc
        except Exception as exc:
            raise CommandError(f"Failed to open file: {exc}") from exc

        if not isinstance(data, list):
            raise CommandError("JSON root must be a list of objects.")

        # 2) 변환 & 유효성 체크
        payload: List[dict] = []
        skipped = 0
        for item in data:
            name = item.get("bplcnm")
            address = item.get("rdnwhladdr")
            if not name or not address:
                skipped += 1
                continue

            payload.append(
                {
                    "name": name,
                    "address": address,
                    "description": "",
                    "average_rating": 0.0,
                    "photo_urls": [],  # 모델이 JSONField/ArrayField 라고 가정
                }
            )

        total = len(payload)
        self.stdout.write(self.style.NOTICE(f"Parsed {total} items (skipped {skipped} invalid)."))
        if dry_run:
            self.stdout.write(self.style.SUCCESS("[DRY RUN] No DB writes performed."))
            return

        created = 0
        updated = 0

        # 3) 쓰기 전략
        # - update_existing: name+address 동일 시 update, 아니면 생성
        # - 아니면 bulk_create 로 빠르게 삽입 (unique 제약이 있으면 ignore_conflicts 활용 가능)
        try:
            if update_existing:
                # 업데이트/생성 1건씩 처리 (대량이면 속도 느릴 수 있음)
                with transaction.atomic():
                    for row in payload:
                        obj, is_created = Cafe.objects.update_or_create(
                            name=row["name"],
                            address=row["address"],
                            defaults={
                                "description": row["description"],
                                "average_rating": row["average_rating"],
                                "photo_urls": row["photo_urls"],
                            },
                        )
                        if is_created:
                            created += 1
                        else:
                            updated += 1
            else:
                # 빠른 대량 삽입: 이미 존재하면 에러날 수 있으므로 unique 제약이 있다면 ignore_conflicts=True 고려
                objs = [
                    Cafe(
                        name=row.get("name"),
                        address=row.get("address"),
                        description="",
                        average_rating=0.0,
                        photo_urls=[]
                    ) for row in payload
                ]
                # unique (name, address) 같은 제약이 없다면 아래 그대로 사용
                # unique가 있고 중복 있을 수 있으면: ignore_conflicts=True 사용 (단, 어떤 레코드가 건너뛰었는지 카운트 못 함)
                for i in range(0, len(objs), batch_size):
                    chunk = objs[i : i + batch_size]
                    Cafe.objects.bulk_create(chunk, batch_size=batch_size)
                    created += len(chunk)

            self.stdout.write(self.style.SUCCESS(f"Done. created={created}, updated={updated}"))

        except IntegrityError as exc:
            # unique 제약 등으로 실패한 경우
            self.stderr.write(self.style.ERROR(f"IntegrityError: {exc}"))
            raise
        except Exception as exc:
            self.stderr.write(self.style.ERROR("Unexpected error while writing to DB"))
            self.stderr.write(traceback.format_exc())
            raise CommandError(str(exc))