import io
import os
import requests
from PIL import Image, ImageFilter, ImageEnhance

MAX_SIDE = 4096
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


def upscale_image(image_bytes: bytes) -> bytes:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    orig_w, orig_h = img.size

    scale = 4
    new_w = min(orig_w * scale, MAX_SIDE)
    new_h = min(orig_h * scale, MAX_SIDE)

    ratio = min(new_w / orig_w, new_h / orig_h)
    new_w = int(orig_w * ratio)
    new_h = int(orig_h * ratio)

    upscaled = img.resize((new_w, new_h), Image.LANCZOS)

    sharpened = upscaled.filter(ImageFilter.UnsharpMask(radius=2, percent=200, threshold=2))

    contrast = ImageEnhance.Contrast(sharpened)
    enhanced = contrast.enhance(1.12)

    color = ImageEnhance.Color(enhanced)
    colored = color.enhance(1.08)

    brightness = ImageEnhance.Brightness(colored)
    brightened = brightness.enhance(1.03)

    sharpness = ImageEnhance.Sharpness(brightened)
    final = sharpness.enhance(2.0)

    output = io.BytesIO()
    final.save(output, format="JPEG", quality=99, optimize=True, subsampling=0)
    output.seek(0)
    return output.getvalue()


def upscale_image_with_ai(image_bytes: bytes) -> bytes:
    if not GOOGLE_API_KEY:
        return upscale_image(image_bytes)

    try:
        import base64
        img_b64 = base64.b64encode(image_bytes).decode("utf-8")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
        headers = {
            "x-goog-api-key": GOOGLE_API_KEY,
            "Content-Type": "application/json",
        }
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": img_b64,
                            }
                        },
                        {
                            "text": (
                                "Please upscale and enhance this image to the highest possible quality. "
                                "Make it sharper, clearer, and more detailed. Return only the enhanced image."
                            )
                        },
                    ]
                }
            ],
            "generationConfig": {"responseModalities": ["image", "text"]},
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        if resp.status_code == 200:
            data = resp.json()
            parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            for part in parts:
                if "inline_data" in part:
                    img_data = base64.b64decode(part["inline_data"]["data"])
                    enhanced = upscale_image(img_data)
                    return enhanced

    except Exception:
        pass

    return upscale_image(image_bytes)
