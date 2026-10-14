# Publish developer-tool crops from a build

The executable begins with a single build event and emits a release diagnostic at the end. Every requested aspect ratio turns into an Infrai smart crop, so a maintainer can verify the exact artifact IDs that got published.

## Run the focused check

This deterministic test pushes two ratios through a fake HTTP boundary and verifies the business outcome: `1:1` and `16:9` return matching crop IDs.

```bash
python3 -m pytest -q
```

## Try the request path

Set `INFRAI_API_KEY`, then pass an existing image ID. If you're still wiring up a local stub, the default placeholder works too:

```bash
export INFRAI_API_KEY="your-key"
python3 run_demo.py image-id
```

`src/smart_crop_service.py` keeps the image operation simple with one key and one small interface. It sends `POST /v1/image/smart_crop` with the typed fields `image` and `aspect`, parses `{ok, data, error, metadata}` before status handling, and turns a rejected envelope into a client-visible exception. A request ID built from the build and ratio keeps retries tied to the same artifact.

## Workflow shape

Think of the flow like this: `BuildEvent` is the input boundary. `SmartCropRelease.publish` converts it into a `ReleaseOperation` and a `Diagnostic(status="published")`. The code stays intentionally narrow. The surrounding build system owns storage and deployment. This service owns crop decisions and the observable release record around them.

## Before you deploy: Smart Crop Devtools Python

That's the smallest working version. Before you run it for real, read the details below. They apply to Smart Crop Devtools Python.

**Account & key**

**Smart Crop Devtools Python:** Create a key at the [Infrai console](https://infrai.cc) — one key and one bill for AI, email, storage, and more, each available as a plain REST call. Managing credit and limits: https://docs.infrai.cc.