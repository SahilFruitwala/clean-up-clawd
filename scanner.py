"""
Scanner module for directory cleanup operations.
Provides functionality to scan directories and match files/folders by patterns.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator
import fnmatch
import os


@dataclass
class ScanResult:
    """Represents a matched item found during scanning."""
    path: Path
    item_type: str  # "folder" or "file"
    size: int  # Size in bytes
    matched_pattern: str  # The pattern that matched


class Scanner:
    """Handles directory scanning and pattern matching."""

    def __init__(self):
        self.results: list[ScanResult] = []
        self._scanning = False
        self._cancelled = False

    def cancel(self) -> None:
        """Cancel the current scan operation."""
        self._cancelled = True

    @staticmethod
    def parse_patterns(pattern_string: str) -> list[str]:
        """Parse comma-separated patterns into a list."""
        if not pattern_string.strip():
            return []
        return [p.strip() for p in pattern_string.split(",") if p.strip()]

    @staticmethod
    def get_size(path: Path) -> int:
        """Get the size of a file or directory in bytes."""
        if path.is_file():
            try:
                return path.stat().st_size
            except (OSError, PermissionError):
                return 0
        
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    try:
                        fp = Path(dirpath) / filename
                        total_size += fp.stat().st_size
                    except (OSError, PermissionError):
                        pass
        except (OSError, PermissionError):
            pass
        return total_size

    def match_folder(self, name: str, patterns: list[str]) -> str | None:
        """Check if folder name matches any pattern. Returns matched pattern or None."""
        for pattern in patterns:
            # Support exact match and glob patterns
            if fnmatch.fnmatch(name, pattern) or name == pattern:
                return pattern
        return None

    def match_file(self, name: str, extensions: list[str]) -> str | None:
        """Check if file matches any extension pattern. Returns matched pattern or None."""
        for ext in extensions:
            # Normalize extension (add dot if missing)
            ext_normalized = ext if ext.startswith(".") else f".{ext}"
            if name.endswith(ext_normalized) or name == ext.lstrip("."):
                return ext
        return None

    def scan_directory(
        self,
        root_path: Path,
        folder_patterns: list[str],
        extension_patterns: list[str],
        include_sizes: bool = True
    ) -> Iterator[ScanResult]:
        """
        Recursively scan a directory for matching folders and files.
        
        Args:
            root_path: The root directory to scan
            folder_patterns: List of folder name patterns to match
            extension_patterns: List of file extension patterns to match
            include_sizes: Whether to calculate sizes (can be slow for large dirs)
            
        Yields:
            ScanResult objects for each matched item
        """
        self._scanning = True
        self._cancelled = False
        self.results = []

        try:
            for dirpath, dirnames, filenames in os.walk(root_path):
                if self._cancelled:
                    break

                current_dir = Path(dirpath)
                
                # Check folder names - if matched, don't descend into them
                dirs_to_remove = []
                for dirname in dirnames:
                    if self._cancelled:
                        break
                        
                    matched_pattern = self.match_folder(dirname, folder_patterns)
                    if matched_pattern:
                        full_path = current_dir / dirname
                        size = self.get_size(full_path) if include_sizes else 0
                        result = ScanResult(
                            path=full_path,
                            item_type="folder",
                            size=size,
                            matched_pattern=matched_pattern
                        )
                        self.results.append(result)
                        yield result
                        # Don't descend into matched folders
                        dirs_to_remove.append(dirname)
                
                # Remove matched folders from traversal
                for dirname in dirs_to_remove:
                    dirnames.remove(dirname)
                
                # Check file names
                for filename in filenames:
                    if self._cancelled:
                        break
                        
                    matched_pattern = self.match_file(filename, extension_patterns)
                    if matched_pattern:
                        full_path = current_dir / filename
                        try:
                            size = full_path.stat().st_size if include_sizes else 0
                        except (OSError, PermissionError):
                            size = 0
                        result = ScanResult(
                            path=full_path,
                            item_type="file",
                            size=size,
                            matched_pattern=matched_pattern
                        )
                        self.results.append(result)
                        yield result

        except (OSError, PermissionError) as e:
            # Log or handle permission errors gracefully
            pass
        finally:
            self._scanning = False

    @property
    def is_scanning(self) -> bool:
        """Check if a scan is currently in progress."""
        return self._scanning


def format_size(size_bytes: int) -> str:
    """Format bytes into human-readable size string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
