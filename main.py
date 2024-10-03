"""
🎨 Elementor Snaps: Capture the beauty of Elementor pages! 📸

This magical script automates the process of taking screenshots of Elementor pages.
It's perfect for recreating UI designs or analyzing layouts using LLMs.

By default, we're targeting elements with the attribute [data-element_type="container"].

May your screenshots be ever crisp and your designs ever inspiring! ✨
"""

import asyncio
import os
from typing import Optional
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from playwright.async_api import async_playwright, TimeoutError

app = typer.Typer(help="🚀 Elementor Snaps: Capture Elementor magic with ease!")
console = Console()

async def take_screenshots(url: str, output_dir: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir="browser",
            headless=False,
        )
        page = await browser.new_page()
        
        with console.status(f"[bold green]🌐 Loading page: {url}[/bold green]"):
            await page.goto(url)
            await page.wait_for_load_state("networkidle")

        elements = await page.query_selector_all('[data-element_type="container"]')
        console.print(f"[bold cyan]🔍 Found {len(elements)} elements[/bold cyan]")

        os.makedirs(output_dir, exist_ok=True)

        successful_screenshots = 0
        failed_screenshots = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Taking screenshots...", total=len(elements))

            for i, element in enumerate(elements):
                try:
                    if not await element.is_visible():
                        console.print(f"[yellow]⚠️  Element {i} is not visible, skipping...[/yellow]")
                        failed_screenshots += 1
                        progress.advance(task)
                        continue

                    await element.screenshot(path=f"{output_dir}/element_{i}.png", timeout=5000)
                    successful_screenshots += 1
                except TimeoutError:
                    console.print(f"[red]⏱️  Timeout error occurred for element {i}[/red]")
                    failed_screenshots += 1
                except Exception as e:
                    console.print(f"[red]❌ Error capturing screenshot for element {i}: {str(e)}[/red]")
                    failed_screenshots += 1
                
                progress.advance(task)

        await browser.close()

        console.print(f"[bold green]✅ Screenshot capture complete![/bold green]")
        console.print(f"[green]📊 Successful: {successful_screenshots}, Failed: {failed_screenshots}[/green]")

@app.command()
def snap(
    url: str = typer.Argument(..., help="The URL of the Elementor page to screenshot"),
    output_dir: str = typer.Option("elementor_screenshots", help="Directory to save screenshots", show_default=True)
):
    """
    📸 Capture screenshots of Elementor containers on a webpage.
    """
    console.print(f"[bold magenta]🎭 Welcome to Elementor Snaps![/bold magenta]")
    console.print(f"[italic]Preparing to capture the essence of {url}[/italic]")
    
    asyncio.run(take_screenshots(url, output_dir))
    
    console.print(f"[bold green]🎉 All done! Your screenshots are saved in the '{output_dir}' directory.[/bold green]")
    console.print("[bold]Happy designing! 🎨✨[/bold]")

if __name__ == "__main__":
    app()


