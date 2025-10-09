# Markdown Reader - Design Document

## Project Overview

A simple, modular GUI markdown reader built in Python with a focus on clean architecture and easy extensibility.

## Core Principles

- **Simplicity**: Easy to use with intuitive interface
- **Modularity**: Highly modular code structure for easy enhancement
- **Usability**: Practical features for comfortable reading experience

## Technical Stack

### GUI Framework
**PyQt6** or **PySide6**
- Native look and feel across platforms
- QWebEngineView for HTML rendering
- Rich widget library
- Excellent documentation and community support

### Markdown Processing
- Pluggable backend (markdown2, mistune, or markdown-it-py)
- Extensions support: tables, fenced code blocks, footnotes
- Syntax highlighting: Pygments integration

### Configuration
- Persistent settings storage (JSON/TOML)
- User preferences tracking
- Window state persistence

## Project Structure

```
md_reader/
├── main.py                     # Application entry point
├── ui/
│   ├── __init__.py
│   ├── main_window.py          # MainWindow class - coordinates all UI
│   ├── menu_bar.py             # Menu system and actions
│   ├── viewer_widget.py        # Markdown display area (HTML renderer)
│   ├── toc_widget.py           # Table of contents sidebar
│   └── toolbar.py              # Quick access toolbar
├── core/
│   ├── __init__.py
│   ├── markdown_renderer.py    # MD → HTML conversion
│   ├── document_manager.py     # File I/O operations
│   └── toc_generator.py        # TOC extraction from headers
├── config/
│   ├── __init__.py
│   ├── settings_manager.py     # Persistent configuration
│   └── theme_manager.py        # Theme/CSS management
├── resources/
│   ├── themes/                 # CSS theme files
│   │   ├── light.css
│   │   └── dark.css
│   └── icons/                  # UI icons and assets
├── tests/
│   └── __init__.py
├── README.md
├── DESIGN.md                   # This document
└── pyproject.toml              # Project dependencies (uv)
```

## Component Architecture

### 1. Core UI Components

#### MainWindow (`ui/main_window.py`)
- Main application window container
- Coordinates all UI components
- Manages window state (size, position)
- Handles application lifecycle

**Responsibilities**:
- Initialize all UI components
- Connect signals/slots between components
- Manage window state persistence
- Handle drag & drop file opening

#### MenuBar (`ui/menu_bar.py`)
- Application menu system
- Menu actions and keyboard shortcuts

**Menus**:
- **File**: Open, Recent Files, Exit
- **View**: Font Size (+/-), Zoom (+/-), Theme Toggle, Fullscreen, Show/Hide TOC
- **Navigate**: Jump to Heading, Find in Document
- **Help**: About, Keyboard Shortcuts

**Keyboard Shortcuts**:
- `Ctrl+O`: Open file
- `Ctrl+F`: Find in document
- `Ctrl++`: Increase font size
- `Ctrl+-`: Decrease font size
- `F11`: Toggle fullscreen

#### ViewerWidget (`ui/viewer_widget.py`)
- Main markdown display area
- HTML rendering with QWebEngineView
- Link handling (internal anchors, external URLs)
- Image display (local and remote)

**Responsibilities**:
- Render HTML content from markdown
- Handle link clicks (external → browser, internal → scroll)
- Apply theme CSS
- Manage zoom and font size
- Track scroll position

#### TOCWidget (`ui/toc_widget.py`)
- Table of contents sidebar
- Hierarchical tree view of document headers
- Clickable navigation

**Responsibilities**:
- Display document structure
- Navigate to sections on click
- Highlight current section
- Collapsible/expandable tree

#### Toolbar (`ui/toolbar.py`)
- Quick access buttons for common actions

**Buttons**:
- Open file
- Increase/decrease font size
- Theme toggle
- TOC visibility toggle

### 2. Core Logic Modules

#### MarkdownRenderer (`core/markdown_renderer.py`)
- Converts markdown to HTML
- Pluggable backend architecture
- Extension support

**Features**:
- Multiple backend support (markdown2, mistune, markdown-it-py)
- GFM (GitHub Flavored Markdown) support
- Syntax highlighting for code blocks
- Table support
- Emoji rendering
- HTML sanitization

**Interface**:
```python
class MarkdownRenderer:
    def render(self, markdown_text: str) -> str:
        """Convert markdown to HTML"""

    def set_backend(self, backend: str):
        """Switch markdown processing backend"""

    def enable_extension(self, extension: str):
        """Enable markdown extension"""
```

#### DocumentManager (`core/document_manager.py`)
- File operations and management
- Recent files tracking
- File change detection

**Responsibilities**:
- Open/read markdown files
- Encoding detection
- File watching for external changes
- Recent files list management
- Error handling for invalid files

**Interface**:
```python
class DocumentManager:
    def open_file(self, file_path: str) -> str:
        """Open and read markdown file"""

    def get_recent_files(self) -> list[str]:
        """Get list of recently opened files"""

    def add_recent_file(self, file_path: str):
        """Add file to recent files list"""
```

