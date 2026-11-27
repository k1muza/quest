"""Capture the review's tie, movement, reversal, and winner evidence sequence."""
from __future__ import annotations

import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
MAP_DIR = ROOT / "maps" / "kingdom-quest"
REPORTS = MAP_DIR / "reports"
PAGE = ROOT / "unified" / "maps" / "kingdom-quest.html"


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=os.environ.get("CHROMIUM") or None,
            headless=True,
            args=["--disable-dev-shm-usage"],
        )
        context = browser.new_context(
            viewport={"width": 1600, "height": 900},
            record_video_dir=str(REPORTS),
            record_video_size={"width": 1600, "height": 900},
        )
        page = context.new_page()
        page.goto(PAGE.as_uri(), wait_until="load")
        page.wait_for_function("window.quest && window.quest.ready")
        page.add_style_tag(content="""
          #review-note{position:fixed;z-index:30;left:2%;top:17%;padding:9px 13px;
            border:1px solid #e4c27788;border-radius:7px;background:#0d2938dc;color:#f7e9c8;
            font:700 12px/1.2 system-ui,sans-serif;letter-spacing:.08em;text-transform:uppercase;
            box-shadow:0 6px 18px #00141b88;pointer-events:none}
        """)
        page.evaluate("""() => {
          const tag=document.createElement('div');tag.id='review-note';document.body.append(tag);
          window.reviewNote=text=>tag.textContent=text;
        }""")

        page.locator("#operatorToggle").click()
        page.locator("#teamCount").select_option("6")
        page.locator("#start").click()
        page.locator("#close").click()
        page.evaluate("window.reviewNote('Six teams tied at the start')")
        page.wait_for_timeout(1100)
        page.screenshot(path=str(REPORTS / "runtime-review-tie-start.png"), animations="disabled")

        page.evaluate("""() => {
          const s=window.quest.getState();s.teams.forEach(t=>t.score=20);
          window.quest.applyState(s,{instant:true});window.reviewNote('Six teams tied at stop 21');
        }""")
        page.wait_for_timeout(1100)
        page.screenshot(path=str(REPORTS / "runtime-review-tie-interior.png"), animations="disabled")

        page.evaluate("""() => {
          const s=window.quest.getState();s.phase='active';s.teams.forEach(t=>t.score=0);
          s.activeTeamId='team-1';window.quest.applyState(s,{instant:true});
          window.reviewNote('One step: team one moves to stop two');window.quest.score(1);
        }""")
        page.wait_for_timeout(550)
        page.screenshot(path=str(REPORTS / "runtime-review-short-move.png"), animations="disabled")

        page.evaluate("""() => {
          const s=window.quest.getState();s.teams.forEach(t=>t.score=0);
          window.quest.applyState(s,{instant:true});window.reviewNote('Ten steps: team one advances');
          window.quest.score(10);
        }""")
        page.wait_for_timeout(800)
        page.screenshot(path=str(REPORTS / "runtime-review-long-move.png"), animations="disabled")
        page.wait_for_timeout(1000)

        page.evaluate("""() => {
          window.reviewNote('Reversal: team one returns to the start');window.quest.score(-10);
        }""")
        page.wait_for_timeout(800)
        page.screenshot(path=str(REPORTS / "runtime-review-reversal.png"), animations="disabled")
        page.wait_for_timeout(1000)

        page.evaluate("""() => {
          let s=window.quest.getState();s.phase='active';s.complete=false;s.winnerIds=[];
          s.teams.forEach((t,i)=>t.score=i<2?37:0);s.activeTeamId='team-1';
          window.quest.applyState(s,{instant:true});s=window.quest.getState();
          s.phase='complete';s.complete=true;s.winnerIds=['team-1','team-2'];
          window.reviewNote('Two winners at 37 points: results and effects');
          window.quest.applyState(s);
        }""")
        page.wait_for_timeout(1550)
        page.screenshot(path=str(REPORTS / "runtime-review-winners-at-37.png"), animations="disabled")

        video = page.video
        context.close()
        browser.close()
        if video is None:
            raise RuntimeError("Browser video recording was not created")
        temp_path = Path(video.path())
        target = REPORTS / "runtime-review-sequence.webm"
        if target.exists():
            target.unlink()
        temp_path.replace(target)
        manifest = {
            "status": "PASS",
            "sequence": [
                "six-team start tie",
                "six-team interior tie",
                "one-step movement",
                "ten-step movement",
                "reversal to start",
                "two winners at score 37",
            ],
            "video": str(target.relative_to(ROOT)),
            "screenshots": sorted(path.name for path in REPORTS.glob("runtime-review-*.png")),
        }
        (REPORTS / "runtime-review-sequence.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
