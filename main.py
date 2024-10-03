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
from PIL import Image
import imagehash

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

def cleanup_similar_images(directory: str, similarity_threshold: float = 0.9):
    """
    Remove similar images from the given directory, keeping the larger ones.
    
    :param directory: Directory containing the images
    :param similarity_threshold: Threshold for considering images as similar (0.0 to 1.0)
    """
    image_files = [f for f in os.listdir(directory) if f.endswith('.png')]
    image_hashes = {}

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Cleaning up similar images...", total=len(image_files))

        for filename in image_files:
            file_path = os.path.join(directory, filename)
            with Image.open(file_path) as img:
                hash = imagehash.average_hash(img)
                img_size = os.path.getsize(file_path)
                
                for existing_hash, (existing_file, existing_size) in image_hashes.items():
                    if (hash - existing_hash) / len(hash.hash) ** 2 <= 1 - similarity_threshold:
                        if img_size > existing_size:
                            os.remove(existing_file)
                            image_hashes[hash] = (file_path, img_size)
                        else:
                            os.remove(file_path)
                        break
                else:
                    image_hashes[hash] = (file_path, img_size)
            
            progress.advance(task)

    removed_count = len(image_files) - len(image_hashes)
    console.print(f"[bold green]🧹 Cleanup complete! Removed {removed_count} similar images.[/bold green]")

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
    
    console.print(f"[bold green]🎉 Screenshots captured! Now cleaning up similar images...[/bold green]")
    cleanup_similar_images(output_dir)
    
    console.print(f"[bold green]🎉 All done! Your cleaned-up screenshots are saved in the '{output_dir}' directory.[/bold green]")
    console.print("[bold]Happy designing! 🎨✨[/bold]")

@app.command()
def cleanup(
    directory: str = typer.Argument(..., help="The directory containing images to clean up"),
    similarity_threshold: float = typer.Option(0.9, help="Threshold for considering images as similar (0.0 to 1.0)", min=0.0, max=1.0)
):
    """
    🧹 Clean up similar images in a directory, keeping the larger ones.
    """
    console.print(f"[bold magenta]🎭 Welcome to Elementor Snaps Cleanup![/bold magenta]")
    console.print(f"[italic]Preparing to clean up similar images in {directory}[/italic]")
    
    cleanup_similar_images(directory, similarity_threshold)
    
    console.print(f"[bold green]🎉 All done! Your cleaned-up images are in the '{directory}' directory.[/bold green]")
    console.print("[bold]Happy organizing! 🗂️✨[/bold]")

if __name__ == "__main__":
    app()


