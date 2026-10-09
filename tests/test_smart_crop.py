import json

from src.smart_crop_service import BuildEvent, InfraiImageClient, SmartCropRelease


class Response:
    status = 200
    headers = {}

    def __init__(self, payload):
        self.payload = payload

    def read(self):
        return json.dumps({"ok": True, "data": {"id": self.payload}, "error": None, "metadata": {}}).encode()


def test_release_publishes_each_requested_ratio():
    calls = []

    def opener(request, timeout):
        body = json.loads(request.data)
        calls.append((request.method, body, request.headers["Authorization"]))
        return Response(f"crop-{body['aspect']}")

    release, diagnostic = SmartCropRelease(InfraiImageClient("test-key", opener)).publish(
        BuildEvent("b7", "source-42", ("1:1", "16:9"))
    )
    assert release.artifact_ids == {"1:1": "crop-1:1", "16:9": "crop-16:9"}
    assert diagnostic.status == "published"
    assert all(method == "POST" for method, _, _ in calls)
    assert all(body["image"] == {"image_id": "source-42"} for _, body, _ in calls)
    assert all(auth == "Bearer test-key" for _, _, auth in calls)
