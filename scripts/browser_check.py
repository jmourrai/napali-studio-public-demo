"""Visual-only UI test using synthetic mocked API responses (browser cannot reach localhost here).

This does NOT substitute for the separately executed API tests.
"""
import asyncio
import json
import os
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
DATA = [
    {"id": "a10000-000000", "title": "Draft example release note", "description": "Demonstrate a generic review workflow", "priority": "high", "status": "review", "version": 2},
    {"id": "b10000-000000", "title": "Validate sample dashboard", "description": "Synthetic metrics and display checks", "priority": "medium", "status": "in_progress", "version": 3},
    {"id": "c10000-000000", "title": "Approve placeholder summary", "description": "Contains no real business or client information", "priority": "high", "status": "approval", "version": 4},
    {"id": "d10000-000000", "title": "Publish demonstration guide", "description": "Safe documentation using fabricated content", "priority": "low", "status": "published", "version": 5},
    {"id": "e10000-000000", "title": "Triage new sample request", "description": "Illustrative backlog item only", "priority": "medium", "status": "intake", "version": 1},
]


async def main():
    async with async_playwright() as play:
        browser = await play.chromium.launch(
            executable_path=os.environ.get("CHROMIUM_BIN") or None,
            headless=True, args=["--no-sandbox"]
        )
        page = await browser.new_page(viewport={"width": 1490, "height": 970}, device_scale_factor=1)
        raw = (ROOT / "web" / "index.html").read_text()
        raw = raw.replace('<link rel="stylesheet" href="/static/styles.css" />', "")
        raw = raw.replace('<script src="/static/app.js" defer></script>', "")
        await page.set_content(raw)
        await page.add_style_tag(content=(ROOT / "web" / "styles.css").read_text())
        # Browser fetch is mocked; API behavior was separately verified with pytest.
        await page.evaluate(
            """(records) => {
              window.__items = records;
              window.fetch = async (path, options={}) => {
                let body;
                if (path === '/api/work-items') {
                  if (options.method === 'POST') {
                    const data = JSON.parse(options.body);
                    window.__items.push({id:'new-demo-id',status:'intake',version:1,...data});
                    body = window.__items.at(-1);
                  } else body = window.__items;
                } else if (path === '/api/metrics') {
                  const by_status = Object.fromEntries(['intake','review','in_progress','approval','published'].map(s=>[s,window.__items.filter(x=>x.status===s).length]));
                  body = {total:window.__items.length,by_status};
                } else if (path === '/api/workflow') {
                  body = {allowed_transitions:{intake:['review'],review:['intake','in_progress'],in_progress:['review','approval'],approval:['in_progress','published'],published:[]}};
                } else if (path.endsWith('/events')) {
                  body = [{id:1,from_status:null,to_status:'intake',note:'Created in demo',actor:'demo-user',created_at:'2026-10-28T12:00:00+00:00'}];
                } else if (path.endsWith('/transition')) {
                  const id=path.split('/')[3]; const item=window.__items.find(x=>x.id===id);
                  item.status=JSON.parse(options.body).to_status;item.version++;body=item;
                }
                return {ok:true,json:async()=>body};
              };
            }""", DATA,
        )
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        await page.add_script_tag(content=(ROOT / "web" / "app.js").read_text())
        await page.locator("article.work-card").first.wait_for()
        assert await page.locator("article.work-card").count() == 5
        await page.screenshot(path=str(ROOT / "docs" / "demo-board.png"), full_page=True)
        await page.get_by_role("button", name="New work item").click()
        await page.get_by_label("Title").fill("Explore synthetic release flow")
        await page.get_by_label("Description").fill("Made during browser validation")
        await page.get_by_role("button", name="Create item").click()
        await page.get_by_text("Explore synthetic release flow").wait_for()
        assert await page.locator("article.work-card").count() == 6
        assert not errors, f"JavaScript errors: {errors}"
        print(json.dumps({"visual_cards": 5, "after_create": 6, "js_errors": errors,
                          "screenshot": "docs/demo-board.png"}))
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
