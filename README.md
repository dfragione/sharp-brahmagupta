# ⚡ QuickJPG Converter (Windows 11)

A fast, lightweight, and modern Windows 11 desktop app to convert any image format into high-quality JPGs with zero friction.

![QuickJPG](assets/icon.png)

## ✨ Features

- **Effortless UI**: Drag & drop any image file or whole folder, or click to import.
- **Universal Format Support**: Converts `PNG`, `HEIC`/`HEIF` (iPhone photos), `AVIF`, `WEBP`, `SVG`, `TIFF`, `BMP`, `GIF`, `PSD`, `RAW` (`CR2`, `NEF`, `ARW`, `DNG`), and more.
- **Smart Transparency Handling**: Seamlessly composites transparent backgrounds (PNG, WEBP, SVG) onto clean white so images never have ugly black backgrounds.
- **Auto-Fix EXIF Orientation**: Prevents phone camera photos from ending up rotated sideways.
- **Downloads as Default Output**: Automatically saves converted JPGs to your `Downloads` folder, with instant 1-click access to open the folder.
- **Delete Original Option**: Optional checkbox to safely move original photos to the Windows Recycle Bin once converted.
- **Quality Controls**: Adjustable JPG quality slider with presets (Max 100%, High 92%, Standard 80%, Small 70%).
- **Batch Processing**: Convert single files or hundreds of photos at once with live progress and non-blocking background workers.
- **Standalone Portable `.exe`**: No Python installation required for end-users.

---

## 🚀 Running the App

### Option 1: Standalone Portable EXE (No Python Needed)
Run the compiled standalone executable:
```bash
dist\QuickJPG.exe
```
Or double-click `install.bat` to install QuickJPG into your Start Menu and Desktop!

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
This produces `dist\QuickJPG.exe` which bundles Python and all dependencies into a single double-clickable file.

---

## 🧪 Testing

Run the test suite:
```bash
python -m unittest discover tests
```
