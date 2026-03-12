# Markdown Reader

A feature-rich desktop markdown viewer for Linux, built with PyQt6.

## Features

- **Rendered markdown display** with GitHub-flavored syntax (tables, task lists, strikethrough, footnotes)
- **Mermaid diagrams** rendered inline via CDN
- **LaTeX math** (inline and display) rendered via KaTeX
- **Syntax-highlighted code blocks** with Pygments
- **Table of contents** sidebar with click-to-navigate
- **Search** (Ctrl+F) with case-sensitive option
- **Bookmarks** - save and jump to positions across files
- **Multiple themes** - Light, Dark, Sepia, High Contrast (applied to the entire UI)
- **Export** to standalone HTML or PDF
- **Print preview** with system print dialog
- **Presentation mode** - splits document at H1/H2 headings into a fullscreen slideshow
- **Split view** - view two documents side by side
- **Drag & drop** - drop a `.md` file onto the window to open it
- **Fullscreen** reading mode (F11)
- **Scroll memory** - remembers your position in each file
- **Recent files** menu with keyboard shortcuts

## Install

### Ubuntu / Debian (.deb package)

Download the `.deb` from [Releases](https://github.com/TioGlo/md_reader/releases) or build it yourself:

```bash
./build-deb.sh
sudo apt install ./md-reader_0.5.0_all.deb
```

Then launch from the app menu or run `md-reader` from the terminal.

### From source

Requires Python 3.10+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/TioGlo/md_reader.git
cd md_reader
uv sync
uv run python main.py
```

Or with pip:

```bash
pip install pyqt6 pyqt6-webengine markdown2 pygments
python main.py
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+O | Open file |
| Ctrl+F | Find in document |
| Ctrl+B | Add bookmark |
| Ctrl+Shift+B | Toggle bookmarks panel |
| Ctrl+T | Toggle table of contents |
| Ctrl+Shift+S | Toggle split view |
| Ctrl+P | Print |
| Ctrl+Shift+V | Print preview |
| Ctrl+Shift+H | Export as HTML |
| Ctrl+Shift+P | Export as PDF |
| F5 | Presentation mode |
| F11 | Fullscreen |
| Ctrl++/- | Font size |
| Ctrl+0 | Reset font size |
| Esc | Exit fullscreen / presentation |

## Project Structure

```
md_reader/
├── main.py              # Entry point
├── core/                # Markdown rendering, TOC generation, file I/O
├── config/              # Settings and theme management
├── ui/                  # All GUI components
├── resources/           # Themes, desktop entry, icon
├── examples/            # Sample markdown files (Mermaid, LaTeX)
└── build-deb.sh         # Debian package builder
```

## License

MIT
