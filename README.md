<div align="center">

# 🦞 Clean Up Clawd

### The Elegant Directory Cleaner for your Terminal

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Textual](https://img.shields.io/badge/Built%20With-Textual-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)

<p align="center">
  <img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbm90Zm91bmQ/giphy.gif" alt="Clean Up Clawd Demo" width="600" />
  <br>
  <em>Navigate, Scan, and Sweep away the clutter with a modern TUI.</em>
</p>

</div>

---

## ✨ Overview

**Clean Up Clawd** is a powerful, terminal-based utility designed to reclaim disk space with style. Built on the [Textual](https://textual.textualize.io/) framework, it provides a beautiful, interactive interface to identify and remove development clutter like `node_modules`, `__pycache__`, and temporary files.

Say goodbye to manual cleanup scripts and hello to a visual, safe, and efficient cleaning experience.

## 🚀 Features

- **🌲 Interactive Navigation**: Browse your filesystem with a responsive tree view.
- **🔍 Smart Scanning**: Instantly find specific folder names (e.g., `node_modules`) or file extensions (e.g., `.DS_Store`).
- **🛡️ Safety First**: 
  - **Explicit Selection**: Nothing is deleted until you select it.
  - **Confirmation Dialog**: Detailed breakdown of files, folders, and size before deletion.
  - **Non-Recursive**: Prevents double-counting by stopping at the first match.
- **⌨️ Keyboard Centric**: Full keyboard support for power users (`s` to scan, `d` to delete).
- **🎨 Modern UI**: polished dark mode with clear visual feedback.

---

## 📦 Installation

### 🍺 via Homebrew (Recommended for macOS)

The easiest way to install and keep updated.

```bash
brew tap SahilFruitwala/tap
brew install clean-up-clawd
```

### 🐍 via UV / Pip

If you prefer installing as a Python tool:

```bash
# Using uv (Recommended)
uv tool install clean-up-clawd

# Or clone and run
git clone https://github.com/SahilFruitwala/clean-up-clawd.git
cd clean-up-clawd
uv run python app.py
```

---

## 🎮 How to Use

1.  **Launch**: Run `clean-up-clawd` in your terminal.
2.  **Add Folders**: 
    - Type a path in the top bar and hit `Enter`.
    - Or navigate the tree on the left and click a folder.
3.  **Configure Patterns**:
    - **Folders**: Files like `node_modules`, `dist`, `.venv`.
    - **Files**: Extensions like `.pyc`, `.log`, `.DS_Store`.
4.  **Scan**: Press `s` or click the **SCAN** button.
5.  **Review**:
    - The table shows all matches.
    - Click rows to **unselect** items you want to keep.
6.  **Clean**:
    - Press `d` to trigger the deletion.
    - Confirm the details in the popup modal.
    - Done! 🧹

### Keyboard Shortcuts

| Key | Action |
| :---: | :--- |
| `s` | **S**can directories |
| `d` | **D**elete selected |
| `a` | Select **A**ll |
| `n` | Select **N**one |
| `q` | **Q**uit |
| `?` | Show **Help** |

---

## 🛠️ Configuration

### Default Targets

By default, the app looks for:
*   **Folders**: `node_modules`, `__pycache__`, `.venv`, `dist`, `build`, `.next`, `target`, `.git`
*   **Files**: `.pyc`, `.pyo`, `.DS_Store`, `.log`, `.tmp`, `.swp`

You can change these freely in the UI before every scan.

---

## 🏗️ Development

Want to contribute? Run the app locally:

```bash
# Clone the repo
git clone https://github.com/SahilFruitwala/clean-up-clawd.git
cd clean-up-clawd

# Install dependencies and run
uv run python app.py
```

### Building for Release

To create a standalone macOS executable:

```bash
./homebrew/build_release.sh
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

<div align="center">
  <sub>Built with ❤️ by Sahil</sub>
</div>
