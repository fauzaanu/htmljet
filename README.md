# Elementor Snaps

Elementor Snaps is a Python CLI tool for automatically capturing screenshots of Elementor pages. It's designed to assist in analyzing or replicating Elementor-based layouts.

## Features

- Automatically captures screenshots of Elementor containers on a given webpage
- Handles visibility checks to ensure only visible elements are captured
- Implements error handling for robust operation
- Configurable through a command-line interface
- Automatic cleanup of similar images, keeping the larger ones

## Requirements

- Python 3.7+
- Playwright library
- Typer
- Rich
- Pillow
- ImageHash

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/elementor-snaps.git
   cd elementor-snaps
   ```

2. Install the required dependencies:
   ```
   pip install playwright typer rich pillow imagehash
   ```

3. Install the Playwright browsers:
   ```
   playwright install
   ```

## Usage

### Capturing Screenshots

Run the script from the command line, providing the URL of the Elementor page you want to capture:

```
python main.py snap https://example.com/elementor-page
```

Options:
- `--output-dir`: Specify a custom directory for saving screenshots (default: "elementor_screenshots")

### Cleaning Up Existing Images

To clean up similar images in an existing directory:

```
python main.py cleanup /path/to/your/image/directory
```

Options:
- `--similarity-threshold`: Specify the threshold for considering images as similar (default: 0.9, range: 0.0 to 1.0)

## Output

- Screenshots are saved as PNG files in the specified output directory
- Each screenshot is named `element_X.png`, where X is the index of the Elementor container
- Similar images are automatically cleaned up, keeping the larger ones

## Limitations

- The script focuses on elements with the attribute `data-element_type="container"`
- Some elements might not be captured if they're not visible when the script runs
- The image similarity cleanup process may occasionally remove unique images if they are very similar to others

## Contributing

Contributions to improve Elementor Snaps are welcome. Please submit pull requests or open issues to suggest improvements or report bugs.

## License

[MIT License](LICENSE)
