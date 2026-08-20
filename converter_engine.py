import os
import sys
import io
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List

from PIL import Image, ImageOps

# Register HEIF/HEIC and AVIF support
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    HEIF_AVAILABLE = True
except Exception:
    HEIF_AVAILABLE = False

# Safe deletion via Recycle Bin
try:
    import send2trash
    SEND2TRASH_AVAILABLE = True
except ImportError:
    SEND2TRASH_AVAILABLE = False


SUPPORTED_EXTENSIONS = {
    # Standard formats
    ".png", ".webp", ".bmp", ".gif", ".tiff", ".tif", ".ico", ".tga",
    ".ppm", ".pgm", ".pbm", ".pnm", ".pcx", ".dds", ".dib", ".icns",
    # Modern & Apple formats
    ".heic", ".heif", ".avif", ".hif",
    # Adobe & Vector formats
    ".psd", ".psb", ".svg", ".eps",
    # Camera RAW
    ".cr2", ".nef", ".arw", ".dng", ".orf", ".rw2", ".pef", ".raf",
    # JPEG formats
    ".jpeg", ".jpg", ".jfif", ".jpe"
}

TARGET_FORMATS = {
    "JPG": {"ext": ".jpg", "format": "JPEG", "supports_alpha": False, "desc": "High Compatibility JPEG"},
    "WEBP": {"ext": ".webp", "format": "WEBP", "supports_alpha": True, "desc": "Lightweight WebP (Preserves Alpha)"},
    "AVIF": {"ext": ".avif", "format": "AVIF", "supports_alpha": True, "desc": "Next-Gen AVIF (Preserves Alpha)"}
}


def get_default_downloads_folder() -> str:
    """Returns the path to the user's Downloads directory."""
    downloads = Path.home() / "Downloads"
    if not downloads.exists():
        downloads.mkdir(parents=True, exist_ok=True)
    return str(downloads)


def is_supported_image(filepath: str) -> bool:
    """Checks if a file has a supported image extension."""
    ext = Path(filepath).suffix.lower()
    return ext in SUPPORTED_EXTENSIONS


def get_format_badge(filepath: str) -> str:
    """Returns a clean uppercase format badge string (e.g., 'HEIC', 'PNG')."""
    ext = Path(filepath).suffix.lower().lstrip(".")
    if not ext:
        return "IMG"
    if ext in ("jpeg", "jfif", "jpe"):
        return "JPG"
    if ext in ("tiff", "tif"):
        return "TIFF"
    return ext.upper()


