# Local Desktop PDF Reader

A lightweight, cross-platform desktop PDF reader application built with Python, PyQt6, and PyMuPDF. It provides a clean, fast interface for opening, viewing, and navigating PDF documents locally without external server dependencies.

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
   git clone [https://github.com/your-username/local-pdf-reader.git](https://github.com/your-username/local-pdf-reader.git)
   cd local-pdf-reader