#### TOCGenerator (`core/toc_generator.py`)
- Parse markdown headers
- Build hierarchical structure
- Generate navigation anchors

**Responsibilities**:
- Extract headers from markdown
- Build tree structure (H1, H2, H3, etc.)
- Generate unique anchor IDs
- Provide navigation data structure

**Interface**:
```python
class TOCGenerator:
    def generate_toc(self, markdown_text: str) -> list[dict]:
        """Extract headers and build TOC structure"""

    def inject_anchors(self, html: str) -> str:
        """Add anchor IDs to headers in HTML"""
```

### 3. Configuration Modules

#### SettingsManager (`config/settings_manager.py`)
- Persistent application settings
- User preferences management
- Window state tracking

**Stored Settings**:
- Recent files list (paths and metadata)
- Last opened file
- Window size and position
- Theme preference (light/dark)
- Font size
- Zoom level
- TOC visibility
- Scroll positions per file

**Interface**:
```python
class SettingsManager:
    def load_settings(self) -> dict:
        """Load settings from disk"""

    def save_settings(self, settings: dict):
        """Save settings to disk"""

    def get(self, key: str, default=None):
        """Get setting value"""

    def set(self, key: str, value):
        """Set setting value"""
```

#### ThemeManager (`config/theme_manager.py`)
- Theme loading and management
- CSS template system
- Syntax highlighting themes

**Responsibilities**:
- Load CSS theme files
- Apply themes to rendered HTML
- Manage syntax highlighting color schemes
- Support custom themes

**Built-in Themes**:
- Light mode (default)
- Dark mode
- Sepia (future)
- High contrast (future)

**Interface**:
```python
class ThemeManager:
    def load_theme(self, theme_name: str) -> str:
        """Load CSS for specified theme"""

    def get_available_themes(self) -> list[str]:
        """List available themes"""

    def get_syntax_theme(self, theme_name: str) -> str:
        """Get Pygments theme for code highlighting"""
```

## Feature Specifications

### 1. Document Management

#### Opening Files
- Standard file picker dialog (filter: .md, .markdown, .txt)
- Drag & drop support
- Recent files quick access (menu + keyboard shortcut)
- Command-line argument support: `python main.py file.md`

#### Recent Files
- Track last 15 opened files
- Display in File menu with keyboard shortcuts (Alt+1 through Alt+9)
- Store full path and last access time
- Remove non-existent files from list

### 2. Display & Rendering

#### Markdown Rendering
- Full GFM support
- Tables with alignment
- Fenced code blocks with syntax highlighting
- Task lists (checkboxes)
- Strikethrough, superscript, subscript
- Emoji support (:emoji: syntax)
- Automatic URL linking

#### Code Highlighting
- Pygments-based syntax highlighting
- Support for 100+ languages
- Theme-aware color schemes
- Line numbers (optional)

#### Image Handling
- Local image display (relative and absolute paths)
- Remote image loading (HTTP/HTTPS)
- Alt text display on hover
- Responsive sizing

### 3. Navigation

#### Table of Contents
- Auto-generated from headers (H1-H6)
- Hierarchical tree structure
- Clickable navigation
- Current section highlighting
- Collapsible sections
- Keyboard navigation

#### Search
- Find in document (Ctrl+F)
- Case-sensitive/insensitive toggle
- Highlight all matches
- Next/previous navigation
- Match count display

#### Internal Links
- Support for `[text](#anchor)` links
- Smooth scrolling to target
- Back/forward navigation (future)

### 4. Customization

#### Font Size
- Adjustable via menu and keyboard shortcuts
- Range: 8pt to 32pt
- Persists across sessions
- Affects text only (not images)

#### Zoom
- Page zoom (affects everything including images)
- Range: 25% to 400%
- Keyboard shortcuts: Ctrl+0 (reset), Ctrl++, Ctrl+-

#### Themes
- Light/Dark mode toggle
- System theme detection (future)
- Custom CSS support (future)

### 5. User Experience

#### Reading Mode
- Fullscreen/distraction-free mode (F11)
- Hide menu bar and toolbar
- Show TOC on demand
- Exit with Esc or F11

#### Window State
- Remember window size and position
- Remember TOC visibility
- Remember scroll position per file
- Restore last opened file on startup

#### Status Bar
- Current file path
- Word count
- Character count
- Reading time estimate (based on 200 wpm)
- Cursor position indicator (future)

### 6. Link Handling

#### External Links
- Open in default system browser
- Confirm before opening (optional security setting)
- Support for http://, https://, mailto:, file:// protocols

#### Internal Links
- Navigate to anchors within document
- Smooth scroll to target
- Update TOC selection

## Implementation Phases

### Phase 1: MVP (Minimum Viable Product)
**Goal**: Basic functional markdown reader

**Components**:
- MainWindow with basic layout
- MenuBar with File > Open and Exit
- ViewerWidget with markdown rendering
- Basic MarkdownRenderer (single backend)
- DocumentManager for file opening
- Simple SettingsManager (recent files only)

**Features**:
- Open markdown files
- Render basic markdown (headers, paragraphs, lists, code blocks)
- Recent files list (last 5)
- Basic window state persistence

