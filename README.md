# 🗑️ Directory Cleaner TUI

A beautiful terminal-based application for cleaning up your filesystem by removing specific folders (like `node_modules`, `__pycache__`) and files with specific extensions (like `.pyc`, `.DS_Store`).

Built with [Textual](https://textual.textualize.io/) for a modern, responsive TUI experience.

## ✨ Features

- **🌲 Directory Browser**: Navigate your filesystem with an interactive tree view
- **🔍 Pattern Matching**: Scan for folders by name and files by extension
- **📊 Results Table**: View all matches with size information
- **☑️ Selective Deletion**: Choose exactly what to delete
- **🔒 Safe Deletion**: Confirmation modal before any destructive action
- **⌨️ Keyboard Shortcuts**: Fast navigation without leaving the keyboard
- **🎨 Modern UI**: Dark theme with beautiful styling

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Quick Start

```bash
# Clone or navigate to the project directory
cd clean-up-clawd

# Install dependencies and run
uv run python app.py
```

### Development Setup

```bash
# Initialize the project (if not already done)
uv init

# Add dependencies
uv add textual

# Run the application
uv run python app.py
```

## 🚀 Usage

### Launching the App

```bash
uv run python app.py
```

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `s` | Scan the selected directory |
| `d` | Delete selected items |
| `a` | Select all items |
| `n` | Deselect all items |
| `r` | Refresh directory tree |
| `q` | Quit the application |
| `?` | Show help |

### Workflow

1. **Navigate**: Use the directory tree on the left to select a directory to scan
2. **Configure**: Enter folder patterns and/or file extensions to match
3. **Scan**: Press `s` or click "Scan Directory" to find matching items
4. **Review**: Browse the results table showing all matched items with sizes
5. **Select**: Click rows or use "Select All" to choose items for deletion
6. **Delete**: Press `d` or click "Delete Selected" - confirm in the modal

## 📁 Common Patterns

### Folder Patterns

| Pattern | Description |
|---------|-------------|
| `node_modules` | Node.js dependencies |
| `__pycache__` | Python bytecode cache |
| `.git` | Git repository data |
| `.venv`, `venv` | Python virtual environments |
| `dist`, `build` | Build output directories |
| `.next` | Next.js build cache |
| `target` | Rust/Java build output |
| `.cache` | Various cache directories |

### File Extensions

| Pattern | Description |
|---------|-------------|
| `.pyc`, `.pyo` | Python compiled files |
| `.DS_Store` | macOS folder metadata |
| `.log` | Log files |
| `.tmp`, `.temp` | Temporary files |
| `.bak` | Backup files |
| `.swp` | Vim swap files |

## ⚠️ Safety Features

- **Confirmation Required**: A modal dialog shows exactly what will be deleted before any action
- **Size Display**: See the total size of items to be deleted
- **Non-recursive for Matched Folders**: Once a folder matches, its contents are not scanned (prevents duplicate counting)
- **Error Handling**: Failed deletions are reported without stopping the process

## 🛠️ Project Structure

```
clean-up-clawd/
├── app.py          # Main Textual application
├── scanner.py      # Directory scanning and pattern matching
├── styles.tcss     # Textual CSS styles
├── pyproject.toml  # Project configuration
├── README.md       # This file
└── .venv/          # Virtual environment (created by uv)
```

## 🎨 Customization

### Themes

The application uses Textual's built-in theming system. You can modify `styles.tcss` to customize:

- Colors and backgrounds
- Layout and spacing
- Component styles
- Animations

### Default Patterns

Edit the default values in `app.py` in the `compose()` method to change the pre-filled patterns.

## 📝 License

MIT License - feel free to use and modify as needed.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.
