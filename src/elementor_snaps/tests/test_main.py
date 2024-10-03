import unittest
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio
import os
import tempfile
from PIL import Image
from elementor_snaps.main import take_screenshots, cleanup_similar_images, app
from typer.testing import CliRunner

class TestElementorSnaps(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.app = app

    @patch('elementor_snaps.main.async_playwright')
    def test_take_screenshots(self, mock_playwright):
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_element = AsyncMock()

        mock_playwright.return_value.__aenter__.return_value.chromium.launch_persistent_context.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_page.query_selector_all.return_value = [mock_element]
        mock_element.is_visible.return_value = True

        async def run_test():
            await take_screenshots("https://elementor.com", "test_output")

        asyncio.run(run_test())

        mock_page.goto.assert_called_once_with("https://elementor.com")
        mock_element.screenshot.assert_called_once()

    def test_cleanup_similar_images(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create valid PNG test images
            for i in range(3):
                img = Image.new('RGB', (60, 30), color = (73, 109, 137))
                img.save(os.path.join(tmp_dir, f"image_{i}.png"))

            clean_dir = cleanup_similar_images(tmp_dir)

            self.assertTrue(os.path.exists(clean_dir))
            self.assertEqual(len(os.listdir(clean_dir)), 1)  # Assuming all images are similar

    @patch('elementor_snaps.main.take_screenshots')
    @patch('elementor_snaps.main.cleanup_similar_images')
    def test_snap_command(self, mock_cleanup, mock_take_screenshots):
        mock_take_screenshots.return_value = asyncio.Future()
        mock_take_screenshots.return_value.set_result(None)
        
        result = self.runner.invoke(self.app, ["snap", "https://elementor.com"])
        self.assertEqual(result.exit_code, 0)
        mock_take_screenshots.assert_called_once()
        mock_cleanup.assert_called_once()

    @patch('elementor_snaps.main.cleanup_similar_images')
    def test_cleanup_command(self, mock_cleanup):
        with tempfile.TemporaryDirectory() as tmp_dir:
            for i in range(3):
                with open(os.path.join(tmp_dir, f"image_{i}.png"), "wb") as f:
                    f.write(b"test image content")

            result = self.runner.invoke(self.app, ["cleanup", tmp_dir])
            self.assertEqual(result.exit_code, 0)
            mock_cleanup.assert_called_once_with(tmp_dir, 0.9)

if __name__ == '__main__':
    unittest.main()
