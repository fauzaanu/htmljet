import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from elementor_snaps.main import take_screenshots, cleanup_similar_images, snap, cleanup
import os
import shutil
from typer.testing import CliRunner

runner = CliRunner()

@pytest.mark.asyncio
async def test_take_screenshots():
    with patch('elementor_snaps.main.async_playwright') as mock_playwright:
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_element = AsyncMock()

        mock_playwright.return_value.__aenter__.return_value.chromium.launch_persistent_context.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_page.query_selector_all.return_value = [mock_element]
        mock_element.is_visible.return_value = True

        await take_screenshots("https://elementor.com/", "test_output")

        mock_page.goto.assert_called_once_with("https://elementor.com/")
        mock_element.screenshot.assert_called_once()

def test_cleanup_similar_images(tmp_path):
    # Create test images
    img_dir = tmp_path / "test_images"
    img_dir.mkdir()
    for i in range(3):
        with open(img_dir / f"image_{i}.png", "w") as f:
            f.write("test image content")

    clean_dir = cleanup_similar_images(str(img_dir))

    assert os.path.exists(clean_dir)
    assert len(os.listdir(clean_dir)) == 3  # Assuming all images are unique

def test_snap_command():
    with patch('elementor_snaps.main.asyncio.run'), \
         patch('elementor_snaps.main.cleanup_similar_images'):
        result = runner.invoke(snap, ["http://test.com"])
        assert result.exit_code == 0

def test_cleanup_command(tmp_path):
    img_dir = tmp_path / "test_images"
    img_dir.mkdir()
    for i in range(3):
        with open(img_dir / f"image_{i}.png", "w") as f:
            f.write("test image content")

    result = runner.invoke(cleanup, [str(img_dir)])
    assert result.exit_code == 0
