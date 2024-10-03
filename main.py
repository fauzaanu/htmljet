"""
elementor_snaps is a python script designed to take screenshots of Elementor pages.

The default class we will be taking screenshots from is the elementor-element class as that is usually the class that
contains one singular component.

Why?
---
This script was created to automate the process of taking screenshots of Elementor pages. This is useful for recreating
the UI of elementor websites using LLMs for other purposes.

The project only has one dependency, which is the playwright library.
"""

import asyncio
from playwright.async_api import async_playwright
import os
import argparse

async def take_screenshots(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)

        # Wait for the page to load completely
        await page.wait_for_load_state("networkidle")

        # Find all elements with class "elementor-element"
        elements = await page.query_selector_all(".elementor-element")

        # Create a directory for screenshots if it doesn't exist
        os.makedirs("elementor_screenshots", exist_ok=True)

        for i, element in enumerate(elements):
            # Take a screenshot of each element
            await element.screenshot(path=f"elementor_screenshots/element_{i}.png")

        await browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Take screenshots of Elementor elements on a webpage.")
    parser.add_argument("url", help="The URL of the webpage to screenshot")
    args = parser.parse_args()

    asyncio.run(take_screenshots(args.url))


