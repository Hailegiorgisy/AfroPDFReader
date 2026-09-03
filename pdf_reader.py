import json
import os
import sys
import webview

# PyMuPDF is used for fast PDF parsing and searching
import fitz


class AfroPDFAPI:

    def __init__(self):
        self.doc = None
        self.current_pdf_path = None
        self.bookmarks = []

    def open_pdf(self, file_path):
        """Loads PDF using PyMuPDF and extracts page count & table of contents."""
        if not os.path.exists(file_path):
            return {"status": "error", "message": "File not found"}

        try:
            self.doc = fitz.open(file_path)
            self.current_pdf_path = file_path

            # Extract outline/TOC
            raw_toc = self.doc.get_toc()
            toc_data = [
                {"level": item[0], "title": item[1], "page": item[2]}
                for item in raw_toc
            ]

            return {
                "status": "success",
                "file_name": os.path.basename(file_path),
                "total_pages": len(self.doc),
                "toc": toc_data,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def search_text(self, query):
        """Searches document text across all pages and returns match locations."""
        if not self.doc or not query.strip():
            return {"status": "success", "query": query, "results": []}

        results = []
        query_str = query.strip()

        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            text_instances = page.search_for(query_str)

            if text_instances:
                # Extract surrounding text snippet for search context preview
                page_text = page.get_text()
                snippet = self._get_context_snippet(page_text, query_str)

                # Convert bounding boxes (Rects) to serializable dicts
                rects = [
                    {"x0": r.x0, "y0": r.y0, "x1": r.x1, "y1": r.y1}
                    for r in text_instances
                ]

                results.append(
                    {
                        "page": page_num + 1,
                        "matches_count": len(text_instances),
                        "snippet": snippet,
                        "rects": rects,
                    }
                )

        return {"status": "success", "query": query, "results": results}

    def _get_context_snippet(
        self, full_text, query, snippet_len=80
    ) -> str:
        """Helper to format search preview snippets."""
        idx = full_text.lower().find(query.lower())
        if idx == -1:
            return full_text[:snippet_len] + "..."
        start = max(0, idx - 20)
        end = min(len(full_text), idx + len(query) + snippet_len)
        snippet = full_text[start:end].replace("\n", " ")
        return f"...{snippet}..."

    def toggle_bookmark(self, page_number):
        if page_number in self.bookmarks:
            self.bookmarks.remove(page_number)
            action = "removed"
        else:
            self.bookmarks.append(page_number)
            self.bookmarks.sort()
            action = "added"
        return {"status": "success", "action": action, "bookmarks": self.bookmarks}

    def get_bookmarks(self):
        return self.bookmarks


# HTML / CSS / JS Frontend Interface embedded natively
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AfroPDFReader</title>
    <style>
        :root[data-theme="light"] {
            --bg-color: #f8f9fa;
            --sidebar-bg: #e9ecef;
            --text-color: #212529;
            --accent-color: #2563eb;
            --border-color: #dee2e6;
            --hover-bg: #ced4da;
            --highlight-bg: rgba(255, 235, 59, 0.4);
            --highlight-active: rgba(255, 152, 0, 0.7);
        }

        :root[data-theme="dark"] {
            --bg-color: #121212;
            --sidebar-bg: #1e1e1e;
            --text-color: #e0e0e0;
            --accent-color: #3b82f6;
            --border-color: #333333;
            --hover-bg: #2d2d2d;
            --highlight-bg: rgba(255, 235, 59, 0.35);
            --highlight-active: rgba(255, 152, 0, 0.75);
        }

        :root[data-theme="oled"] {
            --bg-color: #000000;
            --sidebar-bg: #0a0a0a;
            --text-color: #ffffff;
            --accent-color: #60a5fa;
            --border-color: #222222;
            --hover-bg: #1a1a1a;
            --highlight-bg: rgba(255, 235, 59, 0.4);
            --highlight-active: rgba(255, 152, 0, 0.8);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }

        body {
            display: flex;
            height: 100vh;
            background-color: var(--bg-color);
            color: var(--text-color);
            overflow: hidden;
        }

        /* Sidebar Styles */
        #sidebar {
            width: 280px;
            background-color: var(--sidebar-bg);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            transition: margin-left 0.2s ease;
        }

        #sidebar.collapsed { margin-left: -280px; }

        .sidebar-header {
            padding: 12px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .tab-buttons { display: flex; border-bottom: 1px solid var(--border-color); }

        .tab-btn {
            flex: 1;
            padding: 8px;
            background: none;
            border: none;
            color: var(--text-color);
            cursor: pointer;
            font-size: 11px;
            text-transform: uppercase;
            font-weight: bold;
            opacity: 0.6;
        }

        .tab-btn.active { opacity: 1; border-bottom: 2px solid var(--accent-color); }

        .sidebar-content { flex: 1; overflow-y: auto; padding: 8px; }

        /* Search Input */
        .search-box {
            padding: 8px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            gap: 4px;
        }

        .search-input {
            flex: 1;
            background: var(--bg-color);
            color: var(--text-color);
            border: 1px solid var(--border-color);
            padding: 6px 8px;
            border-radius: 4px;
            font-size: 12px;
        }

        .nav-item {
            padding: 8px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            margin-bottom: 4px;
            border: 1px solid transparent;
        }

        .nav-item:hover { background-color: var(--hover-bg); }
        .search-snippet { font-size: 11px; opacity: 0.7; margin-top: 2px; }

        /* Main Viewport & Highlights Overlay */
        #main-container { flex: 1; display: flex; flex-direction: column; }

        header {
            height: 48px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 16px;
            background-color: var(--sidebar-bg);
        }

        .controls { display: flex; gap: 8px; align-items: center; }

        button, select {
            background: var(--bg-color);
            color: var(--text-color);
            border: 1px solid var(--border-color);
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }

        #pdf-viewport {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            overflow: auto;
            position: relative;
        }

        .page-canvas-wrapper {
            position: relative;
            width: 595px;
            height: 842px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            background-color: #ffffff;
        }

        .page-canvas {
            width: 100%;
            height: 100%;
            color: #000000;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            position: relative;
        }

        /* Dynamic Page Highlight Overlays */
        .text-highlight {
            position: absolute;
            background-color: var(--highlight-bg);
            border-bottom: 2px solid #f59e0b;
            pointer-events: none;
            border-radius: 2px;
        }
    </style>
