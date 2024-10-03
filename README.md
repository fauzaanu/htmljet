# HTMLJet

HTMLJet is a command-line tool for capturing screenshots of UI components from any website. 

You would simply run the command 
`htmljet snap https://example.com`

Once the page is loaded, HTMLJet will analyze the HTML structure and display the levels and the amount of child elements within each level. You can then choose the level you want to capture screenshots of.

You can also run 
`htmljet snap https://example.com --all-levels` or `htmljet snap https://example.com -a` to capture screenshots of all levels.

When all levels are captured, the folder will contain a folder for each level, with the screenshots of the elements at that level.

## Installation

To install HTMLJet, you need Python 3.12 or higher. You can install it using pip:

```bash
pip install htmljet
```

## Usage

Usage is as simple as it was described in the introduction. There are no additional options at the moment.

## Use case

I created HTMLJet to make it easy for me to feed UI designs to LLMs to recreate them using my frontend frameworks. For instance taking a screenshot of a wordpress website and asking LLMs to create it with tailwindcss.

The idea is that it would save a lot of time if the files are already present locally within your project, compared to having to go to the website and take screenshots manually of each component, add it to the project and then ask the LLMs to recreate it.

## Development

Make sure you have uv installed.

1. Clone the repo
2. run uv sync

