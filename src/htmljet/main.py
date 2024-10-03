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

async def take_screenshots_all_levels(url: str, output_dir: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir="browser",
            headless=True,
        )
        page = await browser.new_page()

        with console.status(f"[bold green]🌐 Loading page: {url}[/bold green]"):
            await page.goto(url)
            await page.wait_for_load_state("networkidle")

        html_content = await page.content()
        soup = BeautifulSoup(html_content, 'html.parser')
        body = soup.body

        def count_elements_by_level(element, current_level=1):
            level_counts = {current_level: 0}
            for child in element.children:
                if child.name:
                    level_counts[current_level] += 1
                    child_counts = count_elements_by_level(child, current_level + 1)
                    for level, count in child_counts.items():
                        level_counts[level] = level_counts.get(level, 0) + count
            return level_counts

        element_counts = count_elements_by_level(body)

        for level in sorted(element_counts.keys()):
            level_dir = os.path.join(output_dir, f"level_{level}")
            os.makedirs(level_dir, exist_ok=True)

            selector = f"body {'> *' * (level - 1)}"
            elements = await page.query_selector_all(selector)

            console.print(f"[bold cyan]🔍 Found {len(elements)} elements at level {level}[/bold cyan]")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:
                task = progress.add_task(f"[cyan]Taking screenshots for level {level}...", total=len(elements))

                for i, element in enumerate(elements):
                    try:
                        if not await element.is_visible():
                            console.print(f"[yellow]⚠️  Element {i} at level {level} is not visible, skipping...[/yellow]")
                            progress.advance(task)
                            continue

                        await element.screenshot(path=f"{level_dir}/element_{i}.png")
                    except TimeoutError:
                        console.print(f"[red]⏱️  Timeout error occurred for element {i} at level {level}[/red]")
                    except Exception as e:
                        console.print(f"[red]❌ Error capturing screenshot for element {i} at level {level}: {str(e)}[/red]")

                    progress.advance(task)

        await browser.close()

        console.print("[bold green]✅ Screenshot capture for all levels complete![/bold green]")

async def analyze_html_structure(page):
    html_content = await page.content()
    soup = BeautifulSoup(html_content, 'html.parser')
    body = soup.body

    def count_elements_by_level(element, current_level=1):
        level_counts = {current_level: 0}
        for child in element.children:
            if child.name:
                level_counts[current_level] += 1
                child_counts = count_elements_by_level(child, current_level + 1)
                for level, count in child_counts.items():
                    level_counts[level] = level_counts.get(level, 0) + count
        return level_counts

    element_counts = count_elements_by_level(body)

    def analyze_likely_component_level(counts):
        levels = sorted(counts.keys())
        if len(levels) <= 1:
            return 1, "Only one level present"

        likely_level = 1
        reason = "First layer is the most likely"

        max_count = counts[1]
        for i in range(2, len(levels)):
            prev_count = counts[levels[i-1]]
            curr_count = counts[levels[i]]

            if curr_count < prev_count and prev_count >= max_count * 0.5:
                likely_level = levels[i-1]
                reason = f"Significant decrease after level {levels[i-1]}"
                break

            max_count = max(max_count, curr_count)

        return likely_level, reason

    likely_level, reason = analyze_likely_component_level(element_counts)

    for level, count in sorted(element_counts.items()):
        likeliness = "[bold magenta]LIKELY[/bold magenta]" if level == likely_level else ""
        console.print(f"[cyan]Level {level}: {count} elements[/cyan] {likeliness}")

    console.print(f"\n[bold yellow]Most likely component level: {likely_level}[/bold yellow]")
    console.print(f"[italic]Reason: {reason}[/italic]\n")

    while True:
        user_input = console.input("\n[bold cyan]Enter the level number to capture (or press Enter for the likely level): [/bold cyan]")
        if user_input == "":
            selected_level = likely_level
        else:
            try:
                selected_level = int(user_input)
            except ValueError:
                console.print("[bold red]Invalid input. Please enter a valid level number or press Enter.[/bold red]")
                continue

        if selected_level in element_counts:
            selector = f"body {'> *' * (selected_level - 1)}"
            console.print(f"[bold green]Using selector: {selector}[/bold green]")
            return selector
        else:
            console.print("[bold red]Invalid level. Please enter a valid level number.[/bold red]")

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
        skipped_scripts = 0

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

                    # Check if the element is or contains a script tag
                    is_script = await page.evaluate("""(element) => {
                        return element.tagName === 'SCRIPT' || element.querySelector('script') !== null;
                    }""", element)

                    if is_script:
                        console.print(f"[yellow]⚠️  Element {i} is or contains a script tag, skipping...[/yellow]")
                        skipped_scripts += 1
                        progress.advance(task)
                        continue

                    # Take a screenshot of the specific element
                    await element.screenshot(path=f"{output_dir}/element_{i}.png")
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
        console.print(f"[green]📊 Successful: {successful_screenshots}, Failed: {failed_screenshots}, Skipped scripts: {skipped_scripts}[/green]")

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
    output_dir: str = typer.Option("htmljet", help="Directory to save screenshots", show_default=True),
    all_levels: bool = typer.Option(False, "--all-levels", "-a", help="Capture screenshots for all levels")
):
    """
    📸 Capture screenshots of HTML elements on a webpage.
    """
    console.print("[bold magenta]🎭 Welcome to HTMLJET![/bold magenta]")
    console.print(f"[italic]Preparing to capture elements from {url}[/italic]")

    if all_levels:
        asyncio.run(take_screenshots_all_levels(url, output_dir))
        console.print(f"[bold green]🎉 All done! Your screenshots for all levels are saved in the '{output_dir}' directory.[/bold green]")
    else:
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


