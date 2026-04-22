import os
import asyncio
import requests

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

BASE_URL = "https://generativelanguage.googleapis.com"


async def _poll_operation(operation_name: str, progress_callback=None) -> dict:
    url = f"{BASE_URL}/v1beta/{operation_name}"
    headers = {"x-goog-api-key": GOOGLE_API_KEY}

    max_wait = 300
    waited = 0
    interval = 10

    while waited < max_wait:
        await asyncio.sleep(interval)
        waited += interval

        try:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            continue

        if data.get("done"):
            return data

        if progress_callback:
            elapsed = waited
            await progress_callback(f"⏳ جاري التوليد... ({elapsed} ثانية)")

        interval = min(interval + 5, 20)

    raise Exception("انتهت مهلة الانتظار (5 دقائق). حاول مرة أخرى لاحقاً.")


async def generate_video_from_text(prompt: str, progress_callback=None) -> bytes:
    if not GOOGLE_API_KEY:
        raise Exception("مفتاح Google API غير مضبوط. يرجى إضافة GOOGLE_API_KEY في الإعدادات.")

    if progress_callback:
        await progress_callback("🎬 جاري إرسال الطلب إلى Veo 3 AI...")

    url = f"{BASE_URL}/v1beta/models/veo-3.0-generate-preview:predictLongRunning"
    headers = {
        "x-goog-api-key": GOOGLE_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "aspectRatio": "16:9",
            "sampleCount": 1,
        },
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        if resp.status_code != 200:
            err = resp.json() if resp.content else {}
            msg = err.get("error", {}).get("message", resp.text[:300])
            raise Exception(f"خطأ من API: {msg}")
        operation = resp.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"فشل الاتصال بـ Veo 3 API: {str(e)}")

    operation_name = operation.get("name")
    if not operation_name:
        raise Exception("لم يتم إرجاع معرف العملية من API.")

    if progress_callback:
        await progress_callback("⏳ جاري توليد الفيديو (قد يستغرق 2-4 دقائق)...")

    result = await _poll_operation(operation_name, progress_callback)

    if "error" in result:
        raise Exception(f"فشل التوليد: {result['error'].get('message', 'خطأ غير معروف')}")

    try:
        videos = result["response"]["generateVideoResponse"]["generatedSamples"]
        video_uri = videos[0]["video"]["uri"]
    except (KeyError, IndexError) as e:
        raise Exception(f"لم يتم العثور على الفيديو في الاستجابة: {str(result)[:300]}")

    if progress_callback:
        await progress_callback("✅ الفيديو جاهز! جاري التحميل...")

    dl_headers = {"x-goog-api-key": GOOGLE_API_KEY}
    video_resp = requests.get(video_uri, headers=dl_headers, timeout=120)
    video_resp.raise_for_status()
    return video_resp.content


async def generate_video_from_image(image_bytes: bytes, prompt: str, progress_callback=None) -> bytes:
    if not GOOGLE_API_KEY:
        raise Exception("مفتاح Google API غير مضبوط. يرجى إضافة GOOGLE_API_KEY في الإعدادات.")

    if progress_callback:
        await progress_callback("🎬 جاري إرسال الصورة إلى Veo 3 AI...")

    import base64
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    url = f"{BASE_URL}/v1beta/models/veo-3.0-generate-preview:predictLongRunning"
    headers = {
        "x-goog-api-key": GOOGLE_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "instances": [
            {
                "prompt": prompt,
                "image": {
                    "bytesBase64Encoded": image_b64,
                    "mimeType": "image/jpeg",
                },
            }
        ],
        "parameters": {
            "aspectRatio": "16:9",
            "sampleCount": 1,
        },
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        if resp.status_code != 200:
            err = resp.json() if resp.content else {}
            msg = err.get("error", {}).get("message", resp.text[:300])
            raise Exception(f"خطأ من API: {msg}")
        operation = resp.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"فشل الاتصال بـ Veo 3 API: {str(e)}")

    operation_name = operation.get("name")
    if not operation_name:
        raise Exception("لم يتم إرجاع معرف العملية من API.")

    if progress_callback:
        await progress_callback("⏳ جاري تحويل الصورة إلى فيديو (قد يستغرق 2-4 دقائق)...")

    result = await _poll_operation(operation_name, progress_callback)

    if "error" in result:
        raise Exception(f"فشل التوليد: {result['error'].get('message', 'خطأ غير معروف')}")

    try:
        videos = result["response"]["generateVideoResponse"]["generatedSamples"]
        video_uri = videos[0]["video"]["uri"]
    except (KeyError, IndexError):
        raise Exception(f"لم يتم العثور على الفيديو في الاستجابة: {str(result)[:300]}")

    if progress_callback:
        await progress_callback("✅ الفيديو جاهز! جاري التحميل...")

    dl_headers = {"x-goog-api-key": GOOGLE_API_KEY}
    video_resp = requests.get(video_uri, headers=dl_headers, timeout=120)
    video_resp.raise_for_status()
    return video_resp.content
