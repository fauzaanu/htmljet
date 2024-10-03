import unittest
import asyncio
from unittest.mock import AsyncMock, patch
import tempfile
from htmljet.main import take_screenshots, app, take_screenshots_all_levels, analyze_html_structure
from typer.testing import CliRunner

class TestHtmlJet(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.app = app

    @patch('htmljet.main.async_playwright')
    @patch('htmljet.main.analyze_html_structure')
    def test_take_screenshots(self, mock_analyze, mock_playwright):
        async def run_test():
            mock_browser = AsyncMock()
            mock_page = AsyncMock()
            mock_element = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value.chromium.launch_persistent_context.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.query_selector_all.return_value = [mock_element]
            mock_element.is_visible.return_value = True
            mock_analyze.return_value = 'body > *'

            # Mock the evaluate method to simulate a non-script element
            mock_page.evaluate.return_value = False

            await take_screenshots("https://example.com", "test_output")

            mock_page.goto.assert_called_once_with("https://example.com")
            mock_page.evaluate.assert_called_once()
            mock_element.screenshot.assert_called_once()

        asyncio.run(run_test())

    @patch('htmljet.main.async_playwright')
    def test_take_screenshots_all_levels(self, mock_playwright):
        async def run_test():
            mock_browser = AsyncMock()
            mock_page = AsyncMock()
            mock_element = AsyncMock()

            mock_playwright.return_value.__aenter__.return_value.chromium.launch_persistent_context.return_value = mock_browser
            mock_browser.new_page.return_value = mock_page
            mock_page.query_selector_all.return_value = [mock_element]
            mock_element.is_visible.return_value = True
            mock_page.content.return_value = "<html><body><div><p>Test</p></div></body></html>"

            with tempfile.TemporaryDirectory() as tmp_dir:
                await take_screenshots_all_levels("https://example.com", tmp_dir)

            mock_page.goto.assert_called_once_with("https://example.com")
            mock_element.screenshot.assert_called()

        asyncio.run(run_test())

    @patch('htmljet.main.async_playwright')
    def test_analyze_html_structure(self, mock_playwright):
        async def run_test():
            mock_page = AsyncMock()
            mock_page.content.return_value = "<html><body><div><p>Test</p></div></body></html>"

            with patch('builtins.input', return_value=''):
                result = await analyze_html_structure(mock_page)

            self.assertEqual(result, 'body > *')

        asyncio.run(run_test())

    @patch('htmljet.main.take_screenshots')
    def test_snap_command(self, mock_take_screenshots):
        async def mock_take_screenshots_async(*args, **kwargs):
            pass

        mock_take_screenshots.side_effect = mock_take_screenshots_async

        result = self.runner.invoke(self.app, ["snap", "https://example.com"])
        self.assertEqual(result.exit_code, 0)
        mock_take_screenshots.assert_called_once()

    @patch('htmljet.main.take_screenshots_all_levels')
    def test_snap_command_all_levels(self, mock_take_screenshots_all_levels):
        async def mock_take_screenshots_all_levels_async(*args, **kwargs):
            pass

        mock_take_screenshots_all_levels.side_effect = mock_take_screenshots_all_levels_async

        result = self.runner.invoke(self.app, ["snap", "https://example.com", "--all-levels"])
        self.assertEqual(result.exit_code, 0)
        mock_take_screenshots_all_levels.assert_called_once()


if __name__ == '__main__':
    unittest.main()
