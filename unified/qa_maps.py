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
                report_dir = map_dir / "reports"
                report_dir.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(report_dir / "runtime-board.png"), animations="disabled")

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

                page.locator("#close").click()
                tied_start = page.evaluate(
                    """() => {
                      const ps=window.quest.positions(), worlds=ps.map(p=>p.location.world);
                      return {
                        teams:ps.length,
                        targetStops:[...new Set(ps.map(p=>p.targetStop))],
                        drawnStops:[...new Set(ps.map(p=>p.drawnStop))],
                        anchorSpread:Math.max(...worlds.map(p=>p.x))-Math.min(...worlds.map(p=>p.x))+
                          Math.max(...worlds.map(p=>p.y))-Math.min(...worlds.map(p=>p.y))+
                          Math.max(...worlds.map(p=>p.z))-Math.min(...worlds.map(p=>p.z)),
                        screenSpread:Math.max(...ps.map(p=>p.location.x))-Math.min(...ps.map(p=>p.location.x))
                      };
                    }"""
                )
                if tied_start["teams"] != 6 or tied_start["targetStops"] != [1] or tied_start["drawnStops"] != [1] or tied_start["anchorSpread"] > 1e-6:
                    failures.append(f"{metadata['id']}: start tie did not share one route anchor: {tied_start}")
                page.screenshot(path=str(report_dir / "runtime-six-team.png"), animations="disabled")
                page.evaluate(
                    """() => {
                      const s=window.quest.getState(), interior=Math.round(s.scoreAtFinish/2);
                      s.teams.forEach(t=>t.score=interior);
                      window.quest.applyState(s,{instant:true});
                    }"""
                )
                tied_interior = page.evaluate(
                    """() => {
                      const ps=window.quest.positions(), worlds=ps.map(p=>p.location.world);
                      return {
                        teams:ps.length,
                        targetStops:[...new Set(ps.map(p=>p.targetStop))],
                        drawnStops:[...new Set(ps.map(p=>p.drawnStop))],
                        anchorSpread:Math.max(...worlds.map(p=>p.x))-Math.min(...worlds.map(p=>p.x))+
                          Math.max(...worlds.map(p=>p.y))-Math.min(...worlds.map(p=>p.y))+
                          Math.max(...worlds.map(p=>p.z))-Math.min(...worlds.map(p=>p.z)),
                        screenSpread:Math.max(...ps.map(p=>p.location.x))-Math.min(...ps.map(p=>p.location.x))
                      };
                    }"""
                )
                if tied_interior["teams"] != 6 or len(tied_interior["targetStops"]) != 1 or tied_interior["targetStops"] != tied_interior["drawnStops"] or tied_interior["anchorSpread"] > 1e-6 or tied_interior["screenSpread"] < 100:
                    failures.append(f"{metadata['id']}: interior tie did not share one anchor with readable indicators: {tied_interior}")
                page.screenshot(path=str(report_dir / "runtime-six-way-tie-interior.png"), animations="disabled")

                move_durations = page.evaluate(
                    """() => {
                      window.quest.reset(6); window.quest.score(1);
                      const one=window.quest.positions()[0].duration;
                      window.quest.reset(6); window.quest.score(10);
                      const ten=window.quest.positions()[0].duration;
                      return {oneStepMs:one,tenStepMs:ten};
                    }"""
                )
                page.wait_for_timeout(250)
                page.evaluate("window.quest.score(-10)")
                page.wait_for_timeout(450)
                reversal = page.evaluate(
                    """() => {
                      const p=window.quest.positions()[0];
                      return {score:p.score,targetStop:p.targetStop,drawnStop:p.drawnStop,duration:p.duration};
                    }"""
                )
                if not (250 <= move_durations["oneStepMs"] <= 500 and move_durations["tenStepMs"] > move_durations["oneStepMs"] * 3):
                    failures.append(f"{metadata['id']}: movement duration did not scale by route steps: {move_durations}")
                if reversal["score"] != 0 or reversal["targetStop"] != 1 or reversal["drawnStop"] != 1:
                    failures.append(f"{metadata['id']}: score reversal failed to settle at its authoritative stop: {reversal}")

                winner_result = page.evaluate(
                    """() => {
                      window.quest.reset(6);
                      let s=window.quest.getState(); s.phase='active';s.teams[0].score=37;s.teams[1].score=37;
                      window.quest.applyState(s,{instant:true});
                      s=window.quest.getState();s.phase='complete';s.complete=true;
                      s.winnerIds=['team-1','team-2'];
                      window.quest.applyState(s);
                      const stops=window.quest.generateStops(s.stopCount),effects=window.quest.effects();
                      const stage=document.querySelector('#stage').getBoundingClientRect(),
                        scaleX=stage.width/window.QUEST_DATA.width,scaleY=stage.height/window.QUEST_DATA.height,
                        markers=[{label:'finish',...stops.at(-1)},{label:'score37',...stops[37]}],
                        panelRect=document.querySelector('#results').getBoundingClientRect(),
                        phaseRect=document.querySelector('.phase').getBoundingClientRect(),
                        covers=(r,p)=>p.x*scaleX>=r.left&&p.x*scaleX<=r.right&&p.y*scaleY>=r.top&&p.y*scaleY<=r.bottom;
                      return {
                        panelVisible:!document.querySelector('#results').hidden,
                        panelCenterX:document.querySelector('#results').getBoundingClientRect().left+
                          document.querySelector('#results').getBoundingClientRect().width/2,
                        panelSide:document.querySelector('#results').dataset.side,
                        phaseCenterX:document.querySelector('.phase').getBoundingClientRect().left+
                          document.querySelector('.phase').getBoundingClientRect().width/2,
                        finishOverlayOverlap:markers.some(p=>covers(panelRect,p)||covers(phaseRect,p)),
                        winners:s.winnerIds,
                        effects:effects.map(e=>({id:e.id,distance:e.d,expected:stops[37].distance})),
                        resultsText:document.querySelector('#resultName').textContent
                      };
                    }"""
                )
                expected_panel_side = "left" if metadata["id"] == "winding-river" else "right"
                wrong_panel_side = winner_result["panelCenterX"] > 800 if expected_panel_side == "left" else winner_result["panelCenterX"] < 800
                if not winner_result["panelVisible"] or winner_result["panelSide"] != expected_panel_side or wrong_panel_side or winner_result["finishOverlayOverlap"] or len(winner_result["effects"]) != 2 or any(abs(e["distance"]-e["expected"]) > 1e-6 for e in winner_result["effects"]):
                    failures.append(f"{metadata['id']}: winner effects/results panel missed actual scoring stops: {winner_result}")
                page.wait_for_timeout(1350)
                page.screenshot(path=str(report_dir / "runtime-winner-near-finish.png"), animations="disabled")

                results.append(
                    {
                        "map": metadata["id"],
                        "title": page.title(),
                        "background": image,
                        "defaultMovementSteps": state["scoreAtFinish"],
                        "defaultPositions": state["stopCount"],
                        "capacities": capacities,
                        "sixTeamStart": started,
                        "sixTeamTieStart": tied_start,
                        "sixTeamTieInterior": tied_interior,
                        "movementDurations": move_durations,
                        "reversal": reversal,
                        "nearFinishMultipleWinner": winner_result,
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
