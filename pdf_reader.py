import json
import os
import sys
import webview
import fitz  # PyMuPDF


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
                page_text = page.get_text()
                snippet = self._get_context_snippet(page_text, query_str)
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

    def _get_context_snippet(self, full_text, query, snippet_len=80) -> str:
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


HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AfroPDFReader</title>
    <style>
        :root {
            /* Ethiopian Flag & Cultural Motif Colors */
            --ethiopia-green: #009A44;
            --ethiopia-yellow: #FED100;
            --ethiopia-red: #EF3340;
            --ethiopia-gold: #D4AF37;
        }

        :root[data-theme="light"] {
            --bg-color: #f4f6f8;
            --sidebar-bg: #ffffff;
            --text-color: #1a1a1a;
            --accent-color: var(--ethiopia-green);
            --accent-hover: #007a36;
            --border-color: #e2e8f0;
            --hover-bg: #f1f5f9;
            --highlight-bg: rgba(254, 209, 0, 0.45);
            --header-bg: #ffffff;
        }

        :root[data-theme="dark"] {
            --bg-color: #121417;
            --sidebar-bg: #1a1d24;
            --text-color: #f0f4f8;
            --accent-color: var(--ethiopia-green);
            --accent-hover: #02b853;
            --border-color: #2d323e;
            --hover-bg: #262b36;
            --highlight-bg: rgba(254, 209, 0, 0.35);
            --header-bg: #1a1d24;
        }

        :root[data-theme="oled"] {
            --bg-color: #000000;
            --sidebar-bg: #090a0c;
            --text-color: #ffffff;
            --accent-color: var(--ethiopia-yellow);
            --accent-hover: #e0b800;
            --border-color: #1f232b;
            --hover-bg: #14171d;
            --highlight-bg: rgba(239, 51, 64, 0.4);
            --header-bg: #090a0c;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }

        body {
            display: flex;
            height: 100vh;
            background-color: var(--bg-color);
            color: var(--text-color);
            overflow: hidden;
        }

        /* Top Cultural Accent Ribbon */
        .cultural-ribbon {
            height: 3px;
            width: 100%;
            display: flex;
            position: absolute;
            top: 0;
            left: 0;
            z-index: 100;
        }
        .ribbon-green { flex: 1; background-color: var(--ethiopia-green); }
        .ribbon-yellow { flex: 1; background-color: var(--ethiopia-yellow); }
        .ribbon-red { flex: 1; background-color: var(--ethiopia-red); }

        /* Sidebar Styles */
        #sidebar {
            width: 290px;
            background-color: var(--sidebar-bg);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            transition: margin-left 0.2s ease;
            margin-top: 3px;
        }

        #sidebar.collapsed { margin-left: -290px; }

        .sidebar-header {
            padding: 14px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .brand-title {
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 700;
            font-size: 15px;
            color: var(--accent-color);
        }

        .tab-buttons { display: flex; border-bottom: 1px solid var(--border-color); }

        .tab-btn {
            flex: 1;
            padding: 10px 4px;
            background: none;
            border: none;
            color: var(--text-color);
            cursor: pointer;
            font-size: 11px;
            text-transform: uppercase;
            font-weight: 600;
            opacity: 0.65;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 5px;
            transition: all 0.2s;
        }

        .tab-btn.active {
            opacity: 1;
            border-bottom: 2px solid var(--accent-color);
            color: var(--accent-color);
        }

        .sidebar-content { flex: 1; overflow-y: auto; padding: 10px; }

        /* Search Input Area */
        .search-box {
            padding: 10px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            gap: 6px;
        }

        .search-input {
            flex: 1;
            background: var(--bg-color);
            color: var(--text-color);
            border: 1px solid var(--border-color);
            padding: 7px 10px;
            border-radius: 6px;
            font-size: 12px;
            outline: none;
        }

        .search-input:focus {
            border-color: var(--accent-color);
        }

        .icon-btn {
            background: var(--bg-color);
            color: var(--text-color);
            border: 1px solid var(--border-color);
            padding: 6px 10px;
            border-radius: 6px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            font-weight: 500;
            transition: all 0.15s ease;
        }

        .icon-btn:hover {
            background-color: var(--hover-bg);
            border-color: var(--accent-color);
        }

        .icon-btn.primary {
            background-color: var(--accent-color);
            color: #ffffff;
            border: none;
        }

        .icon-btn.primary:hover {
            background-color: var(--accent-hover);
        }

        .nav-item {
            padding: 9px 10px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            margin-bottom: 4px;
            border: 1px solid transparent;
            transition: background-color 0.15s;
        }

        .nav-item:hover { background-color: var(--hover-bg); }
        .search-snippet { font-size: 11px; opacity: 0.7; margin-top: 3px; }

        /* Main Viewport Header */
        #main-container { flex: 1; display: flex; flex-direction: column; margin-top: 3px; }

        header {
            height: 50px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 16px;
            background-color: var(--header-bg);
        }

        .controls { display: flex; gap: 10px; align-items: center; }

        select {
            background: var(--bg-color);
            color: var(--text-color);
            border: 1px solid var(--border-color);
            padding: 6px 10px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            outline: none;
        }

        #pdf-viewport {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 24px;
            overflow: auto;
            position: relative;
        }

        .page-canvas-wrapper {
            position: relative;
            width: 595px;
            height: 842px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.25);
            background-color: #ffffff;
            border-radius: 4px;
        }

        .page-canvas {
            width: 100%;
            height: 100%;
            color: #1a1a1a;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            position: relative;
        }

        .text-highlight {
            position: absolute;
            background-color: var(--highlight-bg);
            border-bottom: 2px solid var(--ethiopia-red);
            pointer-events: none;
            border-radius: 2px;
        }

        svg { fill: currentColor; }
    </style>
