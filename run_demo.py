import json
import sys

from src.smart_crop_service import BuildEvent, InfraiImageClient, SmartCropRelease


def main() -> int:
    image = sys.argv[1] if len(sys.argv) > 1 else "image-id"
    event = BuildEvent("build-2026-09-08", image, ("1:1", "4:3", "16:9"))
    release, diagnostic = SmartCropRelease(InfraiImageClient()).publish(event)
    print(json.dumps({"release": release.__dict__, "diagnostic": diagnostic.__dict__}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

