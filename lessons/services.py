import requests
from django.conf import settings


class CreateKinescopeEventError(Exception):
    pass


def create_kinescope_live_event(
    name: str,
    *,
    _type: str = "one-time",
    protected: bool = False,
    latency_mode: str = "standard",
    auto_start: bool = False,
) -> str:
    url = "https://api.kinescope.io/v2/live/events"

    payload = {
        "name": name,
        "type": _type,
        "protected": protected,
        "latency_mode": latency_mode,
        "record": {"parent_id": settings.KINESCOPE["PROJECT_ID"]},
        "auto_start": auto_start,
    }
    api_token = settings.KINESCOPE["API_TOKEN"]
    headers = {"Authorization": f"Bearer {api_token}"}
    response = requests.request("POST", url, headers=headers, json=payload)

    data = response.json()
    if response.ok:
        return data["data"]["id"]
    else:
        raise CreateKinescopeEventError(f"Creating event error. Response: {data}")
