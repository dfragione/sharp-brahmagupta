# ⚡ PixShift (Windows 11)

A fast, lightweight, and modern Windows 11 desktop image converter. Convert any image format into **JPG**, **WEBP**, or **AVIF** with drag-and-drop ease.

![PixShift](assets/icon.png)

## ✨ Features

- **Effortless UI**: Drag & drop any image file or whole folder, or click to import.
- **Segmented Format Tabs**: One-click switching between `JPG` (default), `WEBP`, and `AVIF`.
- **Universal Input Formats**: Converts `PNG`, `HEIC`/`HEIF` (iPhone photos), `AVIF`, `WEBP`, `SVG`, `TIFF`, `BMP`, `GIF`, `PSD`, `RAW` (`CR2`, `NEF`, `ARW`, `DNG`), and more.
- **Smart Transparency Handling**: Preserves alpha transparency when converting to WEBP and AVIF; cleanly composites onto solid white when converting to JPG.
- **Auto-Fix EXIF Orientation**: Prevents phone camera photos from ending up rotated sideways.
- **Downloads as Default Output**: Automatically saves converted images directly into your `Downloads` folder (`C:\Users\<User>\Downloads`), with instant 1-click access to open the folder.
- **Delete Original Option**: Optional checkbox to safely move original photos to the Windows Recycle Bin once converted.
- **Quality Controls**: Adjustable image quality slider with quick presets (Max 100%, High 92%, Standard 80%, Small 70%).
- **Batch Processing**: Convert single files or hundreds of photos at once with live progress and non-blocking background workers.
- **In-App Updater**: Built-in update manager to detect new releases and update with 1 click.
- **Standalone Portable `.exe`**: Zero Python installation required for end-users.

---

## 🚀 Running the App

### Option 1: Standalone Portable EXE (No Python Needed)
Run the compiled standalone executable:
```bash
dist\PixShift.exe
```
Or double-click `install.bat` to install **PixShift** into your Start Menu and Desktop!

### Option 2: Run via Python
```bash
pip install -r requirements.txt
python main.py
```

---

## 🛠️ Building the Standalone `.exe`

To compile the standalone Windows executable yourself:
```bash
python build_exe.py
```
This produces `dist\PixShift.exe` which bundles Python, Qt6, Pillow, pillow-heif, and all dependencies into a single double-clickable file.

---

## 🧪 Testing

Run the test suite:
```bash
python -m unittest discover tests
```
