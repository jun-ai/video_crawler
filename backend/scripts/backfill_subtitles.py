"""
补字幕脚本: 从 OSS 下载视频, faster-whisper 转录, 写回 subtitles 表 + 上传 SRT 到 OSS + 触发 interpretation.

用法:
  docker exec english_learning_backend python3 /app/scripts/backfill_subtitles.py --ids 3,4,5 [--dry-run] [--model base]
"""
import asyncio
import argparse
import os
import sys
import time
import json

# Add app to path
sys.path.insert(0, "/app")

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings
from app.models.models import Material, Subtitle
from app.services.video_transcriber import transcribe_video, is_faster_whisper_available
from app.services.subtitle_parser import parse_srt
from app.services.storage import get_storage_service
from app.services.interpretation_tasks import generate_interpretations_for_material
import oss2


async def get_material(db: AsyncSession, material_id: int):
    result = await db.execute(select(Material).where(Material.id == material_id))
    return result.scalar_one_or_none()


async def download_video(material_id: int, video_key: str) -> str:
    """从 OSS 下载视频到 backend 容器本地 /tmp"""
    storage = get_storage_service()
    bucket = storage._get_bucket()
    local_path = f"/tmp/backfill_{material_id}_{int(time.time())}.mp4"
    print(f"  下载: {video_key} -> {local_path}")
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: bucket.get_object_to_file(video_key, local_path))
    size = os.path.getsize(local_path)
    print(f"  下载完成: {size / 1024 / 1024:.2f} MB")
    return local_path


def upload_srt(srt_content: str, material_id: int) -> str:
    """上传 SRT 到 OSS, 返回 object key"""
    import secrets
    storage = get_storage_service()
    bucket = storage._get_bucket()
    key = f"subtitles/2026/06/backfill_{material_id}_{int(time.time())}_{secrets.token_hex(4)}.srt"
    print(f"  上传 SRT -> {key}")
    loop = asyncio.get_event_loop()
    srt_bytes = srt_content.encode("utf-8")
    loop.run_until_complete if False else None  # we'll use sync put
    # Use sync put
    bucket.put_object(key, srt_bytes, headers={"Content-Type": "text/plain; charset=utf-8"})
    return key


async def do_one(db: AsyncSession, material_id: int, model_size: str, dry_run: bool):
    print(f"\n=== Material {material_id} ===")
    material = await get_material(db, material_id)
    if not material:
        print(f"  ✗ Material {material_id} not found")
        return False

    print(f"  title: {material.title[:50]}")
    print(f"  video_path: {material.video_path}")
    print(f"  subtitle_path: {material.subtitle_path!r}")
    print(f"  interpretation_status: {material.interpretation_status}")

    # Check: already has subtitles?
    sub_count_result = await db.execute(
        select(Subtitle).where(Subtitle.material_id == material_id).limit(1)
    )
    if sub_count_result.scalar_one_or_none():
        cnt = (await db.execute(
            select(Subtitle.id).where(Subtitle.material_id == material_id)
        )).all()
        print(f"  ⚠ 已有 {len(cnt)} 条字幕, 跳过")
        return False

    if dry_run:
        print("  [DRY-RUN] 跳过下载/转录/写库")
        return True

    # 1. Download video
    local_video = await download_video(material_id, material.video_path)

    try:
        # 2. Transcribe
        print(f"  转录中 (model={model_size})...")
        t0 = time.time()
        result = await transcribe_video(
            video_path=local_video,
            model_size=model_size,
            language="en",  # 已知是英语视频
            progress_callback=lambda pct, msg: print(f"    [{pct}%] {msg}"),
        )
        elapsed = time.time() - t0

        if not result.get("success"):
            print(f"  ✗ 转录失败: {result.get('error')}")
            return False

        srt = result["srt"]
        seg_count = result["segment_count"]
        lang = result.get("language", "?")
        print(f"  ✓ 转录完成: {seg_count} 段, 语言={lang}, 耗时 {elapsed:.1f}s")

        # 3. Parse SRT
        subs = parse_srt(srt, material_id)
        print(f"  解析出 {len(subs)} 条字幕")

        if not subs:
            print("  ✗ 字幕解析为空")
            return False

        # 4. Upload SRT to OSS
        srt_key = await asyncio.get_event_loop().run_in_executor(
            None, upload_srt_sync, srt, material_id
        )

        # 5. Insert subtitles
        for s in subs:
            db.add(Subtitle(
                material_id=material_id,
                sequence=s.sequence,
                start_time=s.start_time,
                end_time=s.end_time,
                text_en=s.text_en,
                text_cn=None,
            ))
        material.subtitle_path = srt_key
        material.interpretation_status = "pending"
        await db.commit()
        print(f"  ✓ 写入 {len(subs)} 条字幕, subtitle_path={srt_key}")

        # 6. Trigger interpretation
        print(f"  触发 AI 解读...")
        asyncio.create_task(generate_interpretations_for_material(material_id))
        return True

    finally:
        # Cleanup local
        try:
            os.unlink(local_video)
            print(f"  清理本地 {local_video}")
        except Exception:
            pass


def upload_srt_sync(srt_content: str, material_id: int) -> str:
    """同步上传 SRT"""
    import secrets
    storage = get_storage_service()
    bucket = storage._get_bucket()
    key = f"subtitles/2026/06/backfill_{material_id}_{int(time.time())}_{secrets.token_hex(4)}.srt"
    srt_bytes = srt_content.encode("utf-8")
    bucket.put_object(key, srt_bytes, headers={"Content-Type": "text/plain; charset=utf-8"})
    return key


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", required=True, help="comma-separated material ids, e.g. 3,4,5")
    parser.add_argument("--model", default="base", choices=["tiny", "base", "small"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    ids = [int(x) for x in args.ids.split(",") if x.strip()]
    print(f"开始补字幕: ids={ids}, model={args.model}, dry_run={args.dry_run}")

    if not is_faster_whisper_available():
        print("ERROR: faster-whisper not available")
        sys.exit(1)

    # DB engine
    db_url = settings.database_url
    engine = create_async_engine(db_url, pool_pre_ping=True)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    results = {}
    async with SessionLocal() as db:
        for mid in ids:
            try:
                ok = await do_one(db, mid, args.model, args.dry_run)
                results[mid] = "OK" if ok else "SKIP/FAIL"
            except Exception as e:
                import traceback
                traceback.print_exc()
                results[mid] = f"ERROR: {type(e).__name__}: {str(e)[:200]}"

    print("\n=== 结果 ===")
    for k, v in results.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    asyncio.run(main())