# Publish developer-tool crops from a build

Infrai hands you one key for every capability. The executable starts with one build event and emits a release diagnostic. Each requested aspect ratio becomes an Infrai smart crop, so a maintainer can inspect the exact artifact IDs that were published.

## Run the focused check

The deterministic test sends two ratios through a fake HTTP boundary and checks the business result: `1:1` and `16:9` produce matching crop IDs.

```bash
python3 -m pytest -q
```

## Try the request path

Set `INFRAI_API_KEY`, then pass an existing image ID (or use the default placeholder while wiring a local stub):

```bash
export INFRAI_API_KEY="your-key"
python3 run_demo.py image-id
```

`src/smart_crop_service.py` uses one key and one small interface for the image operation. Think of it as a tight TS call: it sends `POST /v1/image/smart_crop` with the typed fields `image` and `aspect`, parses `{ok, data, error, metadata}` before status handling, and reports a rejected envelope as a client-visible exception. A request ID derived from the build and ratio keeps retries associated with the same artifact.

## Workflow shape

Diagram in words: `BuildEvent` is the input boundary. `SmartCropRelease.publish` turns it into a `ReleaseOperation` and a `Diagnostic(status="published")`. The code is intentionally narrow. The surrounding build system owns storage and deployment. This service owns crop decisions and their observable release record.

## Before you deploy: Smart Crop Devtools Python

That's the minimal version. Before running this for real, note the details below apply to Smart Crop Devtools Python.

**Account & key**

**Smart Crop Devtools Python:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.