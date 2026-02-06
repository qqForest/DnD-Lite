import asyncio
import os
import uuid

from yandex_cloud_ml_sdk import YCloudML

from app.config import get_settings
from app.core.avatar import AVATAR_STYLE_PROMPT


async def generate_avatar(appearance_description: str) -> str:
    """Generate a character avatar using YandexART and return the file URL."""
    settings = get_settings()

    if not settings.yandex_art_folder_id or not settings.yandex_art_api_key:
        raise ValueError("YandexART credentials not configured")

    sdk = YCloudML(
        folder_id=settings.yandex_art_folder_id,
        auth=settings.yandex_art_api_key,
    )

    model = sdk.models.image_generation("yandex-art").configure(
        width_ratio=1,
        height_ratio=1,
    )

    operation = model.run_deferred([AVATAR_STYLE_PROMPT, appearance_description])
    try:
        result = await asyncio.to_thread(operation.wait)
    except Exception as e:
        err_str = str(e)
        if "PERMISSION_DENIED" in err_str:
            raise ValueError("Недостаточно средств на аккаунте Yandex Cloud")
        raise

    avatar_dir = os.path.join("uploads", "avatars")
    os.makedirs(avatar_dir, exist_ok=True)

    filename = f"{uuid.uuid4()}.jpeg"
    filepath = os.path.join(avatar_dir, filename)

    with open(filepath, "wb") as f:
        f.write(result.image_bytes)

    return f"/uploads/avatars/{filename}"
