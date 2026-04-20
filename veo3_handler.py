import os
import time
import asyncio
import io
import requests

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


async def generate_video_from_text(prompt: str, progress_callback=None) -> bytes:
    if not GOOGLE_API_KEY:
        raise Exception("مفتاح Google API غير مضبوط. يرجى إضافة GOOGLE_API_KEY في الإعدادات.")

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=GOOGLE_API_KEY)

        if progress_callback:
            await progress_callback("🎬 جاري إرسال الطلب إلى Veo 3 AI...")

        operation = client.models.generate_video(
            model="veo-3.0-generate-preview",
            prompt=prompt,
            config=types.GenerateVideoConfig(
                aspect_ratio="16:9",
                duration_seconds=8,
                number_of_videos=1,
            ),
        )

        if progress_callback:
            await progress_callback("⏳ جاري توليد الفيديو (قد يستغرق 1-3 دقائق)...")

        await asyncio.sleep(10)

        max_wait = 200
        waited = 0
        while not operation.done and waited < max_wait:
            await asyncio.sleep(15)
            waited += 15
            try:
                operation = client.operations.get(operation)
            except Exception:
                pass

        if not operation.done:
            raise Exception("انتهت المهلة. حاول مرة أخرى.")

        if progress_callback:
            await progress_callback("✅ الفيديو جاهز! جاري التحميل...")

        video = operation.result.generated_videos[0].video
        video_bytes = video.video_bytes
        if not video_bytes and hasattr(video, 'uri'):
            resp = requests.get(video.uri, timeout=60)
            video_bytes = resp.content

        return video_bytes

    except ImportError:
        raise Exception("مكتبة google-genai غير مثبتة. يرجى المحاولة مرة أخرى.")


async def generate_video_from_image(image_bytes: bytes, prompt: str, progress_callback=None) -> bytes:
    if not GOOGLE_API_KEY:
        raise Exception("مفتاح Google API غير مضبوط. يرجى إضافة GOOGLE_API_KEY في الإعدادات.")

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=GOOGLE_API_KEY)

        if progress_callback:
            await progress_callback("🎬 جاري إرسال الصورة إلى Veo 3 AI...")

        operation = client.models.generate_video(
            model="veo-3.0-generate-preview",
            image=types.Image(image_bytes=image_bytes, mime_type="image/jpeg"),
            config=types.GenerateVideoConfig(
                prompt=prompt,
                aspect_ratio="16:9",
                duration_seconds=8,
                number_of_videos=1,
            ),
        )

        if progress_callback:
            await progress_callback("⏳ جاري تحويل الصورة إلى فيديو (قد يستغرق 1-3 دقائق)...")

        await asyncio.sleep(10)

        max_wait = 200
        waited = 0
        while not operation.done and waited < max_wait:
            await asyncio.sleep(15)
            waited += 15
            try:
                operation = client.operations.get(operation)
            except Exception:
                pass

        if not operation.done:
            raise Exception("انتهت المهلة. حاول مرة أخرى.")

        if progress_callback:
            await progress_callback("✅ الفيديو جاهز! جاري التحميل...")

        video = operation.result.generated_videos[0].video
        video_bytes = video.video_bytes
        if not video_bytes and hasattr(video, 'uri'):
            resp = requests.get(video.uri, timeout=60)
            video_bytes = resp.content

        return video_bytes

    except ImportError:
        raise Exception("مكتبة google-genai غير مثبتة. يرجى المحاولة مرة أخرى.")
