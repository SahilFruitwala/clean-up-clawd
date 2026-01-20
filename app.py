"""
Directory Cleaner TUI Application

A terminal-based application for cleaning up directories by removing
specific folders (like node_modules, __pycache__) and files by extension.
"""

from pathlib import Path
import shutil

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    DataTable,
    DirectoryTree,
    Footer,
    Header,
    Input,
    Label,
    Static,
    ProgressBar,
    Markdown,
)
from textual.containers import Grid
from textual.worker import Worker, get_current_worker

from scanner import Scanner, ScanResult, format_size


class HelpModal(ModalScreen[None]):
    """Help screen showing how to use the app."""

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("enter", "close", "Close"),
    ]

    HELP_TEXT = """
# 📖 user Guide

## 1. Add Folders
Type a path in the top input and press **Enter**, or browse and click folders in the tree view on the left.

## 2. Configure Patterns
Edit the **Folder Patterns** and **File Patterns** inputs to specify what you want to clean.  
*Defaults include `node_modules`, `__pycache__`, etc.*

## 3. Scan
Click the **SCAN** button (or press `s`). The app will search the added folders for matches.

## 4. Review & Delete
Review the results. Uncheck items you want to keep.  
Click **DELETE SELECTED** (or press `d`) to remove them.

---
**Shortcuts:** `s` Scan | `d` Delete | `a` Select All | `n` Deselect All | `q` Quit
"""

    def compose(self) -> ComposeResult:
        with Container(id="help-dialog"):
            yield Markdown(self.HELP_TEXT)
            yield Button("Got it!", variant="primary", id="help-close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(None)

    def action_close(self) -> None:
        self.dismiss(None)


class ConfirmModal(ModalScreen[bool]):
    """Modal screen for confirming deletion."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "confirm", "Confirm"),
    ]

    def __init__(self, items: list[ScanResult]) -> None:
        super().__init__()
        self.items = items
        self.total_size = sum(item.size for item in items)
        self.folder_count = sum(1 for item in items if item.item_type == "folder")
        self.file_count = sum(1 for item in items if item.item_type == "file")

    def compose(self) -> ComposeResult:
        with Container(id="confirm-dialog"):
            yield Label("⚠️ PERMANENTLY DELETE?", id="confirm-title")
            
            with Container(id="confirm-stats"):
                with Horizontal(classes="stat-row"):
                    yield Label(f"Folders: {self.folder_count}", classes="stat-item")
                    yield Label(f"Files: {self.file_count}", classes="stat-item")
                yield Label(f"Total Size: {format_size(self.total_size)}", id="stat-total")

            yield Label("These actions cannot be undone.", id="confirm-warning")
            
            with Horizontal(id="confirm-buttons"):
                yield Button("Cancel", variant="default", id="confirm-cancel")
                yield Button("DELETE EVERYTHING", variant="error", id="confirm-delete")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "confirm-delete")

    def action_cancel(self) -> None:
        self.dismiss(False)

    def action_confirm(self) -> None:
        self.dismiss(True)


class DirectoryCleanerApp(App):
    """Main application for directory cleanup."""

    CSS_PATH = "styles.tcss"
    TITLE = "🗑️ Directory Cleaner"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("s", "scan", "Scan"),
        Binding("d", "delete", "Delete"),
        Binding("a", "select_all", "Select All"),
        Binding("n", "deselect_all", "Deselect"),
        Binding("escape", "cancel_scan", "Cancel"),
        Binding("f1", "show_help", "Help"),
        Binding("?", "show_help", "Help"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.scanner = Scanner()
        self.scan_results: list[ScanResult] = []
        self.selected_indices: set[int] = set()
        self.scan_directories: list[Path] = []
        self._scan_worker: Worker | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        
        with Vertical(id="main-container"):
            # Top bar - folder input
            with Horizontal(id="top-bar"):
                yield Label("📁 Folder:", id="folder-label")
                yield Input(
                    value=str(Path.home()),
                    placeholder="Enter folder path...",
                    id="path-input"
                )
                yield Button("➕ Add", id="add-button", variant="primary")
                yield Button("🏠", id="home-button", variant="default")
                yield Button("❓", id="help-button", variant="default")
            
            # Main content
            with Horizontal(id="content-area"):
                # Left panel - directories and patterns
                with Vertical(id="left-panel"):
                    yield Label("📋 Folders to scan:", classes="section-title")
                    yield DataTable(id="dir-list", cursor_type="row")
                    with Horizontal(id="dir-buttons"):
                        yield Button("Remove", id="remove-dir-button")
                        yield Button("Clear", id="clear-dirs-button")
                    
                    yield Label("🔍 Find these folders:", classes="section-title")
                    yield Input(
                        value="node_modules, __pycache__, .venv, dist, build",
                        id="folder-patterns"
                    )
                    
                    yield Label("🔍 Find these files:", classes="section-title")
                    yield Input(
                        value=".pyc, .pyo, .DS_Store, .log",
                        id="file-patterns"
                    )
                    
                    yield Static("", classes="spacer")
                    
                    yield Label("📂 Browse:", classes="section-title")
                    with VerticalScroll(id="tree-container"):
                        yield DirectoryTree(str(Path.home()), id="directory-tree")
                
                # Right panel - results
                with Vertical(id="right-panel"):
                    with Horizontal(id="scan-bar"):
                        yield Button("🔍 SCAN", id="scan-button", variant="success")
                        yield Button("Cancel", id="cancel-button", variant="warning", disabled=True)
                        yield Static("", id="status-text")
                    
                    yield ProgressBar(id="progress-bar", show_eta=False)
                    
                    yield Label("📋 RESULTS - Click rows to unselect items you want to KEEP:", id="results-label")
                    yield DataTable(id="results-table", zebra_stripes=True, cursor_type="row")
                    
                    with Horizontal(id="results-bar"):
                        yield Button("☑ Select All", id="select-all-button")
                        yield Button("☐ Deselect All", id="deselect-all-button")
                        yield Static("", classes="spacer-h")
                        yield Button("🗑️ DELETE SELECTED", id="delete-button", variant="error")
        
        yield Footer()

    def on_mount(self) -> None:
        """Set up the application on mount."""
        # Results table
        table = self.query_one("#results-table", DataTable)
        table.add_columns("SEL", "TYPE", "PATH", "SIZE")
        
        # Directory list
        dir_table = self.query_one("#dir-list", DataTable)
        dir_table.add_columns("Folder Path")
        
        # Hide progress bar
        self.query_one("#progress-bar", ProgressBar).display = False
        
        # Initial status
        self.update_status("Add folders and click SCAN")
        
        # Focus path input
        self.query_one("#path-input", Input).focus()

    def update_status(self, text: str) -> None:
        """Update the status text."""
        self.query_one("#status-text", Static).update(text)

    def action_show_help(self) -> None:
        """Show help modal."""
        self.push_screen(HelpModal())

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in path input."""
        if event.input.id == "path-input":
            self.add_directory()

    def add_directory(self) -> None:
        """Add directory to the scan list."""
        path_input = self.query_one("#path-input", Input)
        path_str = path_input.value.strip()
        
        if not path_str:
            self.notify("Enter a folder path", severity="warning")
            return
        
        path = Path(path_str).expanduser().resolve()
        
        if not path.exists():
            self.notify(f"Not found: {path}", severity="error")
            return
        
        if not path.is_dir():
            self.notify(f"Not a folder: {path}", severity="error")
            return
        
        if path in self.scan_directories:
            self.notify(f"Already added", severity="warning")
            return
        
        self.scan_directories.append(path)
        
        dir_table = self.query_one("#dir-list", DataTable)
        dir_table.add_row(str(path), key=str(len(self.scan_directories) - 1))
        
        path_input.value = ""
        self.notify(f"Added: {path.name}")
        self.update_status(f"{len(self.scan_directories)} folder(s) ready - Click SCAN")

    def on_directory_tree_directory_selected(
        self, event: DirectoryTree.DirectorySelected
    ) -> None:
        """Handle directory selection in the tree."""
        path = event.path
        if path not in self.scan_directories:
            self.scan_directories.append(path)
            dir_table = self.query_one("#dir-list", DataTable)
            dir_table.add_row(str(path), key=str(len(self.scan_directories) - 1))
            self.notify(f"Added: {path.name}")
            self.update_status(f"{len(self.scan_directories)} folder(s) ready - Click SCAN")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        bid = event.button.id
        
        if bid == "add-button":
            self.add_directory()
        elif bid == "home-button":
            self.query_one("#path-input", Input).value = str(Path.home())
        elif bid == "help-button":
            self.action_show_help()
        elif bid == "remove-dir-button":
            self.remove_selected_directory()
        elif bid == "clear-dirs-button":
            self.clear_directory_list()
        elif bid == "scan-button":
            self.action_scan()
        elif bid == "cancel-button":
            self.action_cancel_scan()
        elif bid == "select-all-button":
            self.action_select_all()
        elif bid == "deselect-all-button":
            self.action_deselect_all()
        elif bid == "delete-button":
            self.action_delete()

    def remove_selected_directory(self) -> None:
        """Remove the selected directory from the list."""
        dir_table = self.query_one("#dir-list", DataTable)
        if dir_table.cursor_row is not None and dir_table.cursor_row < len(self.scan_directories):
            self.scan_directories.pop(dir_table.cursor_row)
            dir_table.clear()
            for idx, path in enumerate(self.scan_directories):
                dir_table.add_row(str(path), key=str(idx))
            self.update_status(f"{len(self.scan_directories)} folder(s) ready")

    def clear_directory_list(self) -> None:
        """Clear all directories from the scan list."""
        self.scan_directories = []
        self.query_one("#dir-list", DataTable).clear()
        self.update_status("Add folders and click SCAN")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Toggle selection when a row is clicked."""
        if event.data_table.id == "results-table" and event.row_key is not None:
            try:
                row_index = int(str(event.row_key.value))
                self.toggle_selection(row_index)
            except (ValueError, TypeError):
                pass

    def toggle_selection(self, index: int) -> None:
        """Toggle the selection state of a row."""
        if index in self.selected_indices:
            self.selected_indices.remove(index)
        else:
            self.selected_indices.add(index)
        self.update_table_display()

    def update_table_display(self) -> None:
        """Update the table to show selection state."""
        table = self.query_one("#results-table", DataTable)
        for idx in range(len(self.scan_results)):
            marker = "✓ DEL" if idx in self.selected_indices else "  keep"
            try:
                table.update_cell_at((idx, 0), marker)
            except:
                pass
        
        # Update status
        selected = len(self.selected_indices)
        total = len(self.scan_results)
        if selected > 0:
            size = sum(self.scan_results[i].size for i in self.selected_indices)
            self.update_status(f"{selected}/{total} selected ({format_size(size)}) - Click DELETE")
        else:
            self.update_status(f"{total} items found - Click rows to select")

    def action_scan(self) -> None:
        """Start scanning."""
        if not self.scan_directories:
            self.notify("Add folders first!", severity="warning")
            return
        
        folder_patterns = Scanner.parse_patterns(
            self.query_one("#folder-patterns", Input).value
        )
        file_patterns = Scanner.parse_patterns(
            self.query_one("#file-patterns", Input).value
        )
        
        if not folder_patterns and not file_patterns:
            self.notify("Enter patterns to find", severity="warning")
            return
        
        # Clear results
        self.query_one("#results-table", DataTable).clear()
        self.scan_results = []
        self.selected_indices = set()
        
        # Show progress
        progress = self.query_one("#progress-bar", ProgressBar)
        progress.display = True
        progress.update(total=len(self.scan_directories), progress=0)
        
        self.update_status("Scanning...")
        self.query_one("#scan-button", Button).disabled = True
        self.query_one("#cancel-button", Button).disabled = False
        
        self._scan_worker = self.run_worker(
            self.perform_scan(folder_patterns, file_patterns),
            name="scanner",
            exclusive=True,
        )

    async def perform_scan(
        self, folder_patterns: list[str], file_patterns: list[str]
    ) -> None:
        """Perform the scan."""
        worker = get_current_worker()
        table = self.query_one("#results-table", DataTable)
        progress = self.query_one("#progress-bar", ProgressBar)
        count = 0
        
        try:
            for dir_idx, scan_dir in enumerate(self.scan_directories):
                if worker.is_cancelled:
                    break
                
                progress.update(progress=dir_idx + 1)
                self.update_status(f"Scanning {scan_dir.name}... ({count} found)")
                
                for result in self.scanner.scan_directory(
                    scan_dir, folder_patterns, file_patterns, include_sizes=True
                ):
                    if worker.is_cancelled:
                        break
                    
                    self.scan_results.append(result)
                    idx = len(self.scan_results) - 1
                    
                    # Auto-select all items
                    self.selected_indices.add(idx)
                    
                    type_str = "📁 FOLDER" if result.item_type == "folder" else "📄 file"
                    
                    # Show readable path
                    path_str = str(result.path)
                    if len(path_str) > 50:
                        path_str = "..." + path_str[-47:]
                    
                    table.add_row(
                        "✓ DEL",  # Selected by default
                        type_str,
                        path_str,
                        format_size(result.size),
                        key=str(idx),
                    )
                    
                    count += 1
                    
                    if count % 5 == 0:
                        self.update_status(f"Scanning {scan_dir.name}... ({count} found)")
                    
        except Exception as e:
            self.notify(f"Error: {e}", severity="error")
        finally:
            self.query_one("#progress-bar", ProgressBar).display = False
            self.query_one("#scan-button", Button).disabled = False
            self.query_one("#cancel-button", Button).disabled = True
            
            if not worker.is_cancelled:
                total = len(self.scan_results)
                if total > 0:
                    size = sum(r.size for r in self.scan_results)
                    self.update_status(f"ALL {total} items selected ({format_size(size)}) - Click DELETE or unselect items to keep")
                    self.notify(f"Found {total} items - All selected for deletion")
                else:
                    self.update_status("No matching items found")
                    self.notify("No items found matching your patterns")

    def action_cancel_scan(self) -> None:
        """Cancel the current scan."""
        if self._scan_worker and self._scan_worker.is_running:
            self._scan_worker.cancel()
            self.scanner.cancel()
            self.notify("Cancelled")

    def action_select_all(self) -> None:
        """Select all items."""
        if not self.scan_results:
            return
        self.selected_indices = set(range(len(self.scan_results)))
        self.update_table_display()
        self.notify("All items selected")

    def action_deselect_all(self) -> None:
        """Deselect all items."""
        self.selected_indices = set()
        self.update_table_display()
        self.notify("All items deselected")

    def action_delete(self) -> None:
        """Delete selected items."""
        if not self.selected_indices:
            self.notify("Nothing selected!", severity="warning")
            return
        
        items = [self.scan_results[i] for i in sorted(self.selected_indices)]
        self.push_screen(ConfirmModal(items), self.handle_delete)

    def handle_delete(self, confirmed: bool) -> None:
        """Handle delete confirmation."""
        if not confirmed:
            self.notify("Cancelled")
            return
        
        count = len(self.selected_indices)
        progress = self.query_one("#progress-bar", ProgressBar)
        progress.display = True
        progress.update(total=count, progress=0)
        
        self.run_worker(self.perform_deletion(), name="deleter", exclusive=True)

    async def perform_deletion(self) -> None:
        """Perform deletion."""
        worker = get_current_worker()
        deleted = 0
        errors = 0
        
        items = [self.scan_results[i] for i in sorted(self.selected_indices, reverse=True)]
        total = len(items)
        progress = self.query_one("#progress-bar", ProgressBar)
        
        for idx, item in enumerate(items):
            if worker.is_cancelled:
                break
            
            progress.update(progress=idx + 1)
            self.update_status(f"Deleting {idx + 1}/{total}: {item.path.name}")
            
            try:
                if item.path.exists():
                    if item.item_type == "folder":
                        shutil.rmtree(item.path)
                    else:
                        item.path.unlink()
                    deleted += 1
            except Exception as e:
                errors += 1
        
        # Clear
        progress.display = False
        self.query_one("#results-table", DataTable).clear()
        self.scan_results = []
        self.selected_indices = set()
        
        self.update_status(f"Deleted {deleted} items" + (f" ({errors} errors)" if errors else ""))
        self.notify(f"✓ Deleted {deleted} items!" if errors == 0 else f"Deleted {deleted} items with {errors} errors")


def main():
    """Entry point for the application."""
    app = DirectoryCleanerApp()
    app.run()


if __name__ == "__main__":
    main()