</head>
<body>

    <div class="cultural-ribbon">
        <div class="ribbon-green"></div>
        <div class="ribbon-yellow"></div>
        <div class="ribbon-red"></div>
    </div>

    <aside id="sidebar">
        <div class="sidebar-header">
            <div class="brand-title">
                <svg width="18" height="18" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-9 14l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
                <span>AfroPDF</span>
            </div>
            <button class="icon-btn" onclick="toggleSidebar()" style="padding: 4px 8px;">✕</button>
        </div>
        
        <div class="tab-buttons">
            <button class="tab-btn active" id="btn-toc" onclick="switchTab('toc')">
                <svg width="14" height="14" viewBox="0 0 24 24"><path d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V7H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 7v2h14V7H7z"/></svg>
                Outline
            </button>
            <button class="tab-btn" id="btn-search" onclick="switchTab('search')">
                <svg width="14" height="14" viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
                Search
            </button>
            <button class="tab-btn" id="btn-bm" onclick="switchTab('bookmarks')">
                <svg width="14" height="14" viewBox="0 0 24 24"><path d="M17 3H7c-1.1 0-1.99.9-1.99 2L5 21l7-3 7 3V5c0-1.1-.9-2-2-2z"/></svg>
                Bookmarks
            </button>
        </div>

        <div id="search-box-container" class="search-box" style="display: none;">
            <input type="text" id="search-query" class="search-input" placeholder="Search in document..." onkeyup="handleSearchKey(event)">
            <button class="icon-btn primary" onclick="executeSearch()">Find</button>
        </div>

        <div id="sidebar-content" class="sidebar-content"></div>
    </aside>

    <div id="main-container">
        <header>
            <div class="controls">
                <button class="icon-btn" onclick="toggleSidebar()">
                    <svg width="16" height="16" viewBox="0 0 24 24"><path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/></svg>
                    Sidebar
                </button>
                <button class="icon-btn" onclick="addBookmark()">
                    <svg width="16" height="16" viewBox="0 0 24 24" style="fill: var(--ethiopia-red);"><path d="M17 3H7c-1.1 0-1.99.9-1.99 2L5 21l7-3 7 3V5c0-1.1-.9-2-2-2z"/></svg>
                    Bookmark Page
                </button>
            </div>
            
            <div class="controls">
                <svg width="16" height="16" viewBox="0 0 24 24"><path d="M12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9c0-.46-.04-.92-.1-1.36-.98 1.37-2.58 2.26-4.4 2.26-2.98 0-5.4-2.42-5.4-5.4 0-1.81.89-3.42 2.26-4.4-.44-.06-.9-.1-1.36-.1z"/></svg>
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
                if (sampleToc.length === 0) {
                    container.innerHTML = '<div style="padding:12px; font-size:12px; opacity:0.6;">No outline available.</div>';
                    return;
                }
                sampleToc.forEach(item => {
                    const el = document.createElement('div');
                    el.className = 'nav-item';
                    el.innerText = `${item.title} (p. ${item.page})`;
                    el.onclick = () => jumpToPage(item.page);
                    container.appendChild(el);
                });
            } else if (currentTab === 'search') {
                if (searchResults.length === 0) {
                    container.innerHTML = '<div style="padding:12px; font-size:12px; opacity:0.6;">No search results.</div>';
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
        width=1020,
        height=720,
        min_size=(800, 500),
    )
    webview.start(debug=False)


if __name__ == "__main__":
    main()