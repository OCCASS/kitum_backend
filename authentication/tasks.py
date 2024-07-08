from io import BytesIO

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

User = get_user_model()


def _get_text_dimensions(text_string, font):
    """Получить размеры текста"""

    _, descent = font.getmetrics()
    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent
    return text_width, text_height


@shared_task
def generate_profile_image_for_user_task(user_id: str, size=128):
    user = User.objects.get(id=user_id)
    image = Image.new("RGB", (size, size), color="#c6c6c6")
    draw = ImageDraw.Draw(image)

    font_path = settings.STATIC_ROOT / "arial.ttf"
    font = ImageFont.truetype(font_path, size // 2)

    initials = f"{user.first_name[0]}{user.last_name[0]}"

    text_width, text_height = _get_text_dimensions(initials, font)
    position = ((size - text_width) / 2, (size - text_height) / 2)
    draw.text(position, initials, fill="#ebebeb", font=font)

    image_io = BytesIO()
    image.save(image_io, format="PNG")
    file = ContentFile(image_io.getvalue(), f"{user.id}.png")
    user.avatar = file
    user.save()
