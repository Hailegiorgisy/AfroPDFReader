# AfroPDFReader 📄✨

**AfroPDFReader** is an ultra-lightweight, high-performance desktop PDF reader designed for Windows. Built using **Python**, **pywebview** (utilizing native Windows WebView2), and **PyMuPDF**, it delivers a full-featured reading experience with a portable, standalone executable footprint (~27 MB) and zero runtime dependencies.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![Python](https://img.shields.io/badge/python-3.14-green.svg)

---

## 🌟 Key Features

* 🚀 **Ultra-Lightweight & Portable:** Built without heavy GUI frameworks like Qt or PySide, running as a standalone `.exe` with UPX compression.
* ⚡ **High-Speed Engine:** Powered by PyMuPDF (`fitz`) and MuPDF C-engine backend for rapid rendering and text extraction.
* 🔍 **In-Document Full-Text Search:** Real-time search with match previews, page jumping, and dynamic bounding box highlights overlay.
* 🗂️ **Sidebar Navigation & Outline:** Collapsible sidebar housing Table of Contents (TOC), active bookmarks, and search results.
* 🎨 **Theme Engine:** Instant switching between **Dark Mode**, **Light Mode**, and high-contrast **OLED Black**.
* 🎨 **African & Ethiopian Heritage Branding:** Custom-designed visual identity showcasing vibrant cultural iconography.
* 🔒 **100% Offline & Private:** Operates entirely on your local file system with zero telemetry or network calls.

---

## 🛠️ Tech Stack

* **Language:** Python 3.14
* **UI & Viewport:** [pywebview](https://pywebview.flowrl.com/) (MS WebView2 Bridge)
* **PDF Engine:** [PyMuPDF / fitz](https://pymupdf.readthedocs.io/)
* **Packaging & Compression:** PyInstaller + UPX

---

## 🏗️ Project Structure

```text
AfroPDFReader/
├── pdf_reader.py       # Main Python entry point, JS bridge, & PyMuPDF logic
├── build.py            # Automated Nuitka/PyInstaller build script
├── app_icon.ico        # High-resolution application icon
├── requirements.txt    # Python dependencies
├── setup_script.iss    # Inno Setup installer script
└── README.md           # Project documentation