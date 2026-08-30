import sys
import pymupdf  # PyMuPDF engine
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QHBoxLayout, QLabel,
    QMainWindow, QPushButton, QScrollArea, QVBoxLayout, QWidget
)

class PDFReader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.doc = None
        self.current_page = 0
        self.zoom_factor = 1.5  # Controls render quality/scale
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Python Local PDF Reader")
        self.setGeometry(100, 100, 900, 700)

        # Main Layout Setup
        main_widget = QWidget()
        self.layout = QVBoxLayout(main_widget)

        # Toolbar / Control Controls
        controls = QHBoxLayout()

        self.btn_open = QPushButton("Open PDF")
        self.btn_open.clicked.connect(self.open_pdf)
        controls.addWidget(self.btn_open)

        self.btn_prev = QPushButton("◄ Previous")
        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_prev.setEnabled(False)
        controls.addWidget(self.btn_prev)

        self.page_label = QLabel("Page: 0 / 0")
        controls.addWidget(self.page_label)

        self.btn_next = QPushButton("Next ►")
        self.btn_next.clicked.connect(self.next_page)
        self.btn_next.setEnabled(False)
        controls.addWidget(self.btn_next)

        self.btn_zoom_in = QPushButton("Zoom +")
        self.btn_zoom_in.clicked.connect(lambda: self.zoom(1.2))
        controls.addWidget(self.btn_zoom_in)

        self.btn_zoom_out = QPushButton("Zoom -")
        self.btn_zoom_out.clicked.connect(lambda: self.zoom(0.8))
        controls.addWidget(self.btn_zoom_out)

        self.layout.addLayout(controls)

        # Scrollable Area for PDF Display
        self.scroll_area = QScrollArea()
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label = QLabel()
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)

        self.setCentralWidget(main_widget)

    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open PDF File", "", "PDF Files (*.pdf)"
        )
        if file_path:
            self.doc = pymupdf.open(file_path)
            self.current_page = 0
            self.render_page()

    def render_page(self):
        if not self.doc:
            return

        # Render PDF page to a PyMuPDF Pixmap matrix
        page = self.doc.load_page(self.current_page)
        matrix = pymupdf.Matrix(self.zoom_factor, self.zoom_factor)
        pix = page.get_pixmap(matrix=matrix)

        # Convert raw RGB byte stream to PyQt QImage
        qimg = QImage(
            pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888
        )
        
        # Display image on QLabel
        pixmap = QPixmap.fromImage(qimg)
        self.image_label.setPixmap(pixmap)
        self.image_label.adjustSize()

        # Update Navigation State
        self.page_label.setText(f"Page: {self.current_page + 1} / {len(self.doc)}")
        self.btn_prev.setEnabled(self.current_page > 0)
        self.btn_next.setEnabled(self.current_page < len(self.doc) - 1)

    def prev_page(self):
        if self.doc and self.current_page > 0:
            self.current_page -= 1
            self.render_page()

    def next_page(self):
        if self.doc and self.current_page < len(self.doc) - 1:
            self.current_page += 1
            self.render_page()

    def zoom(self, factor):
        if self.doc:
            self.zoom_factor *= factor
            self.render_page()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = PDFReader()
    viewer.show()
    sys.exit(app.exec())
window = webview.create_window(
    'AfroPDF Reader',
    url=os.path.join(web_dir, 'index.html'),
    js_api=api,
    width=1000,
    height=700
)