### Phase 2: Enhanced Display
**Goal**: Improved rendering and styling

**Components**:
- ThemeManager with light/dark themes
- Enhanced MarkdownRenderer with extensions
- Code syntax highlighting

**Features**:
- Full GFM support
- Theme toggle (light/dark)
- Syntax highlighting for code blocks
- Image display (local and remote)
- Font size adjustment
- Zoom control

### Phase 3: Navigation & Search
**Goal**: Easy document navigation

**Components**:
- TOCWidget with tree view
- TOCGenerator for header extraction
- Search dialog

**Features**:
- Table of contents sidebar
- Clickable TOC navigation
- Find in document
- Internal link handling
- Smooth scrolling

### Phase 4: User Experience
**Goal**: Polish and refinement

**Features**:
- Reading mode (fullscreen)
- Status bar with statistics
- Keyboard shortcuts
- Drag & drop file opening
- Improved settings persistence
- Scroll position memory
- Toolbar for quick access

### Phase 5: Advanced Features (Future)
**Goal**: Extended functionality

**Features**:
- Export to HTML/PDF
- Print preview
- Custom themes
- Bookmarks/favorites
- Split view (multiple documents)
- Math rendering (LaTeX/MathJax)
- Mermaid diagram support
- Document outline export
- Presentation mode

## Dependencies

### Required
- PyQt6 or PySide6 (GUI framework)
- PyQt6-WebEngine (HTML rendering)
- markdown2 or mistune (markdown processing)
- Pygments (syntax highlighting)

### Optional
- watchdog (file change detection)
- python-magic (file type detection)

### Development
- pytest (testing)
- black (code formatting)
- mypy (type checking)

## Configuration File Format

### settings.json
```json
{
  "window": {
    "width": 1200,
    "height": 800,
    "x": 100,
    "y": 100,
    "maximized": false
  },
  "ui": {
    "theme": "light",
    "font_size": 14,
    "zoom_level": 100,
    "toc_visible": true,
    "toc_width": 250
  },
  "recent_files": [
    {
      "path": "/path/to/document.md",
      "last_opened": "2025-10-09T10:30:00",
      "scroll_position": 450
    }
  ],
  "preferences": {
    "restore_last_file": true,
    "confirm_external_links": false,
    "auto_reload_changed_files": true
  }
}
```

## Testing Strategy

### Unit Tests
- MarkdownRenderer: Test various markdown inputs
- TOCGenerator: Test header extraction
- SettingsManager: Test load/save operations
- DocumentManager: Test file operations

### Integration Tests
- Full rendering pipeline (MD → HTML → Display)
- Theme switching
- Recent files management
- Window state persistence

### Manual Testing
- UI responsiveness
- Theme appearance
- Link handling
- File opening/drag-drop
- Keyboard shortcuts

## Performance Considerations

- Lazy loading for large documents
- Efficient HTML rendering (QWebEngineView caching)
- Debounced file watching
- Optimized TOC generation
- Thread-safe file operations

## Security Considerations

- HTML sanitization (prevent XSS in markdown)
- Safe external link handling
- File path validation
- Resource loading restrictions (remote images)

## Future Enhancement Ideas

### Export & Sharing
- Export to HTML (standalone with embedded CSS)
- Export to PDF
- Print with custom styling
- Copy as formatted HTML

### Advanced Features
- Markdown editing mode (split view)
- Live preview while editing
- Version control integration (git status display)
- Document comparison/diff view
- Collaborative features (comments, annotations)

### Customization
- Custom CSS injection
- Plugin system for extensions
- Custom keyboard shortcuts
- Configurable toolbar
- Multiple theme options

### Organization
- Document collections/projects
- Tags and categories
- Full-text search across files
- Bookmarks within documents
- Reading history and analytics

### Accessibility
- Screen reader support
- High contrast themes
- Keyboard-only navigation
- Adjustable line spacing
- Dyslexia-friendly fonts

## Success Criteria

### Core Functionality
- ✅ Open and render markdown files correctly
- ✅ Display images, tables, and code blocks
- ✅ Navigate via table of contents
- ✅ Remember user preferences

### User Experience
- ✅ Fast startup time (< 1 second)
- ✅ Smooth scrolling and navigation
- ✅ Intuitive interface
- ✅ Responsive to user input

### Code Quality
- ✅ Modular architecture
- ✅ Well-documented code
- ✅ Comprehensive test coverage
- ✅ Type hints throughout

### Extensibility
- ✅ Easy to add new themes
- ✅ Pluggable markdown backends
- ✅ Extensible menu system
- ✅ Clear component boundaries

---

## Getting Started

1. Set up Python environment with `uv`
2. Install dependencies: `uv add PyQt6 PyQt6-WebEngine markdown2 Pygments`
3. Create project structure as outlined above
4. Implement Phase 1 (MVP) components
5. Test and iterate

## Notes

- Use uv for dependency management: `uv run python main.py`
- Follow modular design principles for easy enhancement
- Commit frequently to git repository
- Focus on clean, readable code with type hints
- Document all public APIs
- Test incrementally as features are added
