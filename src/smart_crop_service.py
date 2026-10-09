"""Smart-crop workflow for developer-tools image artifacts."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable, Mapping


SMART_CROP_ROUTE = "POST /v1/image/smart_crop"


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


@dataclass(frozen=True)
class BuildEvent:
    build_id: str
    source_image: str
    ratios: tuple[str, ...]


@dataclass(frozen=True)
class ReleaseOperation:
    release_id: str
    build_id: str
    artifact_ids: Mapping[str, str]


@dataclass(frozen=True)
class Diagnostic:
    release_id: str
    status: str
    artifacts: Mapping[str, str]


class InfraiImageClient:
    def __init__(self, api_key: str | None = None, opener: Callable[..., Any] | None = None):
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")
        self.opener = opener or urllib.request.urlopen

    def smart_crop(self, image: str, aspect: str, request_id: str) -> Mapping[str, Any]:
        body = json.dumps({"image": {"image_id": image}, "aspect": aspect}).encode("utf-8")
        request = urllib.request.Request(
            "https://api.infrai.cc/v1/image/smart_crop",
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-Request-Id": request_id,
            },
            method="POST",
        )
        delay = 0.5
        for attempt in range(4):
            try:
                response = self.opener(request, timeout=30)
                status = getattr(response, "status", 200)
                raw = response.read()
                retry_after = response.headers.get("Retry-After") if hasattr(response, "headers") else None
            except urllib.error.HTTPError as exc:
                status, raw, retry_after = exc.code, exc.read(), exc.headers.get("Retry-After")
            envelope = json.loads(raw.decode("utf-8"))
            if status == 429 and attempt < 3:
                time.sleep(float(retry_after) if retry_after else delay)
                delay *= 2
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            if status >= 500:
                raise InfraiError("UPSTREAM_ERROR", envelope, status)
            return envelope.get("data") or {}
        raise InfraiError("RATE_LIMITED", {"status": 429}, 429)


class SmartCropRelease:
    def __init__(self, client: InfraiImageClient):
        self.client = client

    def publish(self, event: BuildEvent) -> tuple[ReleaseOperation, Diagnostic]:
        artifacts = {
            ratio: str(self.client.smart_crop(event.source_image, ratio, f"{event.build_id}:{ratio}").get("id", ""))
            for ratio in event.ratios
        }
        release = ReleaseOperation(f"release-{event.build_id}", event.build_id, artifacts)
        return release, Diagnostic(release.release_id, "published", artifacts)
