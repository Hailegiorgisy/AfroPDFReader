# Local Desktop PDF Reader
# AfroPdf 📄✨

**AfroPdf** is an ultra-lightweight, high-performance desktop PDF viewer designed for Windows. Built using Python, `pywebview` (utilizing native Windows WebView2), and Mozilla's PDF.js rendering engine, AfroPdf delivers a full-featured reading experience with an extremely small executable footprint .

---

## 🌟 Key Features

* 🚀 **Ultra-Lightweight Footprint:** Built without heavy GUI frameworks (Qt/PySide), reducing executable size f.
* ⚡ **High-Speed Rendering:** Powered by Mozilla's trusted `PDF.js` web engine for smooth page rendering and scrolling.
* 🎨 **African & Ethiopian Heritage Iconography:** Custom-designed visual identity showcasing vibrant Ethiopian colors (Green, Yellow, Red) and geometric cultural motifs.
* 🔒 **Offline First:** Completely self-contained with no external server or internet connectivity required.

---

## 🏗️ Project Structure

```text
AfroPdf/
├── app.py              # Main Python entry point & pywebview native bridge
├── app.spec            # PyInstaller build configuration
├── app_icon.ico        # High-resolution application icon
├── web/                # Frontend application resources
│   ├── index.html      # UI layout & file selection interface
│   └── pdfjs/          # Embedded PDF.js engine files
└── README.md           # Project documentation

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-brightgreen.svg)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-informational.svg)

---

## Features

* **Fast Rendering:** Powered by PyMuPDF (`fitz`) for quick page load times.
* **Smooth Page Navigation:** Next/Previous controls and direct page tracking.
* **Dynamic Zooming:** Dynamic resolution scaling for clear text reading.
* **Fully Offline:** Operates entirely locally on your file system without telemetry or data transfers.

---

## Tech Stack

* **Language:** Python 3.9+
* **GUI Framework:** PyQt6
* **PDF Processing Engine:** PyMuPDF (`pymupdf`)
* **Packaging:** PyInstaller & Inno Setup

---

## Getting Started

### Prerequisites

Ensure you have Python 3.9 or higher installed on your machine.

### Installation & Local Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/HAILEGIOGRIGY/AFROPDFREADER.git]
   cd local-pdf-reader