def get_file_size_str(size_bytes: int) -> str:
    """Converts bytes to human readable format (KB, MB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def render_svg_to_image(svg_path: str, max_dimension: int = 2400) -> Image.Image:
    """
    Renders an SVG file to a PIL Image using PyQt6 QtSvg if available,
    with high resolution and crisp anti-aliasing.
    """
    try:
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtGui import QImage, QPainter, QColor
        from PyQt6.QtCore import QByteArray, QSize, QBuffer, QIODevice

        renderer = QSvgRenderer(svg_path)
        if not renderer.isValid():
            raise ValueError("Invalid SVG file")

        default_size = renderer.defaultSize()
        w = default_size.width() if default_size.width() > 0 else 1000
        h = default_size.height() if default_size.height() > 0 else 1000

        scale = 1.0
        if max(w, h) < max_dimension:
            scale = min(max_dimension / max(w, h), 4.0)
            w = int(w * scale)
            h = int(h * scale)

        qimage = QImage(w, h, QImage.Format.Format_ARGB32)
        qimage.fill(QColor(255, 255, 255, 0))

        painter = QPainter(qimage)
        renderer.render(painter)
        painter.end()

        buffer = QByteArray()
        qbuffer = QBuffer(buffer)
        qbuffer.open(QIODevice.OpenModeFlag.WriteOnly)
        qimage.save(qbuffer, "PNG")
        qbuffer.close()

        pil_img = Image.open(io.BytesIO(buffer.data()))
        return pil_img.copy()
    except Exception as e:
        raise RuntimeError(f"Could not render SVG: {e}")


def get_unique_output_path(target_folder: str, original_filename: str, target_ext: str = ".jpg") -> str:
    """Generates a non-conflicting output filename in target_folder with target_ext."""
    base_name = Path(original_filename).stem
    target_dir = Path(target_folder)
    target_dir.mkdir(parents=True, exist_ok=True)

    if not target_ext.startswith("."):
        target_ext = f".{target_ext}"

    candidate = target_dir / f"{base_name}{target_ext}"
    counter = 1
    while candidate.exists():
        candidate = target_dir / f"{base_name} ({counter}){target_ext}"
        counter += 1

    return str(candidate)


def convert_image(
    input_path: str,
    output_dir: Optional[str] = None,
    target_format: str = "JPG",
    quality: int = 92,
    delete_original: bool = False,
    background_color: Tuple[int, int, int] = (255, 255, 255),
    overwrite: bool = False
) -> Dict[str, Any]:
    """
    Converts any supported image format to JPG, WEBP, or AVIF.

    Args:
        input_path: Path to source image.
        output_dir: Destination folder (defaults to Downloads).
        target_format: "JPG", "WEBP", or "AVIF" (default "JPG").
        quality: Image quality (1-100, default 92).
        delete_original: If True, moves original image to Recycle Bin after conversion.
        background_color: RGB tuple to replace transparency when target doesn't support alpha.
        overwrite: If True, overwrites existing file with same name.

    Returns:
        Dict with status, output_path, sizes, dimensions, and error details.
    """
    input_file = Path(input_path)
    if not input_file.exists():
        return {
            "success": False,
            "input_path": input_path,
            "error": "Source file does not exist"
        }

    # Normalize target format
    target_fmt_key = target_format.upper()
    if target_fmt_key not in TARGET_FORMATS:
        target_fmt_key = "JPG"

    fmt_info = TARGET_FORMATS[target_fmt_key]
    target_ext = fmt_info["ext"]
    pil_format = fmt_info["format"]
    supports_alpha = fmt_info["supports_alpha"]

    # Determine destination folder
    if not output_dir:
        output_dir = get_default_downloads_folder()
    
    out_dir_path = Path(output_dir)
    out_dir_path.mkdir(parents=True, exist_ok=True)

    if overwrite:
        output_path = str(out_dir_path / f"{input_file.stem}{target_ext}")
    else:
        output_path = get_unique_output_path(output_dir, input_file.name, target_ext)

    original_size = input_file.stat().st_size

    try:
        ext = input_file.suffix.lower()

        # Handle SVG vector files
        if ext == ".svg":
            img = render_svg_to_image(str(input_file))
        else:
            with Image.open(str(input_file)) as raw_img:
                img = raw_img.copy()

        # 1. Correct EXIF Orientation
        try:
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass

        # 2. Handle Multi-frame images (GIF, TIFF) -> Grab first frame
        try:
            img.seek(0)
        except Exception:
            pass

        # 3. Handle Alpha Channel & Color Space
        has_alpha = img.mode in ("RGBA", "LA", "PA") or (img.mode == "P" and "transparency" in img.info)

        if supports_alpha and has_alpha:
            # Preserve full alpha transparency for WEBP / AVIF
            final_img = img.convert("RGBA")
        elif not supports_alpha and has_alpha:
            # Composite onto solid background for JPG
            img_rgba = img.convert("RGBA")
            bg = Image.new("RGBA", img_rgba.size, background_color + (255,))
            combined = Image.alpha_composite(bg, img_rgba)
            final_img = combined.convert("RGB")
        elif img.mode == "CMYK":
            final_img = img.convert("RGB")
        elif img.mode not in ("RGB", "RGBA"):
            final_img = img.convert("RGB")
        else:
            final_img = img

        width, height = final_img.size
        quality = max(1, min(100, int(quality)))

        # 4. Save per format
        if pil_format == "JPEG":
            final_img.save(
                output_path,
                format="JPEG",
                quality=quality,
                optimize=True,
                progressive=True
            )
        elif pil_format == "WEBP":
            final_img.save(
                output_path,
                format="WEBP",
                quality=quality,
                method=6
            )
        elif pil_format == "AVIF":
            final_img.save(
                output_path,
                format="AVIF",
                quality=quality
            )
        else:
            final_img.save(output_path, format=pil_format, quality=quality)

        output_size = Path(output_path).stat().st_size

        # 5. Delete original file if requested
        deleted = False
        if delete_original:
            try:
                if Path(output_path).resolve() != input_file.resolve():
                    if SEND2TRASH_AVAILABLE:
                        send2trash.send2trash(str(input_file.resolve()))
                    else:
                        os.remove(str(input_file.resolve()))
                    deleted = True
            except Exception as del_err:
                print(f"Warning: Could not delete original file {input_path}: {del_err}")

        return {
            "success": True,
            "input_path": str(input_file),
            "output_path": output_path,
            "filename": input_file.name,
            "output_filename": Path(output_path).name,
            "original_size": original_size,
            "output_size": output_size,
            "dimensions": (width, height),
            "deleted_original": deleted,
            "target_format": target_fmt_key,
            "format": get_format_badge(str(input_file))
        }

    except Exception as e:
        return {
            "success": False,
            "input_path": str(input_file),
            "filename": input_file.name,
            "error": str(e)
        }


# Backwards compatibility alias
def convert_image_to_jpg(input_path: str, output_dir: Optional[str] = None, quality: int = 92, delete_original: bool = False) -> Dict[str, Any]:
    return convert_image(input_path, output_dir=output_dir, target_format="JPG", quality=quality, delete_original=delete_original)
