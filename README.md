# 🎨 Elementor Snaps

Elementor Snaps is a beautiful Python CLI tool designed to take screenshots of Elementor pages automatically. It's particularly useful for recreating the UI of Elementor websites using LLMs for other purposes.

## ✨ Why?

This script automates the process of capturing screenshots of individual Elementor components. It's a valuable tool for developers, designers, or anyone needing to analyze or replicate Elementor-based layouts.

## 🚀 Features

- 📸 Automatically captures screenshots of Elementor containers on a given webpage
- 👁️ Handles visibility checks to ensure only visible elements are captured
- 🛡️ Implements error handling for robust operation
- 🎛️ Configurable through an intuitive command-line interface
- 🌈 Beautiful, colorful output with progress bars and emojis

## 📋 Requirements

- Python 3.7+
- Playwright library
- Typer
- Rich

## 🛠️ Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/elementor-snaps.git
   cd elementor-snaps
   ```

2. Install the required dependencies:
   ```
   pip install playwright typer rich
   ```

3. Install the Playwright browsers:
   ```
   playwright install
   ```

## 🎮 Usage

Run the script from the command line, providing the URL of the Elementor page you want to capture:

```
python main.py snap https://example.com/elementor-page
```

Options:
- `--output-dir`: Specify a custom directory for saving screenshots (default: "elementor_screenshots")

Example with custom output directory:
```
python main.py snap https://example.com/elementor-page --output-dir my_screenshots
```

## 📤 Output

- Screenshots are saved as PNG files in the specified output directory (default: `elementor_screenshots`)
- Each screenshot is named `element_X.png`, where X is the index of the Elementor container
- The script provides colorful, emoji-rich output about the progress and results of the screenshot capture process

## ⚠️ Limitations

- The script currently focuses on elements with the attribute `data-element_type="container"`
- Some elements might not be captured if they're not visible when the script runs

## 🤝 Contributing

Contributions to improve Elementor Snaps are welcome! Please feel free to submit pull requests or open issues to suggest improvements or report bugs.

## 📜 License

[MIT License](LICENSE)

## 🎉 Enjoy using Elementor Snaps!

We hope this tool brings a smile to your face while making your Elementor-based design work easier and more enjoyable! 🌟
