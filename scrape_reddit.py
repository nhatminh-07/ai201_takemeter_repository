"""
Scrape r/weather posts using Playwright via old.reddit.com HTML.
Paginates through multiple sort feeds until TARGET posts are collected.
"""

import asyncio
import csv
from playwright.async_api import async_playwright

SUBREDDIT = "weather"
TARGET = 300
OUTPUT = "data.csv"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


async def scrape_sort(page, sort, seen_ids, rows, target):
    url = f"https://old.reddit.com/r/{SUBREDDIT}/{sort}/?limit=100"
    page_num = 0

    while len(rows) < target:
        page_num += 1
        print(f"  [{sort}] page {page_num} — fetching {url[:90]}")

        resp = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        if resp.status != 200:
            print(f"  [{sort}] HTTP {resp.status} — stopping.")
            break
        await asyncio.sleep(2)

        # Each post is a div.thing; extract title + optional selftext snippet
        things = await page.query_selector_all("div.thing[data-fullname]")
        if not things:
            print(f"  [{sort}] No posts found on page {page_num}.")
            break

        added = 0
        for thing in things:
            fullname = await thing.get_attribute("data-fullname")
            if not fullname or fullname in seen_ids:
                continue

            is_stickied = await thing.get_attribute("data-promoted")
            nsfw = await thing.get_attribute("data-nsfw")
            if nsfw == "true":
                continue

            # Post title
            title_el = await thing.query_selector("a.title")
            if not title_el:
                continue
            title = (await title_el.inner_text()).strip()

            # Self-text preview (optional — may not be visible without expansion)
            selftext = ""
            md_el = await thing.query_selector(".md")
            if md_el:
                selftext = (await md_el.inner_text()).strip()
                selftext = " ".join(selftext.split())[:400]

            text = f"{title} | {selftext}" if selftext else title

            seen_ids.add(fullname)
            rows.append({"text": text, "label": "", "notes": ""})
            added += 1

            if len(rows) >= target:
                break

        print(f"  [{sort}] added {added}, total {len(rows)}")

        # Find "next" page link
        next_link = await page.query_selector("a[rel~='next']")
        if not next_link or len(rows) >= target:
            print(f"  [{sort}] No next page or target reached.")
            break
        url = await next_link.get_attribute("href")
        if not url.startswith("http"):
            url = "https://old.reddit.com" + url
        await asyncio.sleep(1.5)


async def main():
    rows = []
    seen_ids = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=UA,
            viewport={"width": 1280, "height": 900},
        )
        page = await context.new_page()

        for sort in ("new", "hot", "top"):
            if len(rows) >= TARGET:
                break
            print(f"\n=== Collecting [{sort}] ===")
            await scrape_sort(page, sort, seen_ids, rows, TARGET)

        await browser.close()

    print(f"\nTotal posts collected: {len(rows)}")
    rows = rows[:TARGET]

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "label", "notes"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} rows to {OUTPUT}")


if __name__ == "__main__":
    asyncio.run(main())
