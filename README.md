# # Elementor Snaps

Elementor Snaps is a Python script designed to take screenshots of Elementor pages automatically. It's particularly useful for recreating the UI of Elementor websites using LLMs for other purposes.

## Why?

This script automates the process of capturing screenshots of individual Elementor components. It can be a valuable tool for developers, designers, or anyone needing to analyze or replicate Elementor-based layouts.

## Features

- Automatically captures screenshots of Elementor containers on a given webpage
- Handles visibility checks to ensure only visible elements are captured
- Implements error handling and logging for robust operation
- Configurable through command-line arguments

## Requirements

- Python 3.7+
- Playwright library

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/elementor-snaps.git
   cd elementor-snaps
   ```

2. Install the required dependencies:
   ```
   pip install playwright
   ```

3. Install the Playwright browsers:
   ```
   playwright install
   ```

## Usage

Run the script from the command line, providing the URL of the Elementor page you want to capture:

```
python main.py https://example.com/elementor-page
```

The script will create a directory named `elementor_screenshots` in the current working directory and save the captured screenshots there.

## Output

- Screenshots are saved as PNG files in the `elementor_screenshots` directory
- Each screenshot is named `element_X.png`, where X is the index of the Elementor container
- The script logs information about successful and failed screenshot attempts

## Limitations

- The script currently focuses on elements with the attribute `data-element_type="container"`
- Some elements might not be captured if they're not visible when the script runs

## Contributing

Contributions to improve Elementor Snaps are welcome! Please feel free to submit pull requests or open issues to suggest improvements or report bugs.

## License

[MIT License](LICENSE)
