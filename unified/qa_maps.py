"""Smoke-test the offline map gallery and every generated standalone board."""
from __future__ import annotations

import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
MAP_ROOT = ROOT / "maps"
GALLERY = ROOT / "unified" / "maps.html"


def main() -> int:
    map_dirs = sorted(path.parent for path in MAP_ROOT.glob("*/map.json"))
    if not map_dirs:
        raise SystemExit("No map manifests found")

    failures: list[str] = []
    results: list[dict] = []
    external_requests: list[str] = []
    browser_errors: list[str] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=os.environ.get("CHROMIUM") or None,
            headless=True,
            args=["--disable-dev-shm-usage"],
        )

        gallery_page = browser.new_page()
        gallery_page.on(
            "request",
            lambda request: external_requests.append(request.url)
            if request.url.startswith(("http:", "https:"))
            else None,
        )
        gallery_page.goto(GALLERY.as_uri(), wait_until="load")
        gallery_ids = gallery_page.locator("a.card").evaluate_all(
            "cards => cards.map(card => card.getAttribute('href').replace('maps/', '').replace('.html', ''))"
        )
        expected_ids = [path.name for path in map_dirs]
        if sorted(gallery_ids) != expected_ids:
            failures.append(f"Gallery links {gallery_ids} do not match manifests {expected_ids}")
        gallery_page.close()

        for map_dir in map_dirs:
            metadata = json.loads((map_dir / "map.json").read_text(encoding="utf-8"))
            page = browser.new_page(viewport={"width": 1600, "height": 900})
            page.on("pageerror", lambda error: browser_errors.append(str(error)))
            page.on(
                "console",
                lambda message: browser_errors.append(message.text)
                if message.type == "error"
                else None,
            )
            page.on(
                "request",
                lambda request: external_requests.append(request.url)
                if request.url.startswith(("http:", "https:"))
                else None,
            )

            try:
                standalone = ROOT / "unified" / "maps" / f"{metadata['id']}.html"
                page.goto(standalone.as_uri(), wait_until="load", timeout=30000)
                page.wait_for_function("window.quest && window.quest.ready", timeout=30000)

                image = page.locator("#background").evaluate(
                    "el => ({complete: el.complete, width: el.naturalWidth, height: el.naturalHeight})"
                )
                if image != {"complete": True, "width": 1920, "height": 1080}:
                    failures.append(f"{metadata['id']}: background did not load at 1920x1080: {image}")

                state = page.evaluate("window.quest.getState()")
                if state["stopCount"] != metadata["defaultStopCount"]:
                    failures.append(f"{metadata['id']}: default position count differs from manifest")
                if state["scoreAtFinish"] != metadata["defaultMovementSteps"]:
                    failures.append(f"{metadata['id']}: default movement count differs from manifest")

                options = page.locator("#stopCount option").evaluate_all(
                    "options => options.map(option => Number(option.value))"
                )
                expected_positions = [steps + 1 for steps in metadata["supportedMovementSteps"]]
                if options != expected_positions:
                    failures.append(f"{metadata['id']}: selector options {options}, expected {expected_positions}")

                capacities = []
                for steps in metadata["supportedMovementSteps"]:
                    validation = page.evaluate("positions => window.quest.validate(positions)", steps + 1)
                    capacities.append(
                        {
                            "movementSteps": steps,
                            "positions": validation["stops"],
                            "minimumSpacingPx": validation["minimumGap"],
                            "valid": validation["ok"],
                        }
                    )
                    if not validation["ok"] or validation["stops"] != steps + 1:
                        failures.append(f"{metadata['id']}: invalid {steps}-step route: {validation}")

                unsupported_rejected = page.evaluate(
                    """() => {
                      try { window.quest.validate(61); return false; }
                      catch (_) { return true; }
                    }"""
                )
                if 60 not in metadata["supportedMovementSteps"] and not unsupported_rejected:
                    failures.append(f"{metadata['id']}: unsupported 60-step route was accepted")

                page.locator("#operatorToggle").click()
                page.locator("#stopCount").select_option(str(expected_positions[0]))
                changed = page.evaluate(
                    "({positions: window.quest.getState().stopCount, finish: window.quest.getState().scoreAtFinish})"
                )
                if changed != {
                    "positions": expected_positions[0],
                    "finish": metadata["supportedMovementSteps"][0],
                }:
                    failures.append(f"{metadata['id']}: step selector failed to set positions/finish score: {changed}")

                page.locator("#teamCount").select_option("6")
                page.locator("#start").click()
                started = page.evaluate(
                    "({phase: window.quest.getState().phase, teams: window.quest.positions().length})"
                )
                if started != {"phase": "handover", "teams": 6}:
                    failures.append(f"{metadata['id']}: six-team start failed: {started}")

                results.append(
                    {
                        "map": metadata["id"],
                        "title": page.title(),
                        "background": image,
                        "defaultMovementSteps": state["scoreAtFinish"],
                        "defaultPositions": state["stopCount"],
                        "capacities": capacities,
                        "sixTeamStart": started,
                    }
                )
            except Exception as error:  # Record one map's failure and continue through the set.
                failures.append(f"{metadata['id']}: {type(error).__name__}: {error}")
            finally:
                page.close()

        browser.close()

    if browser_errors:
        failures.append(f"Browser errors: {browser_errors}")
    if external_requests:
        failures.append(f"Unexpected external requests: {external_requests}")

    report = {
        "status": "PASS" if not failures else "FAIL",
        "maps": results,
        "browserErrors": browser_errors,
        "externalRequests": external_requests,
        "failures": failures,
    }
    (MAP_ROOT / "runtime-qa.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
