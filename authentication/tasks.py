from io import BytesIO

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

User = get_user_model()


def _get_text_position(size: int, text: str, font):
    left, top, right, bottom = font.getbbox(text)
    width = right - left
    left = (size - width) / 2.0
    # I just don't know why 2.7, but it seems to be the good ratio
    height = bottom - top
    top = (size - height) / 2.7
    return left, top


@shared_task
def generate_profile_image_for_user_task(user_id: str, size=128):
    user = User.objects.get(id=user_id)
    image = Image.new("RGB", (size, size), color="#c6c6c6")
    draw = ImageDraw.Draw(image)

    font_path = settings.STATIC_ROOT / "arial.ttf"
    font = ImageFont.truetype(font_path, size // 2)

    initials = f"{user.first_name[0]}{user.last_name[0]}"
    draw.text(
        _get_text_position(size, initials, font), initials, fill="#ebebeb", font=font
    )

    image_io = BytesIO()
    image.save(image_io, format="PNG")
    file = ContentFile(image_io.getvalue(), f"{user.id}.png")
    user.avatar = file
    user.save()
