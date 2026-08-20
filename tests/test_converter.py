import os
import shutil
import tempfile
import unittest
from pathlib import Path
from PIL import Image, ImageDraw

import converter_engine

class TestConverterEngine(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="quickjpg_test_")
        self.out_dir = tempfile.mkdtemp(prefix="quickjpg_out_")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)
        shutil.rmtree(self.out_dir, ignore_errors=True)

    def test_png_with_alpha_conversion_to_jpg(self):
        """Test converting transparent RGBA PNG to JPG composites over white."""
        png_path = os.path.join(self.test_dir, "test_alpha.png")
        img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rectangle([25, 25, 75, 75], fill=(255, 0, 0, 255))
        img.save(png_path)

        res = converter_engine.convert_image(
            input_path=png_path,
            output_dir=self.out_dir,
            target_format="JPG",
            quality=90
        )

        self.assertTrue(res["success"])
        self.assertTrue(res["output_path"].endswith(".jpg"))
        self.assertTrue(os.path.exists(res["output_path"]))
        
        with Image.open(res["output_path"]) as jpg:
            self.assertEqual(jpg.format, "JPEG")
            self.assertEqual(jpg.size, (100, 100))
            r, g, b = jpg.getpixel((5, 5))
            self.assertGreaterEqual(r, 250)
            self.assertGreaterEqual(g, 250)
            self.assertGreaterEqual(b, 250)

    def test_png_with_alpha_conversion_to_webp(self):
        """Test converting transparent RGBA PNG to WEBP preserves alpha transparency."""
        png_path = os.path.join(self.test_dir, "test_alpha_webp.png")
        img = Image.new("RGBA", (80, 80), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rectangle([20, 20, 60, 60], fill=(0, 255, 0, 255))
        img.save(png_path)

        res = converter_engine.convert_image(
            input_path=png_path,
            output_dir=self.out_dir,
            target_format="WEBP",
            quality=90
        )

        self.assertTrue(res["success"])
        self.assertTrue(res["output_path"].endswith(".webp"))
        self.assertTrue(os.path.exists(res["output_path"]))

        with Image.open(res["output_path"]) as webp:
            self.assertEqual(webp.format, "WEBP")
            self.assertEqual(webp.mode, "RGBA")
            # Pixel (5, 5) alpha should be 0 (transparent)
            r, g, b, a = webp.getpixel((5, 5))
            self.assertEqual(a, 0)

    def test_png_with_alpha_conversion_to_avif(self):
        """Test converting PNG to AVIF."""
        png_path = os.path.join(self.test_dir, "test_alpha_avif.png")
        img = Image.new("RGBA", (60, 60), (0, 0, 255, 128))
        img.save(png_path)

        res = converter_engine.convert_image(
            input_path=png_path,
            output_dir=self.out_dir,
            target_format="AVIF",
            quality=90
        )

        self.assertTrue(res["success"])
        self.assertTrue(res["output_path"].endswith(".avif"))
        self.assertTrue(os.path.exists(res["output_path"]))

    def test_various_formats_conversion(self):
        """Test converting BMP, TIFF, GIF, WEBP."""
        formats = [
            ("test.bmp", "BMP", "RGB"),
            ("test.tiff", "TIFF", "RGB"),
            ("test.gif", "GIF", "P"),
            ("test.webp", "WEBP", "RGBA")
        ]

        for fname, fmt, mode in formats:
            fpath = os.path.join(self.test_dir, fname)
            img = Image.new(mode, (80, 60), (0, 128, 255) if mode == "RGB" else 1)
            img.save(fpath, format=fmt)

            res = converter_engine.convert_image(
                input_path=fpath,
                output_dir=self.out_dir,
                target_format="JPG"
            )
            self.assertTrue(res["success"], f"Failed for format {fmt}: {res.get('error')}")
            self.assertTrue(os.path.exists(res["output_path"]))

    def test_delete_original_option(self):
        """Test delete_original flag deletes the source file."""
        src_path = os.path.join(self.test_dir, "to_delete.png")
        img = Image.new("RGB", (50, 50), (10, 20, 30))
        img.save(src_path)

        res = converter_engine.convert_image(
            input_path=src_path,
            output_dir=self.out_dir,
            target_format="JPG",
            delete_original=True
        )

        self.assertTrue(res["success"])
        self.assertFalse(os.path.exists(src_path), "Source file should have been deleted")

    def test_default_downloads_folder(self):
        downloads = converter_engine.get_default_downloads_folder()
        self.assertTrue(os.path.exists(downloads))

if __name__ == "__main__":
    unittest.main()
