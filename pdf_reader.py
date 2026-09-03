import base64
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

    def open_file_dialog(self):
        """Opens native file explorer dialog to select a PDF."""
        try:
            # Safely grab the active window or fallback to the first window instance
            window = webview.active_window()
            if not window and webview.windows:
                window = webview.windows[0]

            if not window:
                return {"status": "error", "message": "No active window found"}

            file_types = ("PDF Files (*.pdf)", "All files (*.*)")
            result = window.create_file_dialog(
                webview.OPEN_DIALOG,
                allow_multiple=False,
                file_types=file_types,
            )

            if result and len(result) > 0:
                return self.load_pdf(result[0])
            return {"status": "cancelled"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def load_pdf(self, file_path):
        """Loads PDF, extracts TOC, and encodes file data for rendering."""
        if not os.path.exists(file_path):
            return {"status": "error", "message": "File not found"}

        try:
            self.doc = fitz.open(file_path)
            self.current_pdf_path = file_path
            self.bookmarks = []

            # Extract Table of Contents
            raw_toc = self.doc.get_toc()
            toc_data = [
                {"level": item[0], "title": item[1], "page": item[2]}
                for item in raw_toc
            ]

            # Read binary and convert to base64 for WebView rendering
            with open(file_path, "rb") as f:
                pdf_bytes = f.read()
                pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

            return {
                "status": "success",
                "file_name": os.path.basename(file_path),
                "total_pages": len(self.doc),
                "toc": toc_data,
                "pdf_base64": pdf_base64,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def search_text(self, query):
        """Searches text across all pages in the loaded document."""
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
            --ethiopia-green: #009A44;
            --ethiopia-yellow: #FED100;
            --ethiopia-red: #EF3340;
        }

        :root[data-theme="light"] {
            --bg-color: #f4f6f8;
            --sidebar-bg: #ffffff;
            --text-color: #1a1a1a;
            --accent-color: var(--ethiopia-green);
            --border-color: #e2e8f0;
            --hover-bg: #f1f5f9;
            --header-bg: #ffffff;
        }

        :root[data-theme="dark"] {
            --bg-color: #121417;
            --sidebar-bg: #1a1d24;
            --text-color: #f0f4f8;
            --accent-color: var(--ethiopia-green);
            --border-color: #2d323e;
            --hover-bg: #262b36;
            --header-bg: #1a1d24;
        }

        :root[data-theme="oled"] {
            --bg-color: #000000;
            --sidebar-bg: #090a0c;
            --text-color: #ffffff;
            --accent-color: var(--ethiopia-yellow);
            --border-color: #1f232b;
            --hover-bg: #14171d;
            --header-bg: #090a0c;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, -apple-system, sans-serif; }

        body { display: flex; height: 100vh; background-color: var(--bg-color); color: var(--text-color); overflow: hidden; }

        .cultural-ribbon { height: 3px; width: 100%; display: flex; position: absolute; top: 0; left: 0; z-index: 100; }
        .ribbon-green { flex: 1; background-color: var(--ethiopia-green); }
        .ribbon-yellow { flex: 1; background-color: var(--ethiopia-yellow); }
        .ribbon-red { flex: 1; background-color: var(--ethiopia-red); }

        #sidebar {
            width: 290px;
            background-color: var(--sidebar-bg);
            border-right: 1px solid var(--border-color);
            display: flex; flex-direction: column;
            margin-top: 3px;
        }
        #sidebar.collapsed { margin-left: -290px; }

        .sidebar-header { padding: 14px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; }
        .brand-title { display: flex; align-items: center; gap: 8px; font-weight: 700; color: var(--accent-color); }

        .tab-buttons { display: flex; border-bottom: 1px solid var(--border-color); }
        .tab-btn {
            flex: 1; padding: 10px 4px; background: none; border: none; color: var(--text-color);
            cursor: pointer; font-size: 11px; text-transform: uppercase; font-weight: 600; opacity: 0.65;
            display: flex; align-items: center; justify-content: center; gap: 5px;
        }
        .tab-btn.active { opacity: 1; border-bottom: 2px solid var(--accent-color); color: var(--accent-color); }

        .sidebar-content { flex: 1; overflow-y: auto; padding: 10px; }

        .search-box { padding: 10px; border-bottom: 1px solid var(--border-color); display: flex; gap: 6px; }
        .search-input { flex: 1; background: var(--bg-color); color: var(--text-color); border: 1px solid var(--border-color); padding: 7px 10px; border-radius: 6px; font-size: 12px; }

        .icon-btn {
            background: var(--bg-color); color: var(--text-color); border: 1px solid var(--border-color);
            padding: 6px 12px; border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; font-size: 12px;
        }
        .icon-btn.primary { background-color: var(--accent-color); color: #ffffff; border: none; font-weight: 600; }

        .nav-item { padding: 9px 10px; border-radius: 6px; cursor: pointer; font-size: 12px; margin-bottom: 4px; }
        .nav-item:hover { background-color: var(--hover-bg); }

        #main-container { flex: 1; display: flex; flex-direction: column; margin-top: 3px; }

        header { height: 50px; border-bottom: 1px solid var(--border-color); display: flex; align-items: center; justify-content: space-between; padding: 0 16px; background-color: var(--header-bg); }
        .controls { display: flex; gap: 10px; align-items: center; }

        select { background: var(--bg-color); color: var(--text-color); border: 1px solid var(--border-color); padding: 6px 10px; border-radius: 6px; font-size: 12px; }

        #pdf-viewport { flex: 1; display: flex; align-items: center; justify-content: center; padding: 16px; overflow: auto; }
        iframe { width: 100%; height: 100%; border: none; border-radius: 4px; }

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
            <button class="tab-btn active" id="btn-toc" onclick="switchTab('toc')">Outline</button>
            <button class="tab-btn" id="btn-search" onclick="switchTab('search')">Search</button>
            <button class="tab-btn" id="btn-bm" onclick="switchTab('bookmarks')">Bookmarks</button>
        </div>

        <div id="search-box-container" class="search-box" style="display: none;">
            <input type="text" id="search-query" class="search-input" placeholder="Search text..." onkeyup="if(event.key==='Enter') executeSearch()">
            <button class="icon-btn primary" onclick="executeSearch()">Find</button>
        </div>

        <div id="sidebar-content" class="sidebar-content"></div>
    </aside>

    <div id="main-container">
        <header>
            <div class="controls">
                <button class="icon-btn" onclick="toggleSidebar()">Sidebar</button>
                <button class="icon-btn primary" onclick="openPdfFile()">📂 Open PDF</button>
                <button class="icon-btn" onclick="addBookmark()">🔖 Bookmark Page</button>
            </div>
            
            <div class="controls">
                <select id="theme-select" onchange="changeTheme(this.value)">
                    <option value="dark" selected>Dark Mode</option>
                    <option value="light">Light Mode</option>
                    <option value="oled">OLED Black</option>
                </select>
            </div>
        </header>

        <div id="pdf-viewport">
            <div id="empty-state" style="text-align:center; opacity:0.6; font-size:14px;">
                <p>No PDF loaded.</p>
                <button class="icon-btn primary" style="margin-top:10px;" onclick="openPdfFile()">Click to select a PDF file</button>
            </div>
            <iframe id="pdf-frame" style="display:none;"></iframe>
        </div>
    </div>

    <script>
        let currentTab = 'toc';
        let sampleToc = [];
        let activePage = 1;

        function toggleSidebar() { document.getElementById('sidebar').classList.toggle('collapsed'); }
        function changeTheme(theme) { document.documentElement.setAttribute('data-theme', theme); }

        function switchTab(tab) {
            currentTab = tab;
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById(`btn-${tab}`).classList.add('active');
            document.getElementById('search-box-container').style.display = (tab === 'search') ? 'flex' : 'none';
            renderSidebar();
        }

        function openPdfFile() {
            pywebview.api.open_file_dialog().then(data => {
                if (data.status === 'success') {
                    sampleToc = data.toc;
                    renderSidebar();
                    
                    const iframe = document.getElementById('pdf-frame');
                    document.getElementById('empty-state').style.display = 'none';
                    iframe.style.display = 'block';
                    iframe.src = "data:application/pdf;base64," + data.pdf_base64;
                }
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
                    container.appendChild(el);
                });
            }
        }
    </script>
</body>
</html>
"""


def main():
    api = AfroPDFAPI()
    webview.create_window(
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