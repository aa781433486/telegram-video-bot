import io
from PIL import Image, ImageFilter, ImageEnhance

MAX_SIDE = 4096


def upscale_image(image_bytes: bytes) -> bytes:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    orig_w, orig_h = img.size

    scale = 4
    new_w = orig_w * scale
    new_h = orig_h * scale

    if max(new_w, new_h) > MAX_SIDE:
        ratio = MAX_SIDE / max(new_w, new_h)
        new_w = int(new_w * ratio)
        new_h = int(new_h * ratio)

    upscaled = img.resize((new_w, new_h), Image.LANCZOS)

    sharpened = upscaled.filter(
        ImageFilter.UnsharpMask(radius=1.5, percent=150, threshold=3)
    )

    contrast = ImageEnhance.Contrast(sharpened)
    enhanced = contrast.enhance(1.08)

    color = ImageEnhance.Color(enhanced)
    final = color.enhance(1.05)

    output = io.BytesIO()
    final.save(output, format="JPEG", quality=97, optimize=True)
    output.seek(0)
    return output.getvalue()
