import random
from io import BytesIO

from celery import shared_task
from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


def _get_text_position(size: int, text: str, font):
    left, top, right, bottom = font.getbbox(text)
    width = right - left
    left = (size - width) / 2.0
    # I just don't know why 2.4, but it seems to be the good ratio
    height = bottom - top
    top = (size - height) / 2.4
    return left, top


def _select_color():
    return random.choice(settings.PROFILE_IMAGE_COLORS)


@shared_task
def generate_profile_image_for_user_task(user, size=128):
    color = _select_color()
    image = Image.new("RGB", (size, size), color=color["background"])
    draw = ImageDraw.Draw(image)

    font_path = settings.STATIC_ROOT / "arial.ttf"
    font = ImageFont.truetype(font_path, size * 0.4)

    initials = f"{user.first_name[0]}{user.last_name[0]}"
    draw.text(
        _get_text_position(size, initials, font),
        initials,
        fill=color["text"],
        font=font,
    )

    image_io = BytesIO()
    image.save(image_io, format="webp")
    file = ContentFile(image_io.getvalue(), f"{user.id}.webp")
    user.avatar = file
    user.save()
