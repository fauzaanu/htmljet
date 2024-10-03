import asyncio
import os
import shutil
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from playwright.async_api import async_playwright, TimeoutError
from PIL import Image
import imagehash
from bs4 import BeautifulSoup

app = typer.Typer(help="🚀 HTMLJET: Capture HTML elements as screenshots")
console = Console()

# Global variable to store the Progress object
progress = None

async def analyze_html_structure(page):
    html_content = await page.content()
    soup = BeautifulSoup(html_content, 'html.parser')
    body = soup.body

    def print_element_hierarchy(elements, level=1):
        element_dict = {}
        for i, element in enumerate(elements, 1):
            if element.name:
                element_dict[i] = element
                child_count = len([child for child in element.children if child.name])
                console.print(f"[bold]{level}.{i}[/bold] {element.name}: {child_count} child elements")

        return element_dict

    level = 1
    current_elements = body.children
    element_dict = {}

    while True:
        console.print(f"\n[cyan]Level {level}:[/cyan]")
        level_dict = print_element_hierarchy(current_elements, level)
        element_dict[level] = level_dict

        if not level_dict:
            console.print("[yellow]No more elements at this level.[/yellow]")
            break

        while True:
            user_input = console.input("\n[bold cyan]Enter the level number to capture, or 'n' to go deeper: [/bold cyan]")
            if user_input.lower() == 'n':
                level += 1
                current_elements = [child for element in level_dict.values() for child in element.children if child.name]
                break
            try:
                selected_level = int(user_input)
                if selected_level in element_dict:
                    selected_elements = element_dict[selected_level].values()
                    selector = ', '.join([element.name for element in selected_elements])
                    console.print(f"[bold green]Using selector: {selector}[/bold green]")
                    return selector
                else:
                    console.print("[bold red]Invalid level. Please enter a valid level number.[/bold red]")
            except ValueError:
                console.print("[bold red]Invalid input. Please enter a valid level number or 'n'.[/bold red]")

    console.print("[bold yellow]No elements selected. Using 'body > *' as fallback.[/bold yellow]")
    return 'body > *'

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

        selector = await analyze_html_structure(page)

        elements = await page.query_selector_all(selector)
        console.print(f"[bold cyan]🔍 Found {len(elements)} elements at the selected level[/bold cyan]")

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

                    # Get the bounding box of the element
                    bounding_box = await element.bounding_box()
                    if bounding_box is None:
                        console.print(f"[yellow]⚠️  Element {i} has no bounding box, skipping...[/yellow]")
                        failed_screenshots += 1
                        progress.advance(task)
                        continue

                    # Take a screenshot of the specific element
                    await page.screenshot(
                        path=f"{output_dir}/element_{i}.png",
                        clip=bounding_box,
                        timeout=5000
                    )
                    successful_screenshots += 1
                except TimeoutError:
                    console.print(f"[red]⏱️  Timeout error occurred for element {i}[/red]")
                    failed_screenshots += 1
                except Exception as e:
                    console.print(f"[red]❌ Error capturing screenshot for element {i}: {str(e)}[/red]")
                    failed_screenshots += 1

                progress.advance(task)

        await browser.close()

        console.print("[bold green]✅ Screenshot capture complete![/bold green]")
        console.print(f"[green]📊 Successful: {successful_screenshots}, Failed: {failed_screenshots}[/green]")

def cleanup_similar_images(directory: str, similarity_threshold: float = 0.5):
    """
    Copy unique images to a new 'clean' directory, keeping the larger ones when similar.

    :param directory: Directory containing the images
    :param similarity_threshold: Threshold for considering images as similar (0.0 to 1.0)
    :return: Path to the new 'clean' directory
    """
    global progress
    clean_dir = os.path.join(directory, "clean")
    os.makedirs(clean_dir, exist_ok=True)

    image_files = [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    image_hashes = {}

    if progress is None:
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        )

    with progress:
        task = progress.add_task("[cyan]Cleaning up similar images...", total=len(image_files))

        for filename in image_files:
            file_path = os.path.join(directory, filename)
            try:
                with Image.open(file_path) as img:
                    hash = imagehash.average_hash(img)
                    img_size = os.path.getsize(file_path)

                    for existing_hash, (existing_file, existing_size) in image_hashes.items():
                        if (hash - existing_hash) / len(hash.hash) ** 2 <= 1 - similarity_threshold:
                            if img_size > existing_size:
                                image_hashes[hash] = (file_path, img_size)
                            break
                    else:
                        image_hashes[hash] = (file_path, img_size)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not process '{filename}': {str(e)}[/yellow]")

            progress.advance(task)

        # Copy unique images to clean directory
        for file_path, _ in image_hashes.values():
            shutil.copy2(file_path, clean_dir)

    unique_count = len(image_hashes)
    removed_count = len(image_files) - unique_count
    console.print(f"[bold green]🧹 Cleanup complete! Copied {unique_count} unique images to '{clean_dir}'.[/bold green]")
    console.print(f"[bold green]🗑️ {removed_count} similar images were not copied.[/bold green]")

    return clean_dir

@app.command()
def snap(
    url: str = typer.Argument(..., help="The URL of the web page to screenshot"),
    output_dir: str = typer.Option("htmljet", help="Directory to save screenshots", show_default=True)
):
    """
    📸 Capture screenshots of HTML elements on a webpage.
    """
    console.print("[bold magenta]🎭 Welcome to HTMLJET![/bold magenta]")
    console.print(f"[italic]Preparing to capture elements from {url}[/italic]")

    asyncio.run(take_screenshots(url, output_dir))

    console.print("[bold green]🎉 Screenshots captured! Now cleaning up similar images...[/bold green]")
    clean_dir = cleanup_similar_images(output_dir)

    console.print(f"[bold green]🎉 All done! Your cleaned-up screenshots are saved in the '{clean_dir}' directory.[/bold green]")

@app.command()
def cleanup(
    directory: str = typer.Argument(".", help="The directory containing images to clean up (default: current directory)"),
    similarity_threshold: float = typer.Option(0.9, help="Threshold for considering images as similar (0.0 to 1.0)", min=0.0, max=1.0)
):
    """
    🧹 Clean up similar images in a directory, keeping the larger ones.
    """
    console.print("[bold magenta]🎭 Welcome to HTMLJET Cleanup![/bold magenta]")

    # Convert to absolute path
    abs_directory = os.path.abspath(directory)
    console.print(f"[italic]Preparing to clean up similar images in {abs_directory}[/italic]")

    if not os.path.exists(abs_directory):
        console.print(f"[bold red]Error: The directory '{abs_directory}' does not exist.[/bold red]")
        return

    cleanup_similar_images(abs_directory, similarity_threshold)

    console.print(f"[bold green]🎉 All done! Your cleaned-up images are in the '{abs_directory}' directory.[/bold green]")
    console.print("[bold]Happy coding! 🗂️✨[/bold]")

if __name__ == "__main__":
    app()


