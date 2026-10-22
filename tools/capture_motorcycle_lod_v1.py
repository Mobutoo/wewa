"""Capture source/LOD at identical cameras and compare silhouettes; software WebGL only."""
import base64
import hashlib
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "creative/reviews/motorcycle-lod-review-v1"
OUT.mkdir(parents=True, exist_ok=True)
VIEWS = ["quarter", "left", "right", "front", "rear", "cockpit"]


def capture(page, relative):
    encoded = page.evaluate("document.querySelector('canvas').toDataURL('image/png').split(',')[1]")
    raw = base64.b64decode(encoded)
    (OUT / relative).write_bytes(raw)
    return {"path":relative, "sha256":hashlib.sha256(raw).hexdigest(), "bytes":len(raw)}


def main():
    results = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path="/usr/bin/chromium", args=[
            "--no-sandbox", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader",
            "--js-flags=--max-old-space-size=8192",
        ])
        for model in ["lod", "source"]:
            page = browser.new_page(viewport={"width":1280,"height":900})
            errors, failures = [], []
            page.on("pageerror",lambda e:errors.append(str(e)))
            page.on("response",lambda r:failures.append({"url":r.url,"status":r.status}) if r.status>=400 else None)
            page.goto(f"http://127.0.0.1:4143/tools/motorcycle-lod-review-v1/?model={model}&capture=1",wait_until="domcontentloaded",timeout=120000)
            print("OPENED",model,flush=True)
            page.wait_for_function("document.querySelector('#error').textContent || (window.__MOTO_LOD__?.scene.isReady() && window.__MOTO_LOD__.report().textures_ready)",timeout=300000)
            assert not page.locator("#error").inner_text(), page.locator("#error").inner_text()
            page.evaluate("window.__MOTO_LOD__.engine.stopRenderLoop()")
            report = page.evaluate("window.__MOTO_LOD__.report()")
            assert len(report["parents"])==162
            files = []
            for view in VIEWS:
                page.evaluate("v=>{window.__MOTO_LOD__.view(v);window.__MOTO_LOD__.silhouette(false);window.__MOTO_LOD__.scene.render()}",view)
                files.append(capture(page,f"{model}-{view}.png"))
                page.evaluate("async()=>{window.__MOTO_LOD__.silhouette(true);await window.__MOTO_LOD__.scene.whenReadyAsync();window.__MOTO_LOD__.scene.render()}")
                files.append(capture(page,f"{model}-{view}-mask.png"))
                page.evaluate("window.__MOTO_LOD__.silhouette(false)")
                print("CAPTURED",model,view,flush=True)
            assert not errors and not failures,(errors,failures)
            report.update(files=files,page_errors=errors,http_failures=failures)
            results[model]=report
            (OUT/f"{model}-engine-report.json").write_text(json.dumps(report,indent=2)+"\n")
            page.close()
        browser.close()
    source = {p["name"]:p["matrix"] for p in results["source"]["parents"]}
    lod = {p["name"]:p["matrix"] for p in results["lod"]["parents"]}
    assert source.keys()==lod.keys()
    matrices = [{"name":name,"max_delta":max(abs(a-b) for a,b in zip(matrix,lod[name]))} for name,matrix in source.items()]
    assert max(row["max_delta"] for row in matrices)<2e-6
    comparisons = []
    for view in VIEWS:
        a=np.asarray(Image.open(OUT/f"source-{view}-mask.png").convert("RGB"))[:,:,0]>128
        b=np.asarray(Image.open(OUT/f"lod-{view}-mask.png").convert("RGB"))[:,:,0]>128
        union=int(np.count_nonzero(a|b));intersection=int(np.count_nonzero(a&b))
        assert np.count_nonzero(a)>1000 and np.count_nonzero(b)>1000
        comparisons.append({"view":view,"source_pixels":int(a.sum()),"lod_pixels":int(b.sum()),"intersection_over_union":intersection/union,"different_pixels":int(np.count_nonzero(a^b)),"scope":"Same-camera opaque silhouettes, diagnostic only; not a score of realism, internal surface detail or optical quality."})
    build = ROOT/"assets-src/moto-components/motorcycle-lod-review-v1/build-report.json"
    report={"schema":1,"date":"2026-10-22","models":results,"parent_matrix_checks":matrices,"silhouette_comparisons":comparisons,
            "build_report_sha256":hashlib.sha256(build.read_bytes()).hexdigest(),
            "viewer_sha256":hashlib.sha256((ROOT/"tools/motorcycle-lod-review-v1/viewer.js").read_bytes()).hexdigest(),
            "capture_tool_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "art_accepted":False,"physical_iphone_tested":False,
            "scope":"Actual Babylon imports and rendered canvases in desktop Chromium software WebGL. No physical-device performance, source/LOD surface identity or OEM fit claim."}
    (OUT/"engine-comparison.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"source_triangles":results["source"]["triangles"],"lod_triangles":results["lod"]["triangles"],"views":len(VIEWS),"min_silhouette_iou":min(x["intersection_over_union"] for x in comparisons)}))


if __name__ == "__main__":
    main()
