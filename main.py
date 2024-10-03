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
from playwright.async_api import async_playwright, TimeoutError
import os
import argparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def take_screenshots(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir="browser",
            headless=False,
        )
        page = await browser.new_page()
        await page.goto(url)

        # Wait for the page to load completely
        await page.wait_for_load_state("networkidle")

        # Find all elements with attribute data-element_type="container"
        elements = await page.query_selector_all('[data-element_type="container"]')

        logging.info(f"Found {len(elements)} elements")

        # Create a directory for screenshots if it doesn't exist
        os.makedirs("elementor_screenshots", exist_ok=True)

        successful_screenshots = 0
        failed_screenshots = 0

        for i, element in enumerate(elements):
            try:
                # Check if the element is visible
                is_visible = await element.is_visible()
                if not is_visible:
                    logging.warning(f"Element {i} is not visible, skipping...")
                    failed_screenshots += 1
                    continue

                # Take a screenshot of each element
                await element.screenshot(path=f"elementor_screenshots/element_{i}.png", timeout=5000)
                logging.info(f"Successfully captured screenshot for element {i}")
                successful_screenshots += 1
            except TimeoutError:
                logging.error(f"Timeout error occurred while capturing screenshot for element {i}")
                failed_screenshots += 1
            except Exception as e:
                logging.error(f"Error occurred while capturing screenshot for element {i}: {str(e)}")
                failed_screenshots += 1

        await browser.close()

        logging.info(f"Screenshot capture complete. Successful: {successful_screenshots}, Failed: {failed_screenshots}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Take screenshots of Elementor elements on a webpage.")
    parser.add_argument("url", help="The URL of the webpage to screenshot")
    args = parser.parse_args()

    asyncio.run(take_screenshots(args.url))