</head>
<body>

    <aside id="sidebar">
        <div class="sidebar-header">
            <span style="font-weight: bold; font-size: 14px;">AfroPDF</span>
            <button onclick="toggleSidebar()">✕</button>
        </div>
        <div class="tab-buttons">
            <button class="tab-btn active" id="btn-toc" onclick="switchTab('toc')">Outline</button>
            <button class="tab-btn" id="btn-search" onclick="switchTab('search')">Search</button>
            <button class="tab-btn" id="btn-bm" onclick="switchTab('bookmarks')">Bookmarks</button>
        </div>

        <div id="search-box-container" class="search-box" style="display: none;">
            <input type="text" id="search-query" class="search-input" placeholder="Search document..." onkeyup="handleSearchKey(event)">
            <button onclick="executeSearch()">Find</button>
        </div>

        <div id="sidebar-content" class="sidebar-content"></div>
    </aside>

    <div id="main-container">
        <header>
            <div class="controls">
                <button onclick="toggleSidebar()">☰ Sidebar</button>
                <button onclick="addBookmark()">🔖 Bookmark Page</button>
            </div>
            
            <div class="controls">
                <label for="theme-select" style="font-size: 12px;">Theme:</label>
                <select id="theme-select" onchange="changeTheme(this.value)">
                    <option value="dark" selected>Dark Mode</option>
                    <option value="light">Light Mode</option>
                    <option value="oled">OLED Black</option>
                </select>
            </div>
        </header>

        <div id="pdf-viewport">
            <div class="page-canvas-wrapper" id="canvas-wrapper">
                <div class="page-canvas" id="canvas">
                    Page Viewport (Page 1)
                </div>
                <!-- Dynamic text highlights render here -->
                <div id="highlight-layer"></div>
            </div>
        </div>
    </div>

    <script>
        let currentTab = 'toc';
        let sampleToc = [];
        let searchResults = [];
        let activePage = 1;

        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('collapsed');
        }

        function changeTheme(themeName) {
            document.documentElement.setAttribute('data-theme', themeName);
        }

        function switchTab(tab) {
            currentTab = tab;
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById(`btn-${tab}`).classList.add('active');

            const searchBox = document.getElementById('search-box-container');
            searchBox.style.display = (tab === 'search') ? 'flex' : 'none';

            renderSidebar();
        }

        function handleSearchKey(e) {
            if (e.key === 'Enter') executeSearch();
        }

        function executeSearch() {
            const query = document.getElementById('search-query').value;
            if (!query.trim()) return;

            pywebview.api.search_text(query).then(res => {
                searchResults = res.results;
                renderSidebar();
            });
        }

        function renderSidebar() {
            const container = document.getElementById('sidebar-content');
            container.innerHTML = '';

            if (currentTab === 'toc') {
                sampleToc.forEach(item => {
                    const el = document.createElement('div');
                    el.className = 'nav-item';
                    el.innerText = `${item.title} (p. ${item.page})`;
                    el.onclick = () => jumpToPage(item.page);
                    container.appendChild(el);
                });
            } else if (currentTab === 'search') {
                if (searchResults.length === 0) {
                    container.innerHTML = '<div style="padding:12px; font-size:12px; opacity:0.6;">No search results found.</div>';
                    return;
                }
                searchResults.forEach(res => {
                    const el = document.createElement('div');
                    el.className = 'nav-item';
                    el.innerHTML = `<strong>Page ${res.page}</strong> (${res.matches_count} matches)<div class="search-snippet">${res.snippet}</div>`;
                    el.onclick = () => jumpToPage(res.page, res.rects);
                    container.appendChild(el);
                });
            } else {
                pywebview.api.get_bookmarks().then(bookmarks => {
                    if (bookmarks.length === 0) {
                        container.innerHTML = '<div style="padding:12px; font-size:12px; opacity:0.6;">No bookmarks added.</div>';
                        return;
                    }
                    bookmarks.forEach(page => {
                        const el = document.createElement('div');
                        el.className = 'nav-item';
                        el.innerText = `🔖 Page ${page}`;
                        el.onclick = () => jumpToPage(page);
                        container.appendChild(el);
                    });
                });
            }
        }

        function jumpToPage(page, rects = null) {
            activePage = page;
            document.getElementById('canvas').innerText = `PDF Page Viewport (Page ${page})`;
            renderHighlights(rects);
        }

        function renderHighlights(rects) {
            const layer = document.getElementById('highlight-layer');
            layer.innerHTML = '';

            if (!rects) return;

            // Example coordinate mapping overlay logic
            rects.forEach(r => {
                const hl = document.createElement('div');
                hl.className = 'text-highlight';
                hl.style.left = `${r.x0}px`;
                hl.style.top = `${r.y0}px`;
                hl.style.width = `${r.x1 - r.x0}px`;
                hl.style.height = `${r.y1 - r.y0}px`;
                layer.appendChild(hl);
            });
        }

        function addBookmark() {
            pywebview.api.toggle_bookmark(activePage).then(res => {
                alert(`Page ${activePage} ${res.action} to bookmarks!`);
                if (currentTab === 'bookmarks') renderSidebar();
            });
        }

        window.addEventListener('pywebviewready', function() {
            pywebview.api.open_pdf('sample.pdf').then(data => {
                if (data.status === 'success') {
                    sampleToc = data.toc;
                    renderSidebar();
                }
            });
        });
    </script>
</body>
</html>
"""


def main():
    api = AfroPDFAPI()
    window = webview.create_window(
        title="AfroPDFReader",
        html=HTML_LAYOUT,
        js_api=api,
        width=1000,
        height=700,
        min_size=(800, 500),
    )
    webview.start(debug=False)


if __name__ == "__main__":
    main()
    