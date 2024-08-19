from django.conf import settings
from requests import Session

config = settings.KINESCOPE


class CreatingEventError(Exception):
    pass


def create_event(name: str) -> str:
    """Create kinescope stream event"""

    body = {
        "name": name,
        "type": config["STREAM"]["type"],
        "protected": True,
        "record": {"parent_id": config["PROJECT_ID"]},
        "video": {"presets": config["STREAM"]["video_presets"]},
        "latency_mode": "reduced",
        "show_members": False,
        "chat_active": False,
        "chat_after_stream": True,
        "chat_preview": True,
    }
    url = config["API_BASE"] + "/v2/live/events"
    headers = {"Authorization": f"Bearer {config['API_TOKEN']}"}

    with Session() as session:
        with session.post(url, headers=headers, json=body) as response:
            data = response.json()

            if response.status_code != 200:
                raise CreatingEventError(
                    f"Ошибка создания события. Ответ сервера: {data}"
                )

            # stream id is stored only in play_link as param
            stream_id = data["data"]["play_link"].split("/")[-1]
            return stream